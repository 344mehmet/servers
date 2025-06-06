@echo off
echo GitHub kurulumu başlatılıyor...

:: GitHub CLI'yi kontrol et
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git bulunamadı. Kurulum başlatılıyor...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe' -OutFile 'git_installer.exe'"
    start git_installer.exe
    @echo off

:: Git'i kontrol et
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo Git bulunamadi. Git'i yukleyin.
    exit /b 1
)

:: GitHub CLI'yi kontrol et
where gh >nul 2>&1
if %errorlevel% neq 0 (
    echo GitHub CLI bulunamadi. GitHub CLI'yi yukleyin.
    exit /b 1
)

:: GitHub'a giris yap
gh auth login --web

:: Repository olustur
set /p REPO_NAME="Repository adi: "
gh repo create %REPO_NAME% --public --source=. --remote=origin

:: Docker image'i GitHub'a push et
echo Docker image'i GitHub'a push ediliyor...
docker tag mcp-server:latest ghcr.io/%USERNAME%/mcp-server:latest
docker login ghcr.io -u %USERNAME% -p %GITHUB_TOKEN%
docker push ghcr.io/%USERNAME%/mcp-server:latest

echo Kurulum tamamlandı!
echo Repository URL: https://github.com/%USERNAME%/%REPO_NAME%
echo Docker image URL: ghcr.io/%USERNAME%/mcp-server:latest

pause
