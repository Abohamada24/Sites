%%writefile interactive.py
#!/usr/bin/env python3
"""
🎬 Sites - Interactive Subtitle Downloader
واجهة تفاعلية متكاملة للبحث والتحميل التلقائي

Author: Ahmed Abohamada
GitHub: https://github.com/Abohamada24/Sites
"""

import os
import sys
import re
import time
from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import urlparse

# إضافة المسار
sys.path.insert(0, str(Path(__file__).parent))

from src.core.downloader import SubtitleDownloader
from src.core.config import Config
from src.scrapers.youtube import YouTubeScraper
from src.scrapers.opensubtitles import OpenSubtitlesScraper
from src.scrapers.subscene import SubsceneScraper
from src.utils.file_handler import FileHandler


class InteractiveDownloader:
    """
    🎬 واجهة تفاعلية متكاملة
    تربط جميع الوظائف وتعمل تلقائياً
    """
    
    def __init__(self, output_dir: str = "./subtitles"):
        """تهيئة الواجهة"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # تهيئة المكونات
        self.downloader = SubtitleDownloader(output_dir=str(self.output_dir))
        self.youtube = YouTubeScraper()
        self.opensubtitles = OpenSubtitlesScraper()
        self.subscene = SubsceneScraper()
        
        # الإعدادات الافتراضية
        self.default_languages = ['ar', 'ara', 'Arabic']
        self.auto_download = True
        self.auto_clean = True
        
        print(self._get_banner())
    
    def _get_banner(self) -> str:
        """شعار البرنامج"""
        return """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🎬  Sites - Interactive Subtitle Downloader  🎬           ║
║                                                              ║
║   📥 البحث والتحميل التلقائي للترجمات                       ║
║   🌐 يدعم: YouTube, OpenSubtitles, Subscene                 ║
║   🔗 فقط أدخل الرابط أو اسم الفيلم!                         ║
║                                                              ║
║   👨‍💻 By: Ahmed Abohamada                                    ║
╚══════════════════════════════════════════════════════════════╝
        """
    
    def detect_input_type(self, user_input: str) -> Dict:
        """
        🔍 اكتشاف نوع المدخل تلقائياً
        
        Returns:
            {
                'type': 'youtube' | 'direct_link' | 'movie_name' | 'imdb',
                'value': str,
                'details': dict
            }
        """
        user_input = user_input.strip()
        
        # 1. رابط يوتيوب
        youtube_patterns = [
            r'(youtube\.com/watch\?v=)',
            r'(youtu\.be/)',
            r'(youtube\.com/embed/)',
            r'(youtube\.com/v/)',
        ]
        
        for pattern in youtube_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return {
                    'type': 'youtube',
                    'value': user_input,
                    'details': {'platform': 'YouTube'}
                }
        
        # 2. رابط مباشر لملف ترجمة
        subtitle_extensions = ['.srt', '.vtt', '.ass', '.ssa', '.sub']
        if any(ext in user_input.lower() for ext in subtitle_extensions):
            return {
                'type': 'direct_link',
                'value': user_input,
                'details': {'file_type': 'subtitle'}
            }
        
        # 3. رابط عام (http/https)
        if user_input.startswith(('http://', 'https://')):
            # تحقق إذا كان رابط OpenSubtitles أو Subscene
            if 'opensubtitles' in user_input.lower():
                return {
                    'type': 'opensubtitles_link',
                    'value': user_input,
                    'details': {'source': 'OpenSubtitles'}
                }
            elif 'subscene' in user_input.lower():
                return {
                    'type': 'subscene_link',
                    'value': user_input,
                    'details': {'source': 'Subscene'}
                }
            else:
                return {
                    'type': 'direct_link',
                    'value': user_input,
                    'details': {'file_type': 'unknown'}
                }
        
        # 4. IMDB ID
        imdb_pattern = r'^tt\d{7,}$'
        if re.match(imdb_pattern, user_input, re.IGNORECASE):
            return {
                'type': 'imdb',
                'value': user_input,
                'details': {'imdb_id': user_input}
            }
        
        # 5. اسم فيلم/مسلسل
        return {
            'type': 'movie_name',
            'value': user_input,
            'details': {'search_query': user_input}
        }
    
    def process(self, user_input: str, language: str = 'ara') -> List[str]:
        """
        🚀 المعالجة الرئيسية - البحث والتحميل التلقائي
        
        Args:
            user_input: رابط أو اسم فيلم
            language: اللغة المطلوبة
            
        Returns:
            قائمة بالملفات المحملة
        """
        print(f"\n{'='*60}")
        print(f"📝 المدخل: {user_input}")
        print(f"🌐 اللغة: {language}")
        print(f"{'='*60}\n")
        
        # اكتشاف نوع المدخل
        detected = self.detect_input_type(user_input)
        
        print(f"🔍 تم اكتشاف النوع: {detected['type']}")
        print(f"📋 التفاصيل: {detected['details']}\n")
        
        downloaded_files = []
        
        # معالجة حسب النوع
        if detected['type'] == 'youtube':
            downloaded_files = self._process_youtube(detected['value'], language)
        
        elif detected['type'] == 'direct_link':
            downloaded_files = self._process_direct_link(detected['value'])
        
        elif detected['type'] == 'opensubtitles_link':
            downloaded_files = self._process_opensubtitles_link(detected['value'])
        
        elif detected['type'] == 'subscene_link':
            downloaded_files = self._process_subscene_link(detected['value'])
        
        elif detected['type'] == 'imdb':
            downloaded_files = self._process_imdb(detected['value'], language)
        
        elif detected['type'] == 'movie_name':
            downloaded_files = self._process_movie_name(detected['value'], language)
        
        # التنظيف التلقائي
        if self.auto_clean and downloaded_files:
            downloaded_files = self._auto_clean_files(downloaded_files)
        
        # عرض النتائج النهائية
        self._show_results(downloaded_files)
        
        return downloaded_files
    
    def _process_youtube(self, url: str, language: str) -> List[str]:
        """معالجة رابط يوتيوب"""
        print("📺 معالجة رابط يوتيوب...\n")
        
        # تحويل كود اللغة
        lang_codes = self._normalize_language(language)
        
        try:
            # 1. فحص الترجمات المتاحة
            print("🔍 فحص الترجمات المتاحة...")
            subs_info = self.youtube.get_available_subtitles(url)
            
            if subs_info:
                print(f"   🎬 الفيديو: {subs_info.get('title', 'Unknown')}")
                print(f"   📝 ترجمات يدوية: {subs_info.get('manual', [])}")
                print(f"   🤖 ترجمات تلقائية: {subs_info.get('automatic', [])[:5]}...")
            
            # 2. تحميل الترجمات
            print(f"\n📥 تحميل الترجمات ({', '.join(lang_codes)})...")
            
            files = self.youtube.download(
                url,
                output_dir=str(self.output_dir / 'youtube'),
                languages=lang_codes,
                auto_generated=True,
                subtitle_format='srt'
            )
            
            return files
            
        except Exception as e:
            print(f"❌ خطأ في معالجة يوتيوب: {e}")
            return []
    
    def _process_direct_link(self, url: str) -> List[str]:
        """معالجة رابط مباشر"""
        print("🔗 تحميل من رابط مباشر...\n")
        
        try:
            filepath = self.downloader.download(
                url,
                output_dir=str(self.output_dir / 'direct')
            )
            
            return [filepath] if filepath else []
            
        except Exception as e:
            print(f"❌ خطأ في التحميل: {e}")
            return []
    
    def _process_opensubtitles_link(self, url: str) -> List[str]:
        """معالجة رابط OpenSubtitles"""
        print("🌐 معالجة رابط OpenSubtitles...\n")
        
        try:
            filepath = self.opensubtitles.download(
                url,
                output_dir=str(self.output_dir / 'opensubtitles')
            )
            
            return [filepath] if filepath else []
            
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return []
    
    def _process_subscene_link(self, url: str) -> List[str]:
        """معالجة رابط Subscene"""
        print("🌐 معالجة رابط Subscene...\n")
        
        try:
            filepath = self.subscene.download(
                url,
                output_dir=str(self.output_dir / 'subscene')
            )
            
            return [filepath] if filepath else []
            
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return []
    
    def _process_imdb(self, imdb_id: str, language: str) -> List[str]:
        """معالجة IMDB ID"""
        print(f"🎬 البحث بـ IMDB ID: {imdb_id}...\n")
        
        return self._search_and_download(
            query=None,
            imdb_id=imdb_id,
            language=language
        )
    
    def _process_movie_name(self, name: str, language: str) -> List[str]:
        """معالجة اسم الفيلم"""
        print(f"🎬 البحث عن: {name}...\n")
        
        return self._search_and_download(
            query=name,
            imdb_id=None,
            language=language
        )
    
    def _search_and_download(
        self, 
        query: Optional[str], 
        imdb_id: Optional[str],
        language: str
    ) -> List[str]:
        """البحث والتحميل من مصادر متعددة"""
        
        all_results = []
        downloaded_files = []
        
        # 1. البحث في OpenSubtitles
        print("🔍 البحث في OpenSubtitles...")
        try:
            if imdb_id:
                results = self.opensubtitles.search_by_imdb(imdb_id, language=language)
            else:
                results = self.opensubtitles.search(query, language=language, limit=10)
            
            if results:
                print(f"   ✅ تم العثور على {len(results)} نتيجة")
                all_results.extend([('opensubtitles', r) for r in results])
            else:
                print("   ⚠️ لم يتم العثور على نتائج")
                
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
        
        # 2. البحث في Subscene
        print("\n🔍 البحث في Subscene...")
        try:
            lang_name = self._get_language_name(language)
            results = self.subscene.search(query or imdb_id, language=lang_name, limit=10)
            
            if results:
                print(f"   ✅ تم العثور على {len(results)} نتيجة")
                all_results.extend([('subscene', r) for r in results])
            else:
                print("   ⚠️ لم يتم العثور على نتائج")
                
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
        
        # 3. عرض النتائج
        if not all_results:
            print("\n❌ لم يتم العثور على أي نتائج!")
            return []
        
        print(f"\n{'='*60}")
        print(f"📋 إجمالي النتائج: {len(all_results)}")
        print(f"{'='*60}\n")
        
        # 4. التحميل التلقائي
        print("📥 التحميل التلقائي لأفضل النتائج...\n")
        
        for i, (source, result) in enumerate(all_results[:3], 1):
            print(f"\n[{i}/3] تحميل: {result['title'][:50]}...")
            
            try:
                if source == 'opensubtitles':
                    filepath = self.opensubtitles.download(
                        result['url'],
                        output_dir=str(self.output_dir / 'opensubtitles')
                    )
                else:
                    filepath = self.subscene.download(
                        result['url'],
                        output_dir=str(self.output_dir / 'subscene')
                    )
                
                if filepath:
                    downloaded_files.append(filepath)
                    print(f"   ✅ تم التحميل")
                
                # تأخير بسيط
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ فشل: {e}")
        
        return downloaded_files
    
    def _auto_clean_files(self, files: List[str]) -> List[str]:
        """تنظيف تلقائي للملفات"""
        
        print(f"\n🧹 تنظيف تلقائي لـ {len(files)} ملف...\n")
        
        cleaned_files = []
        
        for filepath in files:
            if filepath and os.path.exists(filepath):
                try:
                    cleaned = FileHandler.clean_subtitle(
                        filepath,
                        remove_ads=True,
                        remove_html=True
                    )
                    
                    if cleaned:
                        cleaned_files.append(cleaned)
                        print(f"   ✅ تم تنظيف: {Path(filepath).name}")
                    else:
                        cleaned_files.append(filepath)
                        
                except Exception as e:
                    cleaned_files.append(filepath)
                    print(f"   ⚠️ تخطي التنظيف: {e}")
        
        return cleaned_files
    
    def _show_results(self, files: List[str]):
        """عرض النتائج النهائية"""
        
        print(f"\n{'='*60}")
        print("📊 النتائج النهائية")
        print(f"{'='*60}\n")
        
        if not files:
            print("❌ لم يتم تحميل أي ملفات")
            return
        
        valid_files = [f for f in files if f and os.path.exists(f)]
        
        print(f"✅ تم تحميل {len(valid_files)} ملف:\n")
        
        total_size = 0
        
        for i, filepath in enumerate(valid_files, 1):
            path = Path(filepath)
            size = path.stat().st_size / 1024  # KB
            total_size += size
            
            print(f"   {i}. 📄 {path.name}")
            print(f"      📍 {filepath}")
            print(f"      📊 {size:.2f} KB\n")
        
        print(f"{'='*60}")
        print(f"📊 الإجمالي: {len(valid_files)} ملف ({total_size:.2f} KB)")
        print(f"📁 مجلد الحفظ: {self.output_dir}")
        print(f"{'='*60}\n")
    
    def _normalize_language(self, language: str) -> List[str]:
        """تحويل اللغة لصيغة مناسبة"""
        
        lang_map = {
            'ara': ['ar', 'ara', 'Arabic'],
            'ar': ['ar', 'ara', 'Arabic'],
            'arabic': ['ar', 'ara', 'Arabic'],
            'العربية': ['ar', 'ara', 'Arabic'],
            'eng': ['en', 'eng', 'English'],
            'en': ['en', 'eng', 'English'],
            'english': ['en', 'eng', 'English'],
        }
        
        return lang_map.get(language.lower(), [language])
    
    def _get_language_name(self, code: str) -> str:
        """الحصول على اسم اللغة"""
        
        names = {
            'ara': 'Arabic',
            'ar': 'Arabic',
            'eng': 'English',
            'en': 'English',
        }
        
        return names.get(code.lower(), code)


# =========================================
# 🚀 دالة سريعة للاستخدام المباشر
# =========================================

def quick_download(input_value: str, language: str = 'ara', output_dir: str = './subtitles'):
    """
    ⚡ تحميل سريع - دالة واحدة للكل
    
    Args:
        input_value: رابط يوتيوب، رابط مباشر، أو اسم فيلم
        language: اللغة (ara, eng)
        output_dir: مجلد الحفظ
        
    Returns:
        قائمة الملفات المحملة
        
    Example:
        files = quick_download("Inception", "ara")
        files = quick_download("https://youtube.com/watch?v=xxx")
    """
    
    downloader = InteractiveDownloader(output_dir=output_dir)
    return downloader.process(input_value, language=language)


# =========================================
# 🎯 التشغيل الرئيسي
# =========================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='🎬 Sites - Interactive Subtitle Downloader')
    parser.add_argument('input', nargs='?', help='رابط أو اسم فيلم')
    parser.add_argument('--lang', '-l', default='ara', help='اللغة (ara/eng)')
    parser.add_argument('--output', '-o', default='./subtitles', help='مجلد الحفظ')
    
    args = parser.parse_args()
    
    if args.input:
        # تحميل مباشر
        quick_download(args.input, language=args.lang, output_dir=args.output)
    else:
        print("⚠️ الرجاء إدخال رابط أو اسم فيلم")
        print("مثال: python interactive.py 'Inception' --lang ara")