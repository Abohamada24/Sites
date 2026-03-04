"""
Configuration settings for the application
"""

import os
from pathlib import Path
from typing import Dict

class Config:
    """إعدادات التطبيق"""
    
    # المجلدات الافتراضية
    BASE_DIR = Path(__file__).parent.parent.parent
    OUTPUT_DIR = BASE_DIR / "subtitles"
    TEMP_DIR = BASE_DIR / "temp"
    
    # إعدادات التحميل
    CHUNK_SIZE = 8192
    TIMEOUT = 30
    MAX_RETRIES = 3
    
    # User Agent
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    # اللغات المدعومة
    SUPPORTED_LANGUAGES = {
        'ara': 'Arabic',
        'eng': 'English',
        'fre': 'French',
        'spa': 'Spanish',
        'ger': 'German',
    }
    
    # صيغ الملفات المدعومة
    SUPPORTED_FORMATS = ['.srt', '.vtt', '.ass', '.ssa', '.sub']
    
    @classmethod
    def ensure_directories(cls):
        """إنشاء المجلدات المطلوبة"""
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """الحصول على Headers للطلبات"""
        return {
            'User-Agent': cls.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }