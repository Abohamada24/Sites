"""
Logging utilities
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(
    name: str = 'SubtitleDownloader',
    level: int = logging.INFO,
    log_file: bool = False,
    log_dir: str = './logs'
) -> logging.Logger:
    """
    إعداد Logger
    
    Args:
        name: اسم الـ Logger
        level: مستوى السجلات
        log_file: حفظ السجلات في ملف
        log_dir: مجلد السجلات
        
    Returns:
        Logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # تنسيق الرسائل
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    if log_file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_handler = logging.FileHandler(
            log_path / f'{name}_{timestamp}.log',
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger