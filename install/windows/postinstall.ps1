conda init powershell
conda env create -f environment.yml
$ErrorActionPreference = 'Continue'
cp miniconda\Library\bin\libiomp5md.dll miniconda\
cp miniconda\Library\bin\mkl_*.dll miniconda\
exit