@echo off
call %1 activate
call conda.bat env create -f environment.yml || echo miniconda already installed
call conda.bat activate yanderify
python install\postinstall.py
exit /b