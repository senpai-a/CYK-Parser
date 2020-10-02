%{
	/*word.lex
	 *自然语言处理导论 作业2
	 *编译工具：win_flex+gcc
	 *依赖：oarse.tab.h 由oarse.y生成
	 */
#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include "parse.tab.h"
%}

ws		[ \t\n]+

%option yylineno
%%
{ws} 	{}
"(" 	{return LP;}
")" 	{return RP;}
[^\(\)\t\n ]+ {yylval=strdup(yytext);return TOKEN;}
%%
 int yywrap(){
	return 1;
 }