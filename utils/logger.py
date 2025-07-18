import logging
import sys
from pathlib import Path

class Logger:
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Singleton logger instance döndürür"""
        if name not in cls._loggers:
            cls._loggers[name] = cls._create_logger(name)
        return cls._loggers[name]
    
    @classmethod
    def _create_logger(cls, name: str) -> logging.Logger:
        """Logger konfigürasyonunu oluşturur"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Eğer handler zaten varsa, duplicate eklememe
        if logger.handlers:
            return logger
        
        # Log klasörü oluştur
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File formatter (detailed)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console formatter (sadece mesaj)
        console_formatter = logging.Formatter('%(message)s')
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler(
            log_dir / f"{name}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.FileHandler(
            log_dir / f"{name}_errors.log",
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
        
        return logger 