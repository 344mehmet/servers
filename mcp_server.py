import asyncio
import ssl
import json
from cryptography.fernet import Fernet
from datetime import datetime
import logging
from typing import Dict, Any

# Güvenli bağlantı için SSL/TLS sertifikaları
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile="server.crt", keyfile="server.key")

# Şifreleme anahtarı
KEY = Fernet.generate_key()
fernet = Fernet(KEY)

# Günlük kaydı ayarla
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()
    ]
)

class MCPConnection:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.address = writer.get_extra_info('peername')
        self.session_key = None
        self.is_authenticated = False
        self.last_active = datetime.now()

    async def encrypt_message(self, message: Dict[str, Any]) -> bytes:
        """Mesajı şifreler ve bayt dizisine dönüştürür"""
        json_data = json.dumps(message)
        encrypted = fernet.encrypt(json_data.encode())
        return encrypted

    async def decrypt_message(self, encrypted_data: bytes) -> Dict[str, Any]:
        """Şifrelenmiş mesajı çözer ve sözlüğe dönüştürür"""
        try:
            decrypted = fernet.decrypt(encrypted_data)
            return json.loads(decrypted.decode())
        except Exception as e:
            logging.error(f"Mesaj şifre çözme hatası: {e}")
            raise

    async def send_message(self, message: Dict[str, Any]):
        """Şifrelenmiş mesaj gönderir"""
        encrypted = await self.encrypt_message(message)
        self.writer.write(len(encrypted).to_bytes(4, 'big'))
        self.writer.write(encrypted)
        await self.writer.drain()

    async def receive_message(self) -> Dict[str, Any]:
        """Şifrelenmiş mesaj alır ve çözer"""
        size_bytes = await self.reader.readexactly(4)
        size = int.from_bytes(size_bytes, 'big')
        encrypted_data = await self.reader.readexactly(size)
        return await self.decrypt_message(encrypted_data)

class MCPProtocol(asyncio.Protocol):
    def __init__(self):
        self.connections = {}
        self.message_queue = asyncio.Queue()

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Yeni bağlantıları yönetir"""
        conn = MCPConnection(reader, writer)
        self.connections[conn.address] = conn
        logging.info(f"Yeni bağlantı: {conn.address}")

        try:
            while True:
                message = await conn.receive_message()
                conn.last_active = datetime.now()
                
                if not conn.is_authenticated:
                    if message.get('type') == 'AUTHENTICATE':
                        if await self.authenticate(conn, message):
                            conn.is_authenticated = True
                            await conn.send_message({
                                'type': 'AUTH_RESPONSE',
                                'status': 'SUCCESS'
                            })
                        else:
                            await conn.send_message({
                                'type': 'AUTH_RESPONSE',
                                'status': 'FAILED'
                            })
                            break
                    else:
                        await conn.send_message({
                            'type': 'ERROR',
                            'message': 'Önce kimlik doğrulaması yapmalısınız'
                        })
                        break
                else:
                    await self.handle_message(conn, message)

        except Exception as e:
            logging.error(f"Bağlantı hatası: {e}")
        finally:
            self.connections.pop(conn.address, None)
            writer.close()
            await writer.wait_closed()
            logging.info(f"Bağlantı kapatıldı: {conn.address}")

    async def authenticate(self, conn: MCPConnection, message: Dict[str, Any]) -> bool:
        """Kimlik doğrulama işlemini gerçekleştirir"""
        credentials = message.get('credentials', {})
        # Gerçek kimlik doğrulama mantığı buraya eklenecek
        return True  # Test için geçici olarak true döndürüyor

    async def handle_message(self, conn: MCPConnection, message: Dict[str, Any]):
        """Gelen mesajları işler"""
        message_type = message.get('type')
        
        if message_type == 'HEARTBEAT':
            await conn.send_message({
                'type': 'HEARTBEAT_RESPONSE',
                'status': 'OK'
            })
        elif message_type == 'DATA':
            await self.process_data(conn, message)
        else:
            await conn.send_message({
                'type': 'ERROR',
                'message': f'Bilinmeyen mesaj tipi: {message_type}'
            })

    async def process_data(self, conn: MCPConnection, message: Dict[str, Any]):
        """Gelen verileri işler"""
        data = message.get('data', {})
        # Veri işleme mantığı buraya eklenecek
        await conn.send_message({
            'type': 'DATA_RESPONSE',
            'status': 'SUCCESS',
            'result': data
        })

async def main():
    protocol = MCPProtocol()
    server = await asyncio.start_server(
        protocol.handle_connection,
        '0.0.0.0',
        8888,
        ssl=ssl_context
    )
    
    async with server:
        logging.info("MCP Server başlatıldı. Bağlantı bekleniyor...")
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server kapatılıyor...")
