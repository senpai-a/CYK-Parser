# CYK-Parser
## NLP作业：句法分析器

- Parser: 40 points 
- In this assignment, you will build an English treebank parser. You will consider both the problem of learning a grammar from a treebank and the problem of parsing with that grammar.
  The data is from the Penn Treebank, you can divide the data into the training data, the development data, and the blind test data as required.
- You are recommended to build an array-based CYK parser, but you are also free to build an agenda-driven PCFG parser.

## 数据来源
- http://www.nltk.org/nltk_data/

### 程序运行环境：
	Data/treebank/： 数据：将Data/treebank.zip解压
	
	rules.txt：	learn.exe输出的文法，每行为一个生成式
	learn/parse.y ：	yacc移进-规约解析器代码
	learn/word.lex ：	lex词法分析器代码
	learn/build.bat ：	自动编译以上两个文件，生成learn/learn.exe。依赖win_flex.exe和win_bison.exe，他们是windows版的Lex和Yacc，依赖gcc（Lex/Yacc实际上是C语言框架，因此需要一个C编译器）
	learn/learn.cmd ：	使用这个脚本，输入学习数据的范围(wsj_i到wsj_j)，自动学习输出到rules.txt
	
	parse/ruleT.txt：	parse.py和parsePCFG.py的输入文件，文法序列
	parse/textT.txt：	parse.py和parsePCFG.py的输入文件，待解析的句子
	parse/parse.py：	CYK CFG解析器, python3.6
	parse/parsePCFG.py: 	CYK PCFG解析程序, python3.6
	
### 使用方法：
	在Data/下解压treebank.zip，得到数据在Data/treebank/下。
	运行learn/build.bat，编译learn.exe
	运行learn/learn.cmd，得到rules.txt
	复制rules.txt到parse/ruleT.txt
	在parse/textT.txt中写你的英文句子，第一行以.START开头，之后每行一个句子。
	运行parse/parse.py或parse/parsePCFG.py
	
### 描述：
	学习文法：
		学习文法的程序在learn目录下。
		数据Data\treebank\combined\wsj0001.mrg~wsj0199.mrg是分析好的语法树。使用YACC/Lex从这些语法树中学习CFG，写入rules.txt，每行一个产生式。
		
		Yacc代码learn/parse.y使用这个CFG识别语法树结构：
        (
            { F, S, X },
            { TOKEN, (, ) },
            { F->S|FS|(S), S->(S)|(TOKEN C), C->TOKEN|X, X->S|XS },
            F
        )
	
	解析句子：
		解析句子的程序在parse目录下。
		parse.py:CFG解析程序
		parsePCFG.py:PCFG解析程序
		ruleT.txt:文法序列，每行一个产生式
		textT.txt:待解析的句子序列，第一行是开始标记，它将被忽略，这之后每行一个英语句子。
		
		这两个程序都使用CYK算法解析句子。

parse.py首先执行regular函数，读入文法序列，进行两遍处理，第一遍将文法序列转换为文法集合，然后丢弃epsilon产生式（这意味着得到文法是训练用语法树使用的文法的子文法，但是处理后的文法产生的语言仍是训练语料的超集），第二遍将文法中所有产生串长度大于2的产生式转换为CNF的形式。第二遍处理后的文法和第一遍处理后的文法是等价的，但是符合CNF的要求。

parsePCFG.py的regular函数将在第一遍统计每个产生式出现的频率，第二遍相同，第三遍将文法转换为PCFG文法，对于任意非终结符N的所有产生式(N->ωi,p),Σp=1. p由产生式出现的频率除以非终结符N的所有产生式出现的频率和得到（极大似然）
		
parse.py之后从textT.txt获得所有英语句子，每一个句子都被传入tokenize函数，转换为单词的序列。tokenize函数使用前向最大匹配算法对句子进行分词，词典由文法中出现的所有符号得到。序列化之后的句子被传入parseSentence函数，这个函数使用CYK算法解析句子。
		
CYK算法是一种动态规划算法，它维护一个状态矩阵V，V[i][j]保存若干个元素对(N,k),N表示句子第i~j个符号组成的子句子可以规约成的非终结符号，k表示N是从V[i][k-1]和V[k][j]的某个可能的非终结符号规约成的。parseSentence函数解析完成之后返回这个状态矩阵V
		
parsePCFG.py的tokenize函数和parseSentence函数所做的事情和parse.py完全一样，只是数据结构实现有细微区别，这是因为parsePCFG文法的数据结构稍微不同(多了一个概率字段)。
	
parse.py和parsePCFG.py最后将状态矩阵V和句子(词序列)传入printTree函数，printTree函数将V和句子传入treeStr函数来构建串行化表示(字符串形式的)的语法树。
		
parse.py的treeStr从符号S和整个句子的范围0\~N-1的范围开始，递归下降构建语法树。treeStr获得参数N,i和j，N表示i\~j范围的子句子规约成的非终结符，返回所有可能的以N为根的子树的字符串表示的列表。若i等于j，则返回叶子节点和叶子节点父节点(这个节点的非终结符表示词性)组成的最底层树'(N T)',T是词序列的第i个单词。若i不等于j,treeStr查找V[i][j]，其中非终结符为N的元素对可能有多个k，每个k都是一种可能的子树，从文法中查找N的产生式，找到所有满足X出现在V[i][k-1]中，Y出现在V[k][j]中的产生式N->XY，调用treeStr(X,i,k-1)和treeStr(Y,k,j)获得X和Y产生所有可能的字符串，根据所有的k，每个k可能的N->XY,和X=>ω1,Y=>ω2，返回所有可能的语法树的字符串'(N ω1 ω2)'
		
parsePCFG的treeStr使用内向算法，符号S和整个句子的范围0~N-1的范围开始，递归下降寻找概率最大的一颗语法树。treeStr获得参数N，i和j，返回以N为根最大概率的一颗子树的字符串表示和相应概率p。若i等于j，则返回最底层树'(N T)'和N->T的概率。若i不等于j，则treeStr查找V[i][j]，其中非终结符为N的元素对可能有多个k，每个k都是一种可能的子树，从文法中查找N的产生式，找到所有满足X出现在V[i][k-1]中，Y出现在V[k][j]中的产生式(N->XY,p)，调用treeStr(X,i,k-1)和treeStr(Y,k,j)获得X和Y产生最大概率的字符串ω1,ω2和概率p1,p2，计算p\*p1\*p2即k下N=>ω1ω2语法树的概率。选取所有k和所有可能的产生式得到所有语法树中概率最大(这个最大的概率记为maxp)的一个N=>W1 W2，返回('(N W1 W2)',maxp)

[![LICENSE](https://img.shields.io/badge/license-Anti%20996-blue.svg)](https://github.com/996icu/996.ICU/blob/master/LICENSE)
[![Badge](https://img.shields.io/badge/link-996.icu-red.svg)](https://996.icu/#/zh_CN)
