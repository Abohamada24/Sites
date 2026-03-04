"""
YouTube subtitle scraper using yt-dlp
"""

import yt_dlp
from typing import List, Optional, Dict
from pathlib import Path
from .base_scraper import BaseScraper

class YouTubeScraper(BaseScraper):
    """تحميل الترجمات من يوتيوب"""
    
    def __init__(self):
        """تهيئة YouTube Scraper"""
        super().__init__()
        
        self.ydl_opts_base = {
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
        }
    
    def search(self, query: str, **kwargs) -> List[Dict]:
        """
        البحث عن فيديوهات في يوتيوب
        
        Args:
            query: نص البحث
            **kwargs: max_results (عدد النتائج)
            
        Returns:
            قائمة بالنتائج
        """
        max_results = kwargs.get('max_results', 5)
        search_url = f"ytsearch{max_results}:{query}"
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts_base) as ydl:
                search_results = ydl.extract_info(search_url, download=False)
                
                results = []
                if 'entries' in search_results:
                    for entry in search_results['entries']:
                        if entry:
                            results.append({
                                'title': entry.get('title', 'Unknown'),
                                'url': entry.get('webpage_url', ''),
                                'duration': entry.get('duration', 0),
                                'channel': entry.get('uploader', 'Unknown'),
                                'views': entry.get('view_count', 0),
                            })
                
                self.logger.info(f"✅ تم العثور على {len(results)} فيديو")
                return results
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في البحث: {e}")
            return []
    
    def get_available_subtitles(self, video_url: str) -> Dict:
        """
        الحصول على الترجمات المتاحة لفيديو
        
        Args:
            video_url: رابط الفيديو
            
        Returns:
            قاموس بالترجمات المتاحة
        """
        ydl_opts = {
            **self.ydl_opts_base,
            'skip_download': True,
            'listsubtitles': True,
        }
        
        try:
            self.logger.info(f"🔍 فحص الترجمات المتاحة...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                # الترجمات اليدوية
                manual_subs = info.get('subtitles', {})
                # الترجمات التلقائية
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
        تحميل الترجمات من فيديو يوتيوب
        
        Args:
            video_url: رابط الفيديو
            output_dir: مجلد الحفظ
            languages: قائمة اللغات (مثل: ['ar', 'en'])
            auto_generated: السماح بالترجمات التلقائية
            subtitle_format: صيغة الترجمة (srt, vtt, etc.)
            
        Returns:
            قائمة بمسارات الملفات المحملة
        """
        if languages is None:
            languages = ['ar', 'en']
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        ydl_opts = {
            **self.ydl_opts_base,
            'writesubtitles': True,
            'writeautomaticsub': auto_generated,
            'subtitleslangs': languages,
            'skip_download': True,
            'subtitlesformat': subtitle_format,
            'outtmpl': str(output_path / '%(title)s.%(ext)s'),
        }
        
        try:
            self.logger.info(f"📺 معالجة: {video_url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                title = info.get('title', 'video')
                
                # البحث عن الملفات المحملة
                downloaded_files = []
                
                # البحث عن جميع ملفات الترجمة
                for lang in languages:
                    for ext in [subtitle_format, 'vtt', 'srt']:
                        patterns = [
                            f"{title}.{lang}.{ext}",
                            f"{title}.{lang}-*.{ext}",
                        ]
                        
                        for pattern in patterns:
                            files = list(output_path.glob(pattern))
                            downloaded_files.extend(files)
                
                # إزالة التكرار
                downloaded_files = list(set(downloaded_files))
                
                self.logger.info(f"✅ تم تحميل {len(downloaded_files)} ملف ترجمة")
                
                for f in downloaded_files:
                    self.logger.info(f"   📄 {f.name}")
                
                return [str(f) for f in downloaded_files]
                
        except Exception as e:
            self.logger.error(f"❌ خطأ: {e}")
            return []
    
    def download_video_with_subtitles(
        self,
        video_url: str,
        output_dir: str = './downloads',
        languages: Optional[List[str]] = None,
        quality: str = 'best'
    ) -> Optional[str]:
        """
        تحميل الفيديو مع الترجمات مدمجة
        
        Args:
            video_url: رابط الفيديو
            output_dir: مجلد الحفظ
            languages: قائمة اللغات
            quality: جودة الفيديو
            
        Returns:
            مسار ملف الفيديو
        """
        if languages is None:
            languages = ['ar', 'en']
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        ydl_opts = {
            'format': quality,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': languages,
            'outtmpl': str(output_path / '%(title)s.%(ext)s'),
        }
        
        try:
            self.logger.info(f"📥 تحميل الفيديو مع الترجمات...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                filename = ydl.prepare_filename(info)
                
                self.logger.info(f"✅ تم الحفظ: {filename}")
                return filename
                
        except Exception as e:
            self.logger.error(f"❌ خطأ: {e}")
            return None