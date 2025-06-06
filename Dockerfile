# Güvenli ve hafif taban imaj
FROM python:3.11-windowsservercore-ltsc2022

# Node.js kur
RUN curl -fsSL https://nodejs.org/dist/v18.17.1/node-v18.17.1-win-x64.zip -o node.zip \
    && mkdir -p /nodejs \
    && tar -xvf node.zip -C /nodejs \
    && del node.zip

# Ortam değişkenlerini ayarla
ENV PATH=/nodejs:$PATH

# Python bağımlılıklarını kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Çalışma dizini oluştur
WORKDIR /app

# Kodu kopyala
COPY . .

# Next.js bağımlılıklarını kur
RUN npm install next@15.2.4

# Komutu belirle
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# Portları aç
EXPOSE 8000
EXPOSE 3000 
