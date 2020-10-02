# -*- coding:utf8 -*-

import re
import os

def shell():
    #rules=regular("../rules1.txt") #{'left_symbol':{'right str'..}..}
    rules=regular("ruleT.txt")
    #print(rRules(rules))
    parse(rules)

def regular(inputF):
    rules={}
    srcRules=open(inputF, 'r').read().split('\n')
    #pass 1:去重，去除epsilon产生式
    for rulei in srcRules:
        tokenL=re.split('->',rulei)
        if len(tokenL)!=2: continue
        key=tokenL[0]
        value=tokenL[1]
        rightSymL=value.split(' ')
        while '-NONE-' in rightSymL:
            rightSymL.remove('-NONE-')
        if len(rightSymL)!=0:
            value=' '.join(rightSymL)
            addRuleD(rules,key,value)
        #print(tokenL)
    if '-NONE-' in rules:
        del rules['-NONE-']

    #print(rules)
    #pass 2 对和终结符一样的非终结符进行转义
    '''for keyi in list(rules.keys()).copy():
        right=rules[keyi]
        for righti in right.copy():
            if righti==keyi:
                newKey='NT'+keyi
                rules[newKey]=set()
                rules[newKey].add(righti)
                rules[keyi].remove(righti)
        if len(right)==0:
            del rules[keyi]
    print(rules)'''
    #取消pass2: pass3中，拆分产生式右部串，会得到这些需要转义的符号，但是无法得知它需要转义

    #pass 3 消除多叉产生式
    keys=list(rules.keys()).copy()
    for keyi in keys:
        rSet=rules[keyi]
        for rightTuple in rSet:#rightTuple : (rightStr,freq)
            rightStr=rightTuple[0]
            freq=rightTuple[1]
            rightSymL=rightStr.split(' ')
            if len(rightSymL)>2:
                rSet.remove(rightTuple)
                newSym='_'.join(rightSymL[1:])
                rSet.add((' '.join([rightSymL[0],newSym]),freq))
                newSymL=rightSymL[1:]
                while len(newSymL)>1:
                    nextNewSym='_'.join(newSymL[1:])
                    rules[newSym]=set()
                    rules[newSym].add((' '.join([newSymL[0],nextNewSym]),freq))
                    newSymL=newSymL[1:]
                    newSym=nextNewSym
            elif len(rightSymL)==0:
                rSet.remove(rightTuple)
            elif len(rightSymL)==1:#单产生式
                pass
        if len(rSet)==0: del rules[keyi]
    #print(rules)
    #pass 4 消除非终结符单生成式
	#取消pass4：单生成式总是产生终结符，在CYK中处理。
    '''
    for keyi in list(rules.keys()).copy():
        rSet=rules[keyi]
        reCheck=True
        while reCheck:
            reCheck=False
            rSetC=rSet.copy()
            for rightStr in rSetC:
                rightSymL=rightStr.split(' ')
                if len(rightSymL)==1 and rightStr!=keyi:
                    childRSet=rules.get(rightStr,set())
                    if len(childRSet)>0:
                        if len(childRSet)==1 and rightStr==childRSet.copy().pop():
                            pass #右边是终结符
                        else:
                            rSet.remove(rightStr)
                            rSet=rSet|childRSet
                            rules[keyi]=rSet
                            del rules[rightStr]
                            reCheck = True
                    else: #右边是终结符
                        pass

                elif len(rightSymL)==1 and rightStr==keyi:
                    if len(rSet)==1 :pass #右边是终结符
                    else: rSet.discard(rightStr)'''

    # pass 5 PCFG 归一化
    for keyi in list(rules.keys()):
        s=rules[keyi]
        count=0
        for ti in s:
            count+=ti[1]
        for ti in s.copy():
            s.add((ti[0],ti[1]/count))
            if ti[1]!=ti[1]/count:
                s.remove(ti)

    #print(rules)
    return rules

def parse(rules):
    #print(rules)
    for i in range(1,2):
        #fNum='{}{}{}{}'.format(i//1000%10,i//100%10,i//10%10,i%10)
        #inputF="../Data/treebank/raw/wsj_{}".format(fNum)
        inputF="textT.txt"
        #outputF="./parsed/wsj_{}.out".format(fNum)
        outputF = "./parsed/parsePCFG.out"
        os.makedirs('./parsed/',exist_ok=True)
        file=open(outputF, 'w')
        sentences=open(inputF,'r').read().split('\n')[1:]
        while '' in sentences:  sentences.remove('')
        for sentence in sentences:
            terminal=tokenize(sentence,rules)
            stateMatrix=parseSentence(terminal,rRules(rules))
            printTree(terminal,stateMatrix,rules,file)
            #print(sentence)

def tokenize(sentence,rules): # pass 1:词法分析,写成终结符序列.最大前向匹配
    sLen = len(sentence)
    terminal = []
    l = 0
    wordUnkown = ''
    flag = False
    symbolSet = symbols(rules)
    # print(symbolSet)
    while l < sLen:
        r = sLen
        while r > l:
            if sentence[l:r] in symbolSet:
                terminal.append(sentence[l:r])
                wordUnkown = wordUnkown.replace(' ', '')
                if len(wordUnkown) > 0:
                    print('tokenizer meet unrecognized word: $' + wordUnkown + '$')
                    print('before ' + sentence[l:r])
                    wordUnkown = ''
                    flag = True
                break
            r = r - 1
        if r == l:
            wordUnkown = wordUnkown + sentence[l:l + 1]
            l = l + 1
        else:
            l = r
    wordUnkown = wordUnkown.replace(' ', '')
    if len(wordUnkown) > 0:
        print('tokenizer meet unrecognized word: ' + wordUnkown)
        flag = True

    print('\nSentence (tokenlized):')
    print(terminal)
    print()

    if flag:
        print('drop sentence due to word segmentation failure:\n' + sentence)
        return []

    return terminal

def parseSentence(terminal,rrules):#CYK 返回状态矩阵
    #print(rrules)
    N=len(terminal)
    V=[([None]*N)for i in range(N)]
    for i in range(N):
        t=terminal[i]
        V[i][i]=rrules[t]
        recheck = True
        while recheck:
            recheck=False
            Vii=V[i][i].copy()
            for t in Vii:
                symbol=t[0]
                parent=rrules.get(symbol,set())
                #parent.discard(symbol)
                before=len(V[i][i])
                if len(parent)>0:
                    V[i][i]=V[i][i]|parent
                after=len(V[i][i])
                if after>before :recheck=True

    for length in range(2,N+1): # 2..N
        for left in range(N-length+1):
            V[left][left+length-1]=set()
            for k in range(left+1,left+length):
                #获取k分割两个串可归约的根的集合
                if left==k-1:
                    right1=V[left][left]
                else :
                    right1=set()
                    for tuplei in V[left][k-1]:
                        right1 = right1 | set(tuplei[0].split(' '))
                if k==left+length-1:
                    right2=V[k][k]
                else:
                    right2=set()
                    for tuplei in V[k][left+length-1]:
                        right2.add(tuplei)
                #根据两个集合的积找所有k分割下可归约的左符号集合
                if len(right1)>0 and len(right2)>0 :
                    leftSymbolSet=getLeft(rrules,right1,right2)
                else: leftSymbolSet=set()
                if len(leftSymbolSet)>0:
                    '''recheck = True
                    while recheck:
                        recheck = False
                        leftSymbolSetC = leftSymbolSet.copy()
                        for ti in leftSymbolSetC:
                            lsymbol=ti[0]
                            parent = rrules.get(lsymbol, set())
                            #parent.discard(lsymbol)
                            before = len(leftSymbolSet)
                            if len(parent) > 0:
                                leftSymbolSet = leftSymbolSet | parent
                            after = len(leftSymbolSet)
                            if after > before: recheck = True'''
                    a=1
                    for ti in leftSymbolSet:
                        leftSymbolSetStr=ti[0]
                        V[left][left + length-1].add((leftSymbolSetStr,k))
                        #print('regular: {} {} to {} {} by {} k={}'.format(\
                        #      left,terminal[left],left + length-1,terminal[left + length-1]\
                        #      ,leftSymbolSetStr,k))

    #print (V)
    print('CYK fin')
    return V

def printTree(terminal,stateMartix,rules,file):
    N=len(terminal)
    #print(stateMartix)
    tree=treeStr(terminal,stateMartix,rules,0,N-1,'S')
    file.write('{} Non-terminal symbols\n'.format(len(rules)))
    file.write('Sentence:{}\n'.format(' '.join(terminal)))
    if tree[1]==0:
        file.write("parse failed.\n")
        print("parse failed.")
    else:
        print("parse complete: result P={}".format(tree[1]))
        print(tree[0])
        file.write(tree[0])
        file.write('\nP={}\n'.format(tree[1]))
    file.write('\n')

def treeStr(terminal,V,rules,i,j,leftSymbol):
    if i==j:
        p=childP(rules,[leftSymbol],terminal[i])
        return tuple(['('+leftSymbol+' '+terminal[i]+')',p])
    else:
        ret=tuple()

        maxP = 0
        maxRT1 = ''
        maxRT2 = ''
        for tuplei in V[i][j]: #所有(leftSymbol,k)
            if tuplei[0]==leftSymbol:
                #leftSymbol->?
                k=tuplei[1]
                for ti in rules[leftSymbol]:#尝试用一个产生式匹配左右分段
                    rightStr=ti[0]
                    p=ti[1]
                    rightList=rightStr.split(' ')
                    if len(rightList)==2:
                        r1=rightList[0]
                        r2=rightList[1]
                        if contains(V[i][k-1],r1) and contains(V[k][j],r2):#use leftSymbol->r1 r2,k,p
                            rightTree1=treeStr(terminal,V,rules,i,k-1,r1)
                            rightTree2=treeStr(terminal,V,rules,k,j,r2)
                            rp1=rightTree1[1]
                            rp2=rightTree2[1]
                            thisP=p*rp1*rp2
                            if thisP>maxP:
                                maxP=thisP
                                maxRT1=rightTree1[0]
                                maxRT2=rightTree2[0]
                        else:pass
                    else: pass
        if maxP==0:
            print("can't find subtree {} range {}\'{}\' to {}\'{}\'"\
                  .format(leftSymbol,i,terminal[i],j,terminal[j]))
        return tuple(['({} {} {})'.format(leftSymbol,maxRT1,maxRT2),maxP])

def contains(set,sym):
    ele=set.copy().pop()
    if type(ele)==type(' '):
        return sym in set
    for t in set:
        if t[0]==sym:return True
    return False

def addRule(set,right):#set元素为tuple:(产生式右串，频率)
    flag=False
    for t in set:
        if t[0]==right:
            flag=True
            catch=t
            break
    if flag:
        set.remove((right,catch[1]))
        set.add((right,catch[1]+1))
    else:
        set.add((right,1))

def addRuleD(dic,key,right):#dic为{key:set of (right,freq)}
    dic[key]=dic.get(key,set())
    addRule(dic[key],right)

def key(dic,value): #find a key by given value
    return list(dic.keys())[list(dic.values()).index(value)]

def symbols(rules): #returns set of all symbols in rules
    ret=set()
    for keyi in list(rules.keys()):
        ret.add(keyi)
        for t in rules[keyi]:
            ret.add(t[0])
    return ret

def rRules(rules): #returns reversed rules
    ret={}
    for keyi in list(rules.keys()):
        for ti in rules[keyi]:
            righti=ti[0]
            p=ti[1]
            ret[righti]=ret.get(righti,set())
            ret[righti].add((keyi,p))
    return ret

def getLeft(rrules,right1,right2): #return rrules[{right1} ×{' '}× {right2}]
    ret=set()
    for rsym1 in right1:
        for rsym2 in right2:
            if type(rsym1)==type(tuple()):
                r1str=rsym1[0]
            else: r1str=rsym1
            if type(rsym2)==type(tuple()):
                r2str=rsym2[0]
            else: r2str=rsym2
            rstr=' '.join([r1str,r2str])
            leftSeti=rrules.get(rstr,set())
            ret=ret|leftSeti
    return ret

def childP(rules,leftL,t):
    rSet=rules.get(leftL[-1],set())
    for ti in rSet:
        if t==ti[0]:
            return ti[1]
    for ti in rSet:
        rL=ti[0].split(' ')
        if len(rL)==1 and not ti[0] in leftL[:-1]:
            p=childP(rules,leftL+[ti[0]],t)*ti[1]
            if p>0: return p
    return 0



if __name__ == '__main__':
    shell()

