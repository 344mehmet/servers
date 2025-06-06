@echo off
echo MCP Server başlatılıyor...

:: Gerekli kütüphaneleri yükle
pip install -r requirements.txt

:: Python virtualenv'i oluştur ve aktifleştir
python -m venv .venv
.venv\Scripts\activate

:: Sertifikaları oluştur
python generate_certificates.py

:: Server'ı başlat
echo MCP Server başlatılıyor. Ctrl+C ile durdurabilirsiniz.
python mcp_server.py
