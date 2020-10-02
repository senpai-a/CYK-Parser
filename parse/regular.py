# -*- coding:utf8 -*-

import re

def shell():
    regular("../rules1.txt","../ruleCNF.txt")


def regular(inputF, outputF):
    rules={}
    srcRules=open(inputF, 'r').read().split('\n')
    #pass 1:去重，去除epsilon产生式
    for rulei in srcRules:
        tokenL=re.split('->',rulei)

        key=tokenL[0]
        value=tokenL[1]
        rightSymL=value.split(' ')
        while '-NONE-' in rightSymL:
            rightSymL.remove('-NONE-')
        if len(rightSymL)!=0:
            value=' '.join(rightSymL)
            rules[key]=rules.get(key,set())
            rules[key].add(value)
        #print(tokenL)
    if '-NONE-' in rules:
        del rules['-NONE-']
    print(rules)
    #pass 2 转换成CNF
    keys=list(rules.keys())
    for keyi in keys:
        rSet=rules[keyi]
        for rightStr in rSet:
            rightSymL=rightStr.split(' ')
            if len(rightSymL)>2:
                rSet.remove(rightStr)
                newSym='_'.join(rightSymL[1:])
                rSet.add(' '.join([rightSymL[0],newSym]))
                newSymL=newSym.split('_')
                while len(newSymL)>1:
                    rules[newSym]=rules.get(newSym,set())
                    nextNewSym='_'.join(newSymL[1:])
                    newRightStr=' '.join([newSymL[0],nextNewSym])
                    rules[newSym].add(newRightStr)
                    del newSymL[0]
                    newSym=nextNewSym
            else:
                pass
    print(rules)

if __name__ == '__main__':
    shell()

