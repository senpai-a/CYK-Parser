win_bison -d parse.y
win_flex word.lex
gcc -o learn.exe parse.tab.c lex.yy.c -std=c99
