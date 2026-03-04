"""
Subscene scraper
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from .base_scraper import BaseScraper

class SubsceneScraper(BaseScraper):
    """البحث والتحميل من Subscene"""
    
    def __init__(self):
        """تهيئة Subscene Scraper"""
        super().__init__()
        self.base_url = "https://subscene.com"
    
    def search(self, query: str, language: str = 'Arabic', limit: int = 10) -> List[Dict]:
        """
        البحث عن ترجمات في Subscene
        
        Args:
            query: اسم الفيلم أو المسلسل
            language: اسم اللغة بالإنجليزية
            limit: عدد النتائج
            
        Returns:
            قائمة بالنتائج
        """
        search_url = f"{self.base_url}/subtitles/searchbytitle"
        
        self.logger.info(f"🔍 البحث عن: {query}")
        
        try:
            # إرسال طلب البحث
            response = self.session.post(
                search_url,
                data={'query': query},
                timeout=10
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            
            # البحث عن النتائج
            search_results = soup.find('div', class_='search-result')
            
            if not search_results:
                self.logger.warning("⚠️ لم يتم العثور على نتائج")
                return []
            
            items = search_results.find_all('li')
            
            for item in items[:limit]:
                try:
                    link = item.find('a')
                    if link:
                        title = link.text.strip()
                        url = self.base_url + link['href']
                        
                        results.append({
                            'title': title,
                            'url': url,
                            'language': language,
                        })
                        
                except:
                    continue
            
            self.logger.info(f"✅ تم العثور على {len(results)} نتيجة")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في البحث: {e}")
            return []
    
    def get_subtitle_list(self, movie_url: str, language: str = 'Arabic') -> List[Dict]:
        """
        الحصول على قائمة الترجمات المتاحة لفيلم
        
        Args:
            movie_url: رابط صفحة الفيلم
            language: اسم اللغة
            
        Returns:
            قائمة بالترجمات
        """
        try:
            self.logger.info(f"📋 جلب قائمة الترجمات...")
            
            response = self.session.get(movie_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            subtitles = []
            
            # البحث عن جدول الترجمات
            table = soup.find('table')
            
            if not table:
                return []
            
            rows = table.find_all('tr')
            
            for row in rows:
                try:
                    # التحقق من اللغة
                    lang_cell = row.find('td', class_='a1')
                    if lang_cell:
                        lang_span = lang_cell.find('span')
                        if lang_span and language.lower() in lang_span.text.lower():
                            # الحصول على الرابط
                            link = row.find('a', href=re.compile(r'/subtitles/'))
                            
                            if link:
                                title = link.text.strip()
                                url = self.base_url + link['href']
                                
                                # معلومات إضافية
                                uploader = None
                                comment = None
                                
                                user_cell = row.find('td', class_='a5')
                                if user_cell:
                                    uploader = user_cell.text.strip()
                                
                                comment_cell = row.find('td', class_='a6')
                                if comment_cell:
                                    comment = comment_cell.text.strip()
                                
                                subtitles.append({
                                    'title': title,
                                    'url': url,
                                    'language': language,
                                    'uploader': uploader,
                                    'comment': comment,
                                })
                                
                except:
                    continue
            
            self.logger.info(f"✅ تم العثور على {len(subtitles)} ترجمة")
            return subtitles
            
        except Exception as e:
            self.logger.error(f"❌ خطأ: {e}")
            return []
    
    def get_download_link(self, subtitle_page_url: str) -> Optional[str]:
        """
        استخراج رابط التحميل
        
        Args:
            subtitle_page_url: رابط صفحة الترجمة
            
        Returns:
            رابط التحميل المباشر
        """
        try:
            self.logger.info(f"🔗 استخراج رابط التحميل...")
            
            response = self.session.get(subtitle_page_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # البحث عن زر التحميل
            download_button = soup.find('a', {'id': 'downloadButton'})
            
            if download_button and download_button.get('href'):
                download_url = self.base_url + download_button['href']
                self.logger.info(f"✅ تم العثور على رابط التحميل")
                return download_url
            
            self.logger.warning(f"⚠️ لم يتم العثور على رابط التحميل")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ خطأ: {e}")
            return None
    
    def download(
        self, 
        subtitle_url: str, 
        output_dir: str = './subtitles',
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        تحميل ترجمة من Subscene
        
        Args:
            subtitle_url: رابط صفحة الترجمة
            output_dir: مجلد الحفظ
            filename: اسم الملف
            
        Returns:
            مسار الملف المحمل
        """
        try:
            # الحصول على رابط التحميل
            download_url = self.get_download_link(subtitle_url)
            
            if not download_url:
                return None
            
            # التحميل
            from ..core.downloader import SubtitleDownloader
            
            downloader = SubtitleDownloader(output_dir=output_dir)
            filepath = downloader.download(download_url, filename=filename)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في التحميل: {e}")
            return None