$arch = $env:PROCESSOR_ARCHITECTURE
if (Test-Path '.\miniconda.exe') {
    echo 'Using existing install executable'
} elseif ($arch -eq 'x86') {
    echo 'Installing 32-bit...'
    Invoke-WebRequest 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86.exe' -OutFile miniconda.exe
} elseif ($arch -eq 'amd64') {
    echo 'Installing 64-bit...'
    Invoke-WebRequest 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe' -OutFile miniconda.exe
} else {
    echo 'Could not determine architecture'
    exit
}

$installdir = (Get-Item .).FullName + '\miniconda'

if (Test-Path $installdir) {
    echo 'Using existing installation'
} else {
    .\miniconda.exe /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /S /D=$installdir
}

if (Test-Path '.\fomm.zip') {
    echo 'Using existing fomm.zip'
} else {
    Invoke-WebRequest 'https://github.com/dunnousername/first-order-model/releases/download/v1.0.0/fomm.zip' -OutFile fomm.zip
}

if (Test-Path '.\fomm\') {
    echo 'Using existing first-order-motion-model install'
} else {
    Expand-Archive -Path fomm.zip
}

if (Test-Path '.\yanderify\checkpoint.tar') {
    echo 'not redownloading checkpoint'
} else {
    Invoke-WebRequest 'https://github.com/dunnousername/yanderifier/releases/download/model/checkpoint.tar' -OutFile .\yanderify\checkpoint.tar
}

echo 'starting post-install script'
cmd /k ($installdir + '\Scripts\activate.bat') "&" powershell -File install\windows\postinstall.ps1
cmd /k ($installdir + '\Scripts\activate.bat') "&" powershell -File install\windows\postinstall2.ps1
exit /b