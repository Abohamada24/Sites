"""
File handling utilities
"""

import os
import zipfile
import shutil
from pathlib import Path
from typing import List, Optional
import pysubs2

class FileHandler:
    """معالج الملفات"""
    
    @staticmethod
    def extract_zip(zip_path: str, extract_to: str = './') -> List[str]:
        """
        فك ضغط ملف ZIP
        
        Args:
            zip_path: مسار ملف ZIP
            extract_to: مجلد الاستخراج
            
        Returns:
            قائمة بالملفات المستخرجة
        """
        extracted_files = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
                extracted_files = zip_ref.namelist()
            
            print(f"✅ تم استخراج {len(extracted_files)} ملف")
            return [os.path.join(extract_to, f) for f in extracted_files]
            
        except Exception as e:
            print(f"❌ خطأ في فك الضغط: {e}")
            return []
    
    @staticmethod
    def convert_subtitle(
        input_path: str, 
        output_format: str = 'srt',
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        تحويل صيغة ملف الترجمة
        
        Args:
            input_path: مسار الملف الأصلي
            output_format: الصيغة المطلوبة (srt, ass, vtt, etc.)
            output_path: مسار الحفظ (اختياري)
            
        Returns:
            مسار الملف المحول
        """
        try:
            # قراءة الملف
            subs = pysubs2.load(input_path)
            
            # تحديد مسار الحفظ
            if not output_path:
                input_file = Path(input_path)
                output_path = str(input_file.with_suffix(f'.{output_format}'))
            
            # الحفظ بالصيغة الجديدة
            subs.save(output_path)
            
            print(f"✅ تم التحويل إلى: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ خطأ في التحويل: {e}")
            return None
    
    @staticmethod
    def merge_subtitles(
        subtitle_paths: List[str],
        output_path: str,
        separator: str = '\n---\n'
    ) -> Optional[str]:
        """
        دمج عدة ملفات ترجمة
        
        Args:
            subtitle_paths: قائمة مسارات الملفات
            output_path: مسار الملف الناتج
            separator: الفاصل بين الترجمات
            
        Returns:
            مسار الملف المدمج
        """
        try:
            all_subs = []
            
            for path in subtitle_paths:
                subs = pysubs2.load(path)
                all_subs.append(subs)
            
            # دمج الترجمات
            merged = all_subs[0]
            for subs in all_subs[1:]:
                merged.events.extend(subs.events)
            
            # ترتيب حسب الوقت
            merged.sort()
            
            # الحفظ
            merged.save(output_path)
            
            print(f"✅ تم دمج {len(subtitle_paths)} ملف")
            return output_path
            
        except Exception as e:
            print(f"❌ خطأ في الدمج: {e}")
            return None
    
    @staticmethod
    def clean_subtitle(
        input_path: str,
        output_path: Optional[str] = None,
        remove_ads: bool = True,
        remove_html: bool = True
    ) -> Optional[str]:
        """
        تنظيف ملف الترجمة
        
        Args:
            input_path: مسار الملف
            output_path: مسار الحفظ
            remove_ads: إزالة الإعلانات
            remove_html: إزالة وسوم HTML
            
        Returns:
            مسار الملف المنظف
        """
        try:
            import re
            
            subs = pysubs2.load(input_path)
            
            ad_patterns = [
                r'.*www\..*',
                r'.*http.*',
                r'.*\.com.*',
                r'.*subscribe.*',
                r'.*تابعونا.*',
                r'.*ترجمة.*',
            ]
            
            cleaned_events = []
            
            for event in subs.events:
                text = event.text
                
                # إزالة HTML
                if remove_html:
                    text = re.sub(r'<[^>]+>', '', text)
                
                # إزالة الإعلانات
                if remove_ads:
                    is_ad = False
                    for pattern in ad_patterns:
                        if re.search(pattern, text, re.IGNORECASE):
                            is_ad = True
                            break
                    
                    if is_ad:
                        continue
                
                event.text = text.strip()
                if event.text:  # فقط إذا كان النص غير فارغ
                    cleaned_events.append(event)
            
            subs.events = cleaned_events
            
            # تحديد مسار الحفظ
            if not output_path:
                input_file = Path(input_path)
                output_path = str(input_file.with_stem(f'{input_file.stem}_cleaned'))
            
            subs.save(output_path)
            
            print(f"✅ تم التنظيف: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ خطأ في التنظيف: {e}")
            return None
    
    @staticmethod
    def get_subtitle_info(subtitle_path: str) -> Optional[dict]:
        """
        الحصول على معلومات ملف الترجمة
        
        Args:
            subtitle_path: مسار الملف
            
        Returns:
            قاموس بالمعلومات
        """
        try:
            subs = pysubs2.load(subtitle_path)
            
            total_lines = len(subs.events)
            duration = subs.events[-1].end / 1000 if subs.events else 0  # بالثواني
            
            return {
                'path': subtitle_path,
                'format': Path(subtitle_path).suffix,
                'total_lines': total_lines,
                'duration_seconds': duration,
                'duration_minutes': duration / 60,
                'first_line': subs.events[0].text if subs.events else '',
                'last_line': subs.events[-1].text if subs.events else '',
            }
            
        except Exception as e:
            print(f"❌ خطأ في قراءة الملف: {e}")
            return None