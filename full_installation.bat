@echo off
echo MCP Server Kurulumu Başlatılıyor...

:: 1. Docker'ı Kontrol Et ve Kur
:CHECK_DOCKER
echo 1. Docker kontrolü yapılıyor...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker bulunamadı. Kurulum başlatılıyor...
    
    :: Docker Desktop'ı indir ve kur
    powershell -Command "Invoke-WebRequest -Uri 'https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe' -OutFile 'docker_installer.exe'"
    start docker_installer.exe
    
    echo Lütfen Docker kurulumunu tamamlayın ve bu pencereyi yeniden açın.
    pause
    exit
)

:: 2. Python'ı Kontrol Et ve Kur
:CHECK_PYTHON
echo 2. Python kontrolü yapılıyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python bulunamadı. Kurulum başlatılıyor...
    
    :: Python'ı indir ve kur
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe' -OutFile 'python_installer.exe'"
    start python_installer.exe
    
    echo Lütfen Python kurulumunu tamamlayın ve bu pencereyi yeniden açın.
    pause
    exit
)

:: 3. Gerekli Python Kütüphanelerini Yükle
echo 3. Python kütüphaneleri yükleniyor...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: 4. Docker Image'i Oluştur
echo 4. Docker image'i oluşturuluyor...

:: Dockerfile oluşturma
if not exist "Dockerfile" (
    echo FROM python:3.11-slim > Dockerfile
    echo WORKDIR /app >> Dockerfile
    echo COPY . /app >> Dockerfile
    echo RUN pip install --no-cache-dir -r requirements.txt >> Dockerfile
    echo CMD ["python", "mcp_server.py"] >> Dockerfile
)

docker build -t mcp-server .

:: 5. Docker Container'ı Başlat
echo 5. Docker container başlatılıyor...
docker run -d --name mcp-server -p 8888:8888 mcp-server

:: 6. SSL Sertifikalarını Oluştur
echo 6. SSL sertifikaları oluşturuluyor...
python generate_certificates.py

:: 7. Kurulum Tamamlandı
echo Kurulum tamamlandı!
echo MCP Server Docker container'ında çalışıyor.
echo Container durumunu kontrol etmek için: docker ps
echo Container'ı durdurmak için: docker stop mcp-server
echo Container'ı yeniden başlatmak için: docker start mcp-server
echo Container'ı tamamen silmek için: docker rm -f mcp-server

pause
