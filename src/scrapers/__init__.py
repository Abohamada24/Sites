"""
Scrapers for different subtitle sources
"""

from .youtube import YouTubeScraper
from .opensubtitles import OpenSubtitlesScraper
from .base_scraper import BaseScraper

__all__ = [
    'YouTubeScraper',
    'OpenSubtitlesScraper',
    'BaseScraper'
]