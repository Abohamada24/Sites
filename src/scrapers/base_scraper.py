"""
Base scraper class for all subtitle scrapers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging
import requests
from ..core.config import Config

class BaseScraper(ABC):
    """الكلاس الأساسي لجميع الـ Scrapers"""
    
    def __init__(self):
        """تهيئة الـ Scraper"""
        self.logger = self._setup_logger()
        self.session = self._create_session()
        self.config = Config
    
    def _setup_logger(self) -> logging.Logger:
        """إعداد Logger"""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _create_session(self) -> requests.Session:
        """إنشاء session مع headers مناسبة"""
        session = requests.Session()
        session.headers.update(Config.get_headers())
        return session
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> List[Dict]:
        """
        البحث عن ترجمات
        
        Args:
            query: نص البحث
            **kwargs: معاملات إضافية (language, year, etc.)
            
        Returns:
            قائمة بالنتائج
        """
        pass
    
    @abstractmethod
    def download(self, url: str, output_dir: str = "./") -> Optional[str]:
        """
        تحميل ملف ترجمة
        
        Args:
            url: رابط الترجمة
            output_dir: مجلد الحفظ
            
        Returns:
            مسار الملف المحمل
        """
        pass
    
    def get_download_link(self, page_url: str) -> Optional[str]:
        """
        استخراج رابط التحميل المباشر من صفحة
        
        Args:
            page_url: رابط الصفحة
            
        Returns:
            رابط التحميل المباشر
        """
        return None
    
    def validate_url(self, url: str) -> bool:
        """
        التحقق من صحة الرابط
        
        Args:
            url: الرابط للتحقق منه
            
        Returns:
            True إذا كان الرابط صحيح
        """
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except:
            return False