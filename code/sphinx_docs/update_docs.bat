@echo off
echo [1/3] Regenerating .rst files with sphinx-apidoc...
sphinx-apidoc -o source ../TBCPackage ../TBC_analysis --force

echo [2/3] Building HTML documentation...
call make.bat html

echo [3/3] Opening index.html...
start build\html\index.html

echo Done!
