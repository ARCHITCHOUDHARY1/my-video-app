# utils/logger_config.py
import logging
import os
from datetime import datetime
from config import settings

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    if logger.handlers:
        logger.handlers.clear()
    
    os.makedirs(settings.log_dir, exist_ok=True)
    
    log_file = os.path.join(
        settings.log_dir,
        f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
