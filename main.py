import asyncio
import signal
import sys
from db import init_db, close_db
from agent import create_agent
from security.security_validator import SecurityValidator
from utils.logger import Logger
from utils.conversation_manager import ConversationManager

async def main():
    # Logger'ı initialize et
    logger = Logger.get_logger("main")
    
    # Graceful shutdown için signal handler
    async def shutdown_handler(signum, frame):
        await close_db()
        sys.exit(0)
    
    # Signal handlers kaydet
    signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(shutdown_handler(s, f)))
    signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(shutdown_handler(s, f)))
    
    try:
        await init_db()   # Veritabanı bağlantısını başlat!
    except Exception as e:
        logger.error(f"Veritabanı bağlantı hatası: {str(e)}", exc_info=True)
        return
    
    print("🤖 AI Agent başlatılıyor...")
    print("🔄 Streaming mode için '/stream' komutu kullanın.")
    print("🔄 Normal mode için '/normal' komutu kullanın.\n")
    print("❌ Çıkmak için 'quit' veya 'exit' yazın.")
    
    # Conversation manager oluştur (10 mesaj hafızası)
    conversation_manager = ConversationManager(max_history=10)
    agent = create_agent(conversation_manager)
    streaming_mode = False  # Varsayılan: normal mode
    
    try:
        while True:
            try:
                mode_indicator = "🔄" if streaming_mode else "🤖"
                user_message = input(f"💬 Siz: ").strip()
                
                if user_message.lower() in ['quit', 'exit', 'çıkış', 'q']:
                    print("👋 Görüşürüz!")
                    break
                
                # Mode switch komutları
                if user_message.lower() == '/stream':
                    streaming_mode = True
                    print("✅ Streaming mode aktif")
                    continue
                elif user_message.lower() == '/normal':
                    streaming_mode = False
                    print("✅ Normal mode aktif")
                    continue

                
                if not user_message:
                    continue
                
                # Güvenlik kontrolü
                security_check = SecurityValidator.validate_request(user_message)
                if not security_check["is_valid"]:
                    print(f"🚫 {security_check['error_message']}")
                    continue
                
                # Response handling - streaming vs normal
                if streaming_mode:
                    print("🔄 Agent: ", end="", flush=True)
                    async for chunk in agent["stream_run"](user_message):
                        print(chunk, end="", flush=True)
                    print()  # Yeni satır
                else:
                    print("🤖 Agent: ", end="")
                    cevap = await agent["run"](user_message)
                    print(cevap)
                    
                print()  # Boş satır
                
            except KeyboardInterrupt:
                print("\n👋 Görüşürüz!")
                break
            except Exception as e:
                logger.error(f"Main loop hatası: {str(e)}", exc_info=True)
                print(f"❌ Hata: {e}")
                print()
    
    finally:
        # Cleanup - veritabanı bağlantılarını kapat
        logger.info("Uygulama kapatılıyor...")
        await close_db()
        logger.info("✅Uygulama temiz şekilde kapatıldı")

if __name__ == "__main__":
    asyncio.run(main())
