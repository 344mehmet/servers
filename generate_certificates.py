import ssl
import os
import sys

def generate_self_signed_cert():
    """Self-signed SSL sertifikası oluşturur"""
    if os.path.exists('server.crt') and os.path.exists('server.key'):
        print("Sertifikalar zaten mevcut. Yeni oluşturulmayacak.")
        return

    try:
        # SSL bağlamı oluştur
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_default_certs()
        
        # Sertifika oluştur
        key = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH).get_ca_certs()[0]
        
        # Sertifikayı dosyaya yaz
        with open('server.crt', 'wb') as f:
            f.write(ssl.DER_cert_to_PEM_cert(key).encode())
        
        # Anahtar dosyasını oluştur
        with open('server.key', 'wb') as f:
            f.write(ssl.get_default_verify_paths().openssl_cafile.encode())
        
        print("Sertifikalar başarıyla oluşturuldu:")
        print("- server.crt")
        print("- server.key")
    except Exception as e:
        print(f"Sertifika oluşturma hatası: {e}")
        sys.exit(1)

if __name__ == '__main__':
    generate_self_signed_cert()
