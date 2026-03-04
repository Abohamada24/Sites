import requests
from tqdm import tqdm
import os

class SubtitleDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })
    
    def download_file(self, url, save_path, filename=None):
        """تحميل ملف الترجمة مع progress bar"""
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            # تحديد اسم الملف
            if not filename:
                filename = url.split('/')[-1]
            
            full_path = os.path.join(save_path, filename)
            
            # إنشاء المجلد إذا لم يكن موجود
            os.makedirs(save_path, exist_ok=True)
            
            # تحميل الملف
            total_size = int(response.headers.get('content-length', 0))
            
            with open(full_path, 'wb') as f, tqdm(
                desc=filename,
                total=total_size,
                unit='B',
                unit_scale=True
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    progress_bar.update(len(chunk))
            
            print(f"✅ تم الحفظ في: {full_path}")
            return full_path
            
        except Exception as e:
            print(f"❌ خطأ في التحميل: {e}")
            return None