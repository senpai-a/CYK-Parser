%{	/*parse.y
	 *自然语言处理导论 作业2
	 *编译工具：win_bison+gcc
	 */
#include <stdio.h>
#include <ctype.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#define YYSTYPE char *
extern FILE *yyin,*yyout;

%}
%token TOKEN LP RP
%start F
%%
F:S|F S
S:LP TOKEN C RP{
	$$=strdup($2);
	fprintf(yyout,"%s->%s\n",$2,$3);
	free($2); free($3);
	//printf("S->(%s C)\n",$$);
}
|LP S RP {
	$$=strdup($2);
	free($2);
	//printf("S->(S)\n");
}

C:TOKEN {
	$$=strdup($1);
	free($1);
	//printf("C->%s\n",$$);*/
}
|X {
	$$=strdup($1);
	free($1);
	//printf("C->X\n");
}

X:S {
	//printf("X->S\n");
	$$=strdup($1);
	free($1);
}
|X S {	
	int len=strlen($1)+strlen($2)+2;
	int len1=strlen($1);
	$$=strdup($1);
	$$=(char*)realloc($$,len*sizeof(char));
	$$[len1]=' ';
	$$[len1+1]=0;
	strcat($$,$2);
	//printf("X->XS\n");
	free($1); free($2);
}

%%

int yyerror(char *msg){
	printf("Error: %s \n", msg);
}

int main(int argc,char** argv){
	if(argc!=3){
		printf("Usage: learn i j\n"
		"learn grammar from wsj_i to wsj_j");
		return 0;
	}
	int starti=atoi(argv[1]);
	int maxi=atoi(argv[2]);
	if(starti>maxi || maxi<=0 || maxi>199
		||starti>199 ||starti <=0){
		printf("parameter out of range: 1 to 199\n");
		return 0;
	}
	
	yyout=fopen("../rules.txt","w");
	if(!yyout){
		printf("output stream open failed\n");
		return 0;
	}
	
	yyin=0;
	for(int i=starti;i<=maxi;i++){
		char fileName[255]={0};
		sprintf(fileName,"../Data/treebank/combined/wsj_%4d.mrg",i);
		for(int j=0;j<strlen(fileName);j++)
			if(fileName[j]==' ') fileName[j]='0';	
		
		fclose(yyin);
		yyin=fopen(fileName,"r");
		if(!yyin){
			printf("[%d/%d] failed to open: %s\n"
					"aborting...",i,maxi-starti+1,fileName);
			return 0;
		}
		printf("[%d/%d] working on: %s\n",i,maxi-starti+1,fileName);
		yyparse();		
	}
	fclose(yyin);
	fclose(yyout);
	printf("process complete\n");
	return 0;
}