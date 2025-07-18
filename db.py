from tortoise import Tortoise
from utils.logger import Logger
from config import config

# Logger'ı initialize et
logger = Logger.get_logger("database")

async def init_db():
    try:      
        # Production-ready database configuration
        db_config = {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "host": config.DB_HOST,
                        "port": config.DB_PORT,
                        "user": config.DB_USER,
                        "password": config.DB_PASSWORD,
                        "database": config.DB_NAME,
                        "minsize": config.DB_MIN_CONNECTIONS,
                        "maxsize": config.DB_MAX_CONNECTIONS,
                        "max_queries": 50000,   # Max queries per connection
                        "max_inactive_connection_lifetime": 300,  # 5 dakika
                        "timeout": config.DB_CONNECTION_TIMEOUT,
                        "command_timeout": config.DB_COMMAND_TIMEOUT,
                        "server_settings": {
                            "jit": "off"        # JIT off for better performance
                        }
                    }
                }
            },
            "apps": {
                "models": {
                    "models": ["models.hotel_problem"],
                    "default_connection": "default",
                }
            }
        }
        
        await Tortoise.init(config=db_config)
        await Tortoise.generate_schemas()       
        
    except Exception as e:
        logger.error(f"Veritabanı başlatma hatası: {str(e)}", exc_info=True)
        raise

async def close_db():
    """Veritabanı bağlantısını temiz şekilde kapat"""
    try:
        await Tortoise.close_connections()
        
    except Exception as e:
        logger.error(f"Veritabanı kapatma hatası: {str(e)}", exc_info=True)