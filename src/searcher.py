import requests
from bs4 import BeautifulSoup
import re

class SubtitleSearcher:
    def __init__(self):
        self.base_urls = {
            'opensubtitles': 'https://www.opensubtitles.org',
            'subscene': 'https://subscene.com'
        }
    
    def search_opensubtitles(self, movie_name, language='ara'):
        """البحث في OpenSubtitles"""
        search_url = f"{self.base_urls['opensubtitles']}/en/search2/sublanguageid-{language}/moviename-{movie_name}"
        
        try:
            response = requests.get(search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            # استخراج النتائج (مثال مبسط)
            for row in soup.find_all('tr', {'class': 'change'}):
                title = row.find('a')
                if title:
                    results.append({
                        'title': title.text.strip(),
                        'url': self.base_urls['opensubtitles'] + title['href']
                    })
            
            return results[:10]  # أول 10 نتائج
            
        except Exception as e:
            print(f"خطأ في البحث: {e}")
            return []
    
    def search_youtube(self, video_url):
        """استخراج الترجمة من يوتيوب"""
        import yt_dlp
        
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ar', 'en'],
            'skip_download': True,
            'outtmpl': '%(title)s.%(ext)s'
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return info.get('subtitles', {})
        except Exception as e:
            print(f"خطأ: {e}")
            return {}