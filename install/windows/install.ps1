Function Check-Hash($File, $ExpectedHash) {
    $hash = Get-FileHash -Algorithm MD5 -Path "$File"
    $hash.Hash -Eq $ExpectedHash
}

Function Safe-Download($Url, $Output, $ExpectedHash) {
    if (Test-Path "$Output") {
        echo ('Using existing ' + $Output)
    } else {
        echo ('Downloading ' + $Output)
        Invoke-WebRequest "$Url" -OutFile "$Output"
    }

    if (Check-Hash -File "$Output" -ExpectedHash $ExpectedHash) {
        return
    } else {
        echo ('Re-downloading ' + $Output)
        Remove-Item "$Output"
        Safe-Download -Url $Url -Output $Output -ExpectedHash $ExpectedHash
    }
}

if ((Get-Item .).FullName -match ' ') {
    echo 'Your path contains spaces. This will lead to issues.'
    echo 'Examples of good paths: C:\Users\username\Desktop\yanderify; D:\myfiles\code'
    echo 'Examples of bad paths: C:\Users\username\Desktop\my programs; D:\my downloads\yanderify'
    pause
    exit
}

if (Get-Command pythonw -ErrorAction SilentlyContinue) {
    echo 'WARNING: you have python already installed. sometimes this will lead to issues.'
    echo 'see this page about a similar program: https://forum.faceswap.dev/app.php/faqpage#f1r1'
    echo 'you can choose to continue installation or you can exit this window.'
    pause
}

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
    start -Wait -NoNewWindow -FilePath .\miniconda.exe -ArgumentList "/InstallationType=JustMe","/AddToPath=0","/RegisterPython=0","/S","/D=$installdir"
}

Safe-Download -Url 'https://github.com/dunnousername/first-order-model/releases/download/v1.0.0/fomm.zip' -Output fomm.zip -ExpectedHash 'F50E5E39967ABAEB695B67F727E59892'

if (Test-Path '.\fomm\') {
    echo 'Using existing first-order-motion-model install'
} else {
    Expand-Archive -Path fomm.zip
}

Safe-Download -Url 'https://github.com/dunnousername/yanderifier/releases/download/model/checkpoint.tar' -Output .\yanderify\checkpoint.tar -ExpectedHash 'B667124DD6E324F42C3DF0B068B8C593'

echo 'starting post-install script'
& .\install\windows\postinstall.bat "$installdir\condabin\conda.bat"
cp .\miniconda\pkgs\ffmpeg-*\Library\bin\* .\miniconda\Library\bin\
pause
exit