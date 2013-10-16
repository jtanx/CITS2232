@echo off
echo Setting up the python 2 environment...
set P2=C:\python27


doskey python=%P2%\python.exe $1 $2 $3 $4 $5 $6 $7 $8 $9
doskey python2=%P2%\python.exe $1 $2 $3 $4 $5 $6 $7 $8 $9
doskey pythonw2=%P2%\pythonw.exe $1 $2 $3 $4 $5 $6 $7 $8 $9

cmd /k