#!/usr/bin/env python3
"""
🎬 Sites - Google Colab Subtitle Downloader
واجهة تفاعلية متكاملة للتحميل على Google Colab

Author: Ahmed Abohamada
GitHub: https://github.com/Abohamada24/Sites
"""

import requests
import os
from pathlib import Path
from typing import Optional, Dict, List
import json

# ==================== OpenSubtitles API Class ====================

class OpenSubtitles:
    """فئة للتعامل مع واجهة OpenSubtitles API"""
    
    def __init__(self, username: str = "", password: str = ""):
        self.api_url = 'https://api.opensubtitles.org/xml-rpc'
        self.token = None
        if username and password:
            self.login(username, password)
    
    def login(self, username: str, password: str) -> bool:
        """تسجيل الدخول"""
        try:
            headers = {'Content-Type': 'application/xml'}
            data = {
                'jsonrpc': '2.0',
                'method': 'LogIn',
                'params': [username, password, 'en', 'OSTestUserAgent'],
                'id': 1
            }
            response = requests.post(self.api_url, json=data, headers=headers, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and 'token' in result['result']:
                    self.token = result['result']['token']
                    return True
        except Exception as e:
            print(f"❌ خطأ في التسجيل: {e}")
        return False
    
    def search_subtitles(self, query: str, language: str = 'ara') -> List[Dict]:
        """البحث عن الترجمات"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.token}' if self.token else ''
            }
            data = {
                'jsonrpc': '2.0',
                'method': 'SearchSubtitles',
                'params': [self.token or '', [{'query': query, 'sublanguageid': language}]],
                'id': 1
            }
            response = requests.post(self.api_url, json=data, headers=headers, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    return result['result']
        except Exception as e:
            print(f"❌ خطأ في البحث: {e}")
        return []
    
    def download_subtitle(self, subtitle_id: str, output_path: str) -> bool:
        """تحميل الترجمة"""
        try:
            download_url = f'https://dl.opensubtitles.org/en/download/sub/{subtitle_id}'
            response = requests.get(download_url, timeout=10)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"❌ خطأ في التحميل: {e}")
        return False
    
    def logout(self):
        """تسجيل الخروج"""
        if self.token:
            try:
                headers = {'Content-Type': 'application/json'}
                data = {
                    'jsonrpc': '2.0',
                    'method': 'LogOut',
                    'params': [self.token],
                    'id': 1
                }
                requests.post(self.api_url, json=data, headers=headers, timeout=10)
            except:
                pass
            self.token = None


# ==================== Colab UI Class ====================

class ColabSubtitleDownloader:
    """واجهة Google Colab التفاعلية"""
    
    def __init__(self, output_dir: str = "./subtitles"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.os_api = OpenSubtitles()
        self.print_banner()
    
    def print_banner(self):
        """طباعة شعار البرنامج"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🎬  Sites - Colab Subtitle Downloader  🎬                 ║
║                                                              ║
║   📥 تحميل الترجمات على Google Colab                        ║
║   🌐 يدعم: OpenSubtitles, Direct URLs                       ║
║   🔗 فقط أدخل الرابط أو اسم الفيلم!                         ║
║                                                              ║
║   👨‍💻 By: Ahmed Abohamada                                    ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def download_from_url(self, url: str, output_name: str = None) -> bool:
        """تحميل مباشر من رابط"""
        try:
            print(f"⏳ جاري التحميل من: {url}")
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                if output_name is None:
                    output_name = url.split('/')[-1] or 'subtitle.srt'
                
                output_path = self.output_dir / output_name
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ تم التحميل بنجاح: {output_path}")
                return True
            else:
                print(f"❌ فشل التحميل - الحالة: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return False
    
    def search_and_download(self, query: str, language: str = 'ara') -> bool:
        """البحث والتحميل"""
        try:
            print(f"🔍 جاري البحث عن: {query}")
            results = self.os_api.search_subtitles(query, language)
            
            if results:
                print(f"✅ تم العثور على {len(results)} نتيجة")
                for i, result in enumerate(results[:5]):  # أول 5 نتائج
                    print(f"\n{i+1}. {result.get('SubFileName', 'Unknown')}")
                    print(f"   📊 التقييم: {result.get('SubRating', 'N/A')}")
                    print(f"   📥 التنزيلات: {result.get('SubDownloadsCnt', 'N/A')}")
                
                # تحميل الأول
                first_result = results[0]
                subtitle_id = first_result.get('IDSubtitleFile')
                filename = first_result.get('SubFileName', 'subtitle.srt')
                
                output_path = self.output_dir / filename
                if self.os_api.download_subtitle(subtitle_id, str(output_path)):
                    print(f"\n✅ تم التحميل: {filename}")
                    return True
            else:
                print("❌ لم يتم العثور على نتائج")
                return False
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return False
    
    def create_colab_ui(self):
        """إنشاء واجهة Google Colab"""
        try:
            from google.colab import widgets
            from IPython.display import display
            
            # العنوان
            title = widgets.HTML("<h2>🎬 تحميل الترجمات</h2>")
            
            # اختيار الطريقة
            method_selector = widgets.ToggleButtons(
                options=['من رابط مباشر', 'بحث عن فيلم'],
                description='الطريقة:',
            )
            
            # حقل الإدخال
            input_field = widgets.Text(
                placeholder='أدخل الرابط أو اسم الفيلم',
                description='المدخل:',
                style={'description_width': '100px'}
            )
            
            # اختيار اللغة
            language_selector = widgets.Dropdown(
                options=[
                    ('العربية', 'ara'),
                    ('الإنجليزية', 'eng'),
                    ('الفرنسية', 'fre'),
                    ('الإسبانية', 'spa'),
                    ('الألمانية', 'ger'),
                ],
                value='ara',
                description='اللغة:',
                style={'description_width': '100px'}
            )
            
            # زر التحميل
            download_button = widgets.Button(
                description='🔽 تحميل',
                button_style='success',
                tooltip='انقر للتحميل'
            )
            
            # منطقة الإخراج
            output_area = widgets.Output()
            
            def on_download_click(b):
                with output_area:
                    output_area.clear_output()
                    if not input_field.value.strip():
                        print("⚠️ الرجاء إدخال بيانات!")
                        return
                    
                    if method_selector.value == 'من رابط مباشر':
                        self.download_from_url(input_field.value)
                    else:
                        self.search_and_download(input_field.value, language_selector.value)
            
            download_button.on_click(on_download_click)
            
            # ترتيب العناصر
            vbox = widgets.VBox([
                title,
                widgets.HTML("<hr>"),
                widgets.Label("اختر طريقة التحميل:"),
                method_selector,
                widgets.HTML("<hr>"),
                input_field,
                language_selector,
                download_button,
                widgets.HTML("<hr>"),
                widgets.HTML("<b>📋 النتائج:</b>"),
                output_area,
            ])
            
            display(vbox)
            print("✅ تم تحميل الواجهة بنجاح!")
            
        except ImportError:
            print("⚠️ لم يتم العثور على google.colab - هذا ليس Google Colab!")
            print("💡 استخدم واجهة بدون Colab widgets:")
            self.create_simple_ui()
    
    def create_simple_ui(self):
        """واجهة بسيطة بدون Colab widgets"""
        print("\n" + "="*60)
        print("🎯 اختر الطريقة:")
        print("1️⃣  تحميل من رابط مباشر")
        print("2️⃣  البحث عن فيلم")
        print("3️⃣  الخروج")
        
        choice = input("\n👉 اختيارك (1/2/3): ").strip()
        
        if choice == '1':
            url = input("🔗 أدخل الرابط: ").strip()
            if url:
                self.download_from_url(url)
        elif choice == '2':
            query = input("🎬 أدخل اسم الفيلم: ").strip()
            if query:
                self.search_and_download(query)
        elif choice == '3':
            print("👋 وداعاً!")
        else:
            print("❌ اختيار غير صحيح!")


# ==================== Colab Run Instructions ====================

def run_colab():
    """تشغيل البرنامج على Google Colab"""
    downloader = ColabSubtitleDownloader(output_dir="/content/subtitles")
    downloader.create_colab_ui()


if __name__ == "__main__":
    # للتشغيل المباشر
    downloader = ColabSubtitleDownloader()
    
    # محاولة استخدام واجهة Colab
    try:
        from google.colab import widgets
        downloader.create_colab_ui()
    except ImportError:
        # استخدام واجهة بسيطة إذا لم تكن على Colab
        downloader.create_simple_ui()