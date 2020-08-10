@echo off

if not defined sane echo Please use the shortcut instead of the batch file. && pause && exit
set CONDA_DLL_SEARCH_MODIFICATION_ENABLE=1

cd ..
set MINICONDA_LOCATION=%CD%\miniconda
set FOMM_LOCATION=%CD%\fomm
cd yanderify

call %MINICONDA_LOCATION%\Scripts\activate.bat

call %MINICONDA_LOCATION%\condabin\conda.bat activate yanderify

set PATH=%PATH%;%MINICONDA_LOCATION%\Library\bin
set PYTHONPATH=%PYTHONPATH%;%FOMM_LOCATION%

start python yanderify.py