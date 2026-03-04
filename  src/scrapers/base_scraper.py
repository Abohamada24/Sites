from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging

class BaseScraper(ABC):
    """الكلاس الأساسي لجميع الـ Scrapers"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = self._create_session()
    
    def _create_session(self):
        """إنشاء session مع headers مناسبة"""
        import requests
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
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
        """استخراج رابط التحميل المباشر من صفحة"""
        pass