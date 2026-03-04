"""
Core subtitle downloader module
"""

import os
import requests
from tqdm import tqdm
from pathlib import Path
import logging
from typing import Optional, Dict, List
import time
from .config import Config

class SubtitleDownloader:
    """محرك تحميل الترجمات الأساسي"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        تهيئة المحمل
        
        Args:
            output_dir: مجلد الحفظ (اختياري)
        """
        self.output_dir = Path(output_dir) if output_dir else Config.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # إنشاء Session
        self.session = requests.Session()
        self.session.headers.update(Config.get_headers())
        
        # إعداد Logger
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """إعداد نظام السجلات"""
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
    
    def download(
        self, 
        url: str, 
        filename: Optional[str] = None,
        output_dir: Optional[str] = None,
        chunk_size: Optional[int] = None,
        show_progress: bool = True
    ) -> Optional[str]:
        """
        تحميل ملف ترجمة
        
        Args:
            url: رابط الملف
            filename: اسم الملف (اختياري)
            output_dir: مجلد الحفظ (اختياري)
            chunk_size: حجم القطعة للتحميل (اختياري)
            show_progress: عرض شريط التقدم
            
        Returns:
            مسار الملف المحمل أو None في حالة الفشل
        """
        if chunk_size is None:
            chunk_size = Config.CHUNK_SIZE
            
        try:
            self.logger.info(f"🔄 بدء التحميل من: {url}")
            
            # إرسال الطلب
            response = self.session.get(
                url, 
                stream=True, 
                timeout=Config.TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # تحديد اسم الملف
            if not filename:
                filename = self._extract_filename(response, url)
            
            # تحديد مسار الحفظ
            save_dir = Path(output_dir) if output_dir else self.output_dir
            save_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = save_dir / filename
            
            # الحصول على حجم الملف
            total_size = int(response.headers.get('content-length', 0))
            
            # التحميل
            downloaded = 0
            with open(filepath, 'wb') as f:
                if show_progress and total_size > 0:
                    with tqdm(
                        desc=f"📥 {filename}",
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        ncols=100,
                        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
                    ) as progress:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                size = f.write(chunk)
                                downloaded += size
                                progress.update(size)
                else:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
            
            # التحقق من التحميل
            if total_size > 0 and downloaded < total_size:
                self.logger.warning(f"⚠️ تحميل غير كامل: {downloaded}/{total_size} bytes")
            
            self.logger.info(f"✅ تم الحفظ في: {filepath}")
            return str(filepath)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ خطأ في الطلب: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ خطأ غير متوقع: {e}")
            return None
    
    def _extract_filename(self, response: requests.Response, url: str) -> str:
        """
        استخراج اسم الملف من الرد أو الرابط
        
        Args:
            response: استجابة HTTP
            url: الرابط الأصلي
            
        Returns:
            اسم الملف
        """
        # محاولة الحصول على الاسم من الـ headers
        content_disp = response.headers.get('content-disposition', '')
        if 'filename=' in content_disp:
            parts = content_disp.split('filename=')
            if len(parts) > 1:
                filename = parts[-1].strip('"\'')
                return filename
        
        # الحصول على الاسم من الرابط
        filename = url.split('/')[-1].split('?')[0]
        
        # التأكد من وجود امتداد
        if not any(filename.endswith(ext) for ext in Config.SUPPORTED_FORMATS):
            filename += '.srt'
        
        return filename
    
    def download_multiple(
        self, 
        urls: List[str], 
        output_dir: Optional[str] = None,
        delay: float = 1.0
    ) -> Dict[str, Optional[str]]:
        """
        تحميل عدة ملفات
        
        Args:
            urls: قائمة الروابط
            output_dir: مجلد الحفظ
            delay: التأخير بين التحميلات (بالثواني)
            
        Returns:
            قاموس {url: filepath}
        """
        results = {}
        total = len(urls)
        
        self.logger.info(f"📦 بدء تحميل {total} ملف...")
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"[{i}/{total}] معالجة: {url}")
            self.logger.info(f"{'='*50}")
            
            filepath = self.download(url, output_dir=output_dir)
            results[url] = filepath
            
            # تأخير بين التحميلات
            if i < total and delay > 0:
                time.sleep(delay)
        
        # إحصائيات
        successful = sum(1 for v in results.values() if v is not None)
        failed = total - successful
        
        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"✨ اكتمل التحميل")
        self.logger.info(f"✅ نجح: {successful}")
        self.logger.info(f"❌ فشل: {failed}")
        self.logger.info(f"{'='*50}")
        
        return results
    
    def verify_file(self, filepath: str) -> bool:
        """
        التحقق من سلامة الملف
        
        Args:
            filepath: مسار الملف
            
        Returns:
            True إذا كان الملف صحيح
        """
        try:
            path = Path(filepath)
            
            # التحقق من الوجود
            if not path.exists():
                self.logger.error(f"❌ الملف غير موجود: {filepath}")
                return False
            
            # التحقق من الحجم
            size = path.stat().st_size
            if size == 0:
                self.logger.warning(f"⚠️ الملف فارغ: {filepath}")
                return False
            
            # التحقق من الامتداد
            if path.suffix not in Config.SUPPORTED_FORMATS:
                self.logger.warning(f"⚠️ صيغة غير مدعومة: {path.suffix}")
            
            self.logger.info(f"✅ الملف صحيح - الحجم: {size/1024:.2f} KB")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في التحقق: {e}")
            return False
    
    def get_file_info(self, filepath: str) -> Optional[Dict]:
        """
        الحصول على معلومات الملف
        
        Args:
            filepath: مسار الملف
            
        Returns:
            قاموس بالمعلومات أو None
        """
        try:
            path = Path(filepath)
            
            if not path.exists():
                return None
            
            stat = path.stat()
            
            return {
                'name': path.name,
                'path': str(path.absolute()),
                'size_bytes': stat.st_size,
                'size_kb': stat.st_size / 1024,
                'size_mb': stat.st_size / (1024 * 1024),
                'extension': path.suffix,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في قراءة المعلومات: {e}")
            return None