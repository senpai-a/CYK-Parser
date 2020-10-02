@echo off
echo 请输入学习语法的文档范围wsj_i~wsj_j
echo  i=
set /p i=
echo  j=
set /p j=
learn.exe %i% %j%
pause
