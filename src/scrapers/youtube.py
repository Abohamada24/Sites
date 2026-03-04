%%writefile src/scrapers/youtube_fixed.py
"""
YouTube subtitle scraper - نسخة محسّنة
"""

import yt_dlp
from typing import List, Optional, Dict
from pathlib import Path
from .base_scraper import BaseScraper
import os
import re

class YouTubeScraper(BaseScraper):
    """تحميل الترجمات من يوتيوب - نسخة محسنة"""
    
    def __init__(self):
        super().__init__()
        self.ydl_opts_base = {
            'quiet': False,
            'no_warnings': False,
        }
    
    def get_available_subtitles(self, video_url: str) -> Dict:
        """الحصول على الترجمات المتاحة"""
        ydl_opts = {
            **self.ydl_opts_base,
            'skip_download': True,
            'listsubtitles': True,
        }
        
        try:
            self.logger.info(f"🔍 فحص الترجمات المتاحة...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                manual_subs = info.get('subtitles', {})
                auto_subs = info.get('automatic_captions', {})
                
                result = {
                    'title': info.get('title', 'Unknown'),
                    'manual': list(manual_subs.keys()),
                    'automatic': list(auto_subs.keys()),
                    'all': list(set(list(manual_subs.keys()) + list(auto_subs.keys())))
                }
                
                self.logger.info(f"📝 ترجمات يدوية: {len(result['manual'])}")
                self.logger.info(f"🤖 ترجمات تلقائية: {len(result['automatic'])}")
                
                return result
                
        except Exception as e:
            self.logger.error(f"❌ خطأ: {e}")
            return {}
    
    def download(
        self, 
        video_url: str, 
        output_dir: str = './subtitles',
        languages: Optional[List[str]] = None,
        auto_generated: bool = True,
        subtitle_format: str = 'srt'
    ) -> List[str]:
        """
        تحميل الترجمات - نسخة محسنة
        """
        if languages is None:
            languages = ['ar', 'en']
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # خيارات محسّنة
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,  # مهم جداً!
            'subtitleslangs': languages,
            'skip_download': True,
            'outtmpl': str(output_path / '%(title)s.%(ext)s'),
            'subtitlesformat': 'srt/best',  # محسّن
            'quiet': False,
            'no_warnings': False,
        }
        
        try:
            self.logger.info(f"📺 معالجة: {video_url}")
            self.logger.info(f"🌐 اللغات: {languages}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # التحميل
                info = ydl.extract_info(video_url, download=True)
                title = info.get('title', 'video')
                
                # تنظيف اسم الملف
                safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
                
                # البحث عن الملفات المحملة
                downloaded_files = []
                
                # البحث في المجلد
                for file in output_path.iterdir():
                    if file.suffix in ['.srt', '.vtt', '.en.srt', '.ar.srt']:
                        downloaded_files.append(str(file))
                
                # إذا لم يجد ملفات، جرب طرق بديلة
                if not downloaded_files:
                    self.logger.warning("⚠️ لم يتم العثور على ملفات بالطريقة العادية")
                    self.logger.info("🔄 محاولة طريقة بديلة...")
                    
                    # طريقة بديلة: تحميل يدوي
                    downloaded_files = self._download_subtitles_manual(
                        video_url, 
                        output_path, 
                        languages
                    )
                
                self.logger.info(f"✅ تم تحميل {len(downloaded_files)} ملف ترجمة")
                
                for f in downloaded_files:
                    self.logger.info(f"   📄 {Path(f).name}")
                
                return downloaded_files
                
        except Exception as e:
            self.logger.error(f"❌ خطأ: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _download_subtitles_manual(
        self, 
        video_url: str, 
        output_path: Path,
        languages: List[str]
    ) -> List[str]:
        """
        تحميل يدوي للترجمات (طريقة بديلة)
        """
        downloaded = []
        
        try:
            # الحصول على معلومات الفيديو
            ydl_opts = {'quiet': True, 'skip_download': True}
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                title = info.get('title', 'video')
                safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
                
                # الحصول على الترجمات
                auto_captions = info.get('automatic_captions', {})
                subtitles = info.get('subtitles', {})
                
                # دمج الاثنين
                all_subs = {**subtitles, **auto_captions}
                
                for lang in languages:
                    if lang in all_subs:
                        formats = all_subs[lang]
                        
                        # ابحث عن صيغة SRT
                        srt_format = None
                        for fmt in formats:
                            if fmt.get('ext') == 'srt':
                                srt_format = fmt
                                break
                        
                        # إذا لم يجد SRT، خذ أول صيغة
                        if not srt_format and formats:
                            srt_format = formats[0]
                        
                        if srt_format:
                            # تحميل الملف
                            import requests
                            url = srt_format.get('url')
                            
                            if url:
                                response = requests.get(url)
                                
                                # حفظ الملف
                                filename = f"{safe_title}.{lang}.srt"
                                filepath = output_path / filename
                                
                                with open(filepath, 'wb') as f:
                                    f.write(response.content)
                                
                                downloaded.append(str(filepath))
                                self.logger.info(f"   ✅ تم تحميل: {lang}")
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في التحميل اليدوي: {e}")
        
        return downloaded