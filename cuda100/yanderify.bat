@echo off

set CONDA_DLL_SEARCH_MODIFICATION_ENABLE=1

call .\Scripts\activate.bat

set PATH=%CD%\Library\bin;%PATH%
set PYTHONPATH=%PYTHONPATH%;%CD%\afy;%CD%\afy\fomm

start .\python.exe afy\yanderify.py