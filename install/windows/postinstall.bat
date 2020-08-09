@echo off
call %1 activate
call %1 env create -f environment.yml || echo miniconda already installed
call %1 activate yanderify
python install\postinstall.py
exit /b