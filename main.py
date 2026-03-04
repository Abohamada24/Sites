#!/usr/bin/env python3
"""
Sites - Subtitle Downloader
Main CLI Application

Author: Ahmed Abohamada
GitHub: https://github.com/Abohamada24/Sites
"""

import argparse
import sys
from pathlib import Path

# إضافة المجلد الحالي للـ path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.downloader import SubtitleDownloader
from src.core.config import Config
from src.scrapers.opensubtitles import OpenSubtitlesScraper
from src.scrapers.subscene import SubsceneScraper
from src.scrapers.youtube import YouTubeScraper
from src.utils.file_handler import FileHandler
from src.utils.logger import setup_logger

# إعداد Logger
logger = setup_logger('Main')

def print_banner():
    """طباعة شعار البرنامج"""
    banner = """
    ╔═══════════════════════════════════════╗
    ║   🎬 Sites - Subtitle Downloader 🎬   ║
    ║                                       ║
    ║   Author: Ahmed Abohamada             ║
    ║   Version: 1.0.0                      ║
    ╚═══════════════════════════════════════╝
    """
    print(banner)

def cmd_search(args):
    """أمر البحث عن ترجمات"""
    print_banner()
    logger.info(f"🔍 البحث عن: {args.query}")
    
    # اختيار المصدر
    if args.source == 'opensubtitles':
        scraper = OpenSubtitlesScraper()
        results = scraper.search(args.query, language=args.lang, limit=args.limit)
    elif args.source == 'subscene':
        scraper = SubsceneScraper()
        results = scraper.search(args.query, language=args.lang, limit=args.limit)
    elif args.source == 'youtube':
        scraper = YouTubeScraper()
        results = scraper.search(args.query, max_results=args.limit)
    else:
        logger.error(f"❌ مصدر غير مدعوم: {args.source}")
        return
    
    # عرض النتائج
    if results:
        print(f"\n📋 تم العثور على {len(results)} نتيجة:\n")
        print("="*80)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   🔗 {result['url']}")
            if 'language' in result:
                print(f"   🌐 {result['language']}")
            if 'rating' in result and result['rating']:
                print(f"   ⭐ {result['rating']}")
        
        print("\n" + "="*80)
        
        # حفظ النتائج
        if args.save:
            import json
            output_file = f"search_results_{args.query.replace(' ', '_')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 تم حفظ النتائج في: {output_file}")
    else:
        logger.warning("❌ لم يتم العثور على نتائج")

def cmd_download(args):
    """أمر التحميل المباشر"""
    print_banner()
    logger.info(f"⬇️ التحميل من: {args.url}")
    
    # إنشاء المحمل
    downloader = SubtitleDownloader(output_dir=args.output)
    
    # التحميل
    filepath = downloader.download(
        args.url,
        filename=args.filename,
        show_progress=not args.quiet
    )
    
    if filepath:
        logger.info(f"\n✅ تم التحميل بنجاح!")
        logger.info(f"📁 الملف: {filepath}")
        
        # معلومات الملف
        if args.info:
            info = FileHandler.get_subtitle_info(filepath)
            if info:
                print(f"\n📊 معلومات الملف:")
                print(f"   - عدد الأسطر: {info['total_lines']}")
                print(f"   - المدة: {info['duration_minutes']:.2f} دقيقة")
    else:
        logger.error("\n❌ فشل التحميل")

def cmd_youtube(args):
    """أمر تحميل من يوتيوب"""
    print_banner()
    logger.info(f"📺 معالجة فيديو يوتيوب...")
    
    scraper = YouTubeScraper()
    
    # تحويل اللغات من نص إلى قائمة
    languages = [lang.strip() for lang in args.lang.split(',')]
    
    # عرض الترجمات المتاحة
    if args.list:
        info = scraper.get_available_subtitles(args.url)
        if info:
            print(f"\n📺 الفيديو: {info['title']}")
            print(f"\n📝 ترجمات يدوية ({len(info['manual'])}):")
            for lang in info['manual']:
                print(f"   - {lang}")
            print(f"\n🤖 ترجمات تلقائية ({len(info['automatic'])}):")
            for lang in info['automatic'][:10]:  # أول 10 فقط
                print(f"   - {lang}")
        return
    
    # تحميل الترجمات
    files = scraper.download(
        args.url,
        output_dir=args.output,
        languages=languages,
        auto_generated=args.auto,
        subtitle_format=args.format
    )
    
    if files:
        logger.info(f"\n✅ تم تحميل {len(files)} ملف ترجمة:")
        for f in files:
            logger.info(f"   📄 {f}")
    else:
        logger.warning("\n❌ لم يتم العثور على ترجمات")

def cmd_convert(args):
    """أمر تحويل صيغة الترجمة"""
    print_banner()
    logger.info(f"🔄 تحويل: {args.input}")
    
    output = FileHandler.convert_subtitle(
        args.input,
        output_format=args.format,
        output_path=args.output
    )
    
    if output:
        logger.info(f"✅ تم التحويل إلى: {output}")
    else:
        logger.error("❌ فشل التحويل")

def cmd_clean(args):
    """أمر تنظيف الترجمة"""
    print_banner()
    logger.info(f"🧹 تنظيف: {args.input}")
    
    output = FileHandler.clean_subtitle(
        args.input,
        output_path=args.output,
        remove_ads=args.ads,
        remove_html=args.html
    )
    
    if output:
        logger.info(f"✅ تم التنظيف: {output}")
    else:
        logger.error("❌ فشل التنظيف")

def cmd_info(args):
    """أمر عرض معلومات الترجمة"""
    print_banner()
    logger.info(f"ℹ️ معلومات الملف: {args.file}")
    
    info = FileHandler.get_subtitle_info(args.file)
    
    if info:
        print(f"\n📊 معلومات الترجمة:")
        print(f"   📁 الملف: {info['path']}")
        print(f"   📝 الصيغة: {info['format']}")
        print(f"   📏 عدد الأسطر: {info['total_lines']}")
        print(f"   ⏱️  المدة: {info['duration_minutes']:.2f} دقيقة")
        print(f"   📄 أول سطر: {info['first_line'][:50]}...")
        print(f"   📄 آخر سطر: {info['last_line'][:50]}...")
    else:
        logger.error("❌ فشل قراءة الملف")

def main():
    """الدالة الرئيسية"""
    
    # إنشاء المحلل الرئيسي
    parser = argparse.ArgumentParser(
        description='🎬 Sites - أداة تحميل وإدارة ملفات الترجمة',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
أمثلة الاستخدام:
  
  البحث:
    %(prog)s search "Inception" --source opensubtitles --lang ara
    %(prog)s search "Breaking Bad S01E01" --source subscene
  
  التحميل:
    %(prog)s download "https://example.com/subtitle.srt"
    %(prog)s download "URL" --output ./my_subs --filename custom.srt
  
  يوتيوب:
    %(prog)s youtube "https://youtube.com/watch?v=xxxxx" --lang ar,en
    %(prog)s youtube "URL" --list  # عرض الترجمات المتاحة
  
  التحويل والتنظيف:
    %(prog)s convert input.vtt --format srt
    %(prog)s clean input.srt --ads --html
    %(prog)s info subtitle.srt
        """
    )
    
    # إنشاء Subparsers
    subparsers = parser.add_subparsers(dest='command', help='الأوامر المتاحة')
    
    # ========== أمر البحث ==========
    search_parser = subparsers.add_parser('search', help='البحث عن ترجمات')
    search_parser.add_argument('query', help='اسم الفيلم أو المسلسل')
    search_parser.add_argument('--source', 
                              default='opensubtitles',
                              choices=['opensubtitles', 'subscene', 'youtube'],
                              help='مصدر البحث')
    search_parser.add_argument('--lang', default='ara', help='كود اللغة (ara, eng, etc.)')
    search_parser.add_argument('--limit', type=int, default=10, help='عدد النتائج')
    search_parser.add_argument('--save', action='store_true', help='حفظ النتائج في ملف JSON')
    search_parser.set_defaults(func=cmd_search)
    
    # ========== أمر التحميل ==========
    download_parser = subparsers.add_parser('download', help='تحميل ترجمة مباشرة')
    download_parser.add_argument('url', help='رابط الملف')
    download_parser.add_argument('--output', default='./subtitles', help='مجلد الحفظ')
    download_parser.add_argument('--filename', help='اسم الملف (اختياري)')
    download_parser.add_argument('--quiet', action='store_true', help='بدون progress bar')
    download_parser.add_argument('--info', action='store_true', help='عرض معلومات الملف')
    download_parser.set_defaults(func=cmd_download)
    
    # ========== أمر يوتيوب ==========
    youtube_parser = subparsers.add_parser('youtube', help='تحميل من يوتيوب')
    youtube_parser.add_argument('url', help='رابط الفيديو')
    youtube_parser.add_argument('--lang', default='ar,en', help='اللغات (مفصولة بفاصلة)')
    youtube_parser.add_argument('--output', default='./subtitles', help='مجلد الحفظ')
    youtube_parser.add_argument('--format', default='srt', choices=['srt', 'vtt'], help='صيغة الترجمة')
    youtube_parser.add_argument('--auto', action='store_true', help='تضمين الترجمات التلقائية')
    youtube_parser.add_argument('--list', action='store_true', help='عرض الترجمات المتاحة فقط')
    youtube_parser.set_defaults(func=cmd_youtube)
    
    # ========== أمر التحويل ==========
    convert_parser = subparsers.add_parser('convert', help='تحويل صيغة الترجمة')
    convert_parser.add_argument('input', help='ملف الإدخال')
    convert_parser.add_argument('--format', default='srt', 
                               choices=['srt', 'ass', 'vtt', 'ssa'],
                               help='الصيغة المطلوبة')
    convert_parser.add_argument('--output', help='ملف الإخراج (اختياري)')
    convert_parser.set_defaults(func=cmd_convert)
    
    # ========== أمر التنظيف ==========
    clean_parser = subparsers.add_parser('clean', help='تنظيف ملف الترجمة')
    clean_parser.add_argument('input', help='ملف الإدخال')
    clean_parser.add_argument('--output', help='ملف الإخراج (اختياري)')
    clean_parser.add_argument('--ads', action='store_true', help='إزالة الإعلانات')
    clean_parser.add_argument('--html', action='store_true', help='إزالة وسوم HTML')
    clean_parser.set_defaults(func=cmd_clean)
    
    # ========== أمر المعلومات ==========
    info_parser = subparsers.add_parser('info', help='عرض معلومات ملف الترجمة')
    info_parser.add_argument('file', help='ملف الترجمة')
    info_parser.set_defaults(func=cmd_info)
    
    # تحليل الأوامر
    args = parser.parse_args()
    
    # إذا لم يتم تحديد أمر
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    # تنفيذ الأمر
    try:
        Config.ensure_directories()
        args.func(args)
    except KeyboardInterrupt:
        print("\n\n⚠️ تم الإلغاء بواسطة المستخدم")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()