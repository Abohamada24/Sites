"""
OpenSubtitles scraper (web scraping method)
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from pathlib import Path
from .base_scraper import BaseScraper

class OpenSubtitlesScraper(BaseScraper):
    """البحث والتحميل من OpenSubtitles"""
    
    def __init__(self):
        """تهيئة OpenSubtitles Scraper"""
        super().__init__()
        self.base_url = "https://www.opensubtitles.org"
        
        # Language codes mapping
        self.language_codes = {
            'ara': 'Arabic',
            'eng': 'English',
            'fre': 'French',
            'spa': 'Spanish',
            'ger': 'German',
            'ita': 'Italian',
            'por': 'Portuguese',
            'rus': 'Russian',
            'jpn': 'Japanese',
            'kor': 'Korean',
        }
    
    def search(
        self, 
        query: str, 
        language: str = 'ara',
        season: Optional[int] = None,
        episode: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        البحث عن ترجمات في OpenSubtitles
        
        Args:
            query: اسم الفيلم أو المسلسل
            language: كود اللغة (ara, eng, etc.)
            season: رقم الموسم (للمسلسلات)
            episode: رقم الحلقة (للمسلسلات)
            limit: عدد النتائج المطلوبة
            
        Returns:
            قائمة بالنتائج
        """
        # تنظيف نص البحث
        clean_query = query.replace(' ', '+')
        
        # بناء URL البحث
        search_url = f"{self.base_url}/en/search/sublanguageid-{language}/moviename-{clean_query}"
        
        # إضافة معاملات المسلسل إذا وجدت
        if season is not None:
            search_url += f"/season-{season}"
        if episode is not None:
            search_url += f"/episode-{episode}"
        
        self.logger.info(f"🔍 البحث في: {search_url}")
        
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            
            # البحث عن جدول النتائج
            search_results = soup.find('table', {'id': 'search_results'})
            
            if not search_results:
                # محاولة طريقة بديلة
                search_results = soup.find_all('tr', class_='change')
            else:
                search_results = search_results.find_all('tr')[1:]  # تخطي الهيدر
            
            for row in search_results[:limit]:
                try:
                    # استخراج معلومات الترجمة
                    cells = row.find_all('td')
                    
                    if len(cells) < 5:
                        continue
                    
                    # العنوان والرابط
                    title_cell = cells[0] if cells else None
                    link = title_cell.find('a') if title_cell else None
                    
                    if not link:
                        # محاولة بديلة
                        link = row.find('a', href=re.compile(r'/en/subtitles/'))
                    
                    if link:
                        title = link.text.strip()
                        subtitle_url = self.base_url + link['href'] if not link['href'].startswith('http') else link['href']
                        
                        # معلومات إضافية
                        rating = None
                        downloads = None
                        
                        # محاولة استخراج التقييم
                        rating_cell = row.find('span', class_='rating')
                        if rating_cell:
                            rating = rating_cell.text.strip()
                        
                        results.append({
                            'title': title,
                            'url': subtitle_url,
                            'language': self.language_codes.get(language, language),
                            'language_code': language,
                            'rating': rating,
                            'downloads': downloads,
                        })
                        
                except Exception as e:
                    self.logger.debug(f"تخطي صف: {e}")
                    continue
            
            self.logger.info(f"✅ تم العثور على {len(results)} نتيجة")
            return results
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ خطأ في الاتصال: {e}")
            return []
        except Exception as e:
            self.logger.error(f"❌ خطأ في البحث: {e}")
            return []
    
    def get_download_link(self, page_url: str) -> Optional[str]:
        """
        استخراج رابط التحميل المباشر من صفحة الترجمة
        
        Args:
            page_url: رابط صفحة الترجمة
            
        Returns:
            رابط التحميل المباشر
        """
        try:
            self.logger.info(f"🔗 استخراج رابط التحميل من: {page_url}")
            
            response = self.session.get(page_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # البحث عن زر التحميل
            download_button = soup.find('a', {'id': 'bt-dwl-bt'})
            
            if download_button and download_button.get('href'):
                download_url = download_button['href']
                
                # التأكد من أن الرابط كامل
                if not download_url.startswith('http'):
                    download_url = self.base_url + download_url
                
                self.logger.info(f"✅ تم العثور على رابط التحميل")
                return download_url
            
            # طريقة بديلة
            download_link = soup.find('a', href=re.compile(r'/download/'))
            if download_link:
                download_url = download_link['href']
                if not download_url.startswith('http'):
                    download_url = self.base_url + download_url
                return download_url
            
            self.logger.warning(f"⚠️ لم يتم العثور على رابط التحميل")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في استخراج الرابط: {e}")
            return None
    
    def download(
        self, 
        subtitle_url: str, 
        output_dir: str = './subtitles',
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        تحميل ترجمة من OpenSubtitles
        
        Args:
            subtitle_url: رابط صفحة الترجمة
            output_dir: مجلد الحفظ
            filename: اسم الملف (اختياري)
            
        Returns:
            مسار الملف المحمل
        """
        try:
            # الحصول على رابط التحميل المباشر
            download_url = self.get_download_link(subtitle_url)
            
            if not download_url:
                self.logger.error("❌ فشل الحصول على رابط التحميل")
                return None
            
            # استخدام الـ Downloader للتحميل
            from ..core.downloader import SubtitleDownloader
            
            downloader = SubtitleDownloader(output_dir=output_dir)
            filepath = downloader.download(download_url, filename=filename)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في التحميل: {e}")
            return None
    
    def search_by_imdb(self, imdb_id: str, language: str = 'ara') -> List[Dict]:
        """
        البحث باستخدام IMDB ID
        
        Args:
            imdb_id: معرف IMDB (مثل: tt0133093)
            language: كود اللغة
            
        Returns:
            قائمة بالنتائج
        """
        # إزالة 'tt' إذا كان موجود
        clean_id = imdb_id.replace('tt', '')
        
        search_url = f"{self.base_url}/en/search/sublanguageid-{language}/imdbid-{clean_id}"
        
        self.logger.info(f"🔍 البحث بـ IMDB ID: {imdb_id}")
        
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            
            for row in soup.find_all('tr', class_='change')[:20]:
                try:
                    link = row.find('a', href=re.compile(r'/en/subtitles/'))
                    
                    if link:
                        title = link.text.strip()
                        subtitle_url = self.base_url + link['href']
                        
                        results.append({
                            'title': title,
                            'url': subtitle_url,
                            'language': self.language_codes.get(language, language),
                            'imdb_id': imdb_id,
                        })
                        
                except:
                    continue
            
            self.logger.info(f"✅ تم العثور على {len(results)} نتيجة")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ خطأ: {e}")
            return []