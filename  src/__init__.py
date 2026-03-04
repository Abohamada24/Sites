"""
Sites - Subtitle Downloader Package
Author: Ahmed Abohamada
"""

__version__ = "1.0.0"
__author__ = "Ahmed Abohamada"
__email__ = "your.email@example.com"

from .core.downloader import SubtitleDownloader
from .scrapers.youtube import YouTubeScraper
from .scrapers.opensubtitles import OpenSubtitlesScraper

__all__ = [
    'SubtitleDownloader',
    'YouTubeScraper', 
    'OpenSubtitlesScraper'
]