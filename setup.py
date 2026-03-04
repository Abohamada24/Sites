"""
Setup script for Sites - Subtitle Downloader
"""

from setuptools import setup, find_packages
from pathlib import Path

# قراءة README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# قراءة المتطلبات
requirements = (this_directory / "requirements.txt").read_text(encoding='utf-8').splitlines()

setup(
    name="sites-subtitle-downloader",
    version="1.0.0",
    author="Ahmed Abohamada",
    author_email="your.email@example.com",
    description="أداة قوية لتحميل وإدارة ملفات الترجمة من مصادر متعددة",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Abohamada24/Sites",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Natural Language :: Arabic",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'sites=main:main',
        ],
    },
    keywords='subtitle, download, opensubtitles, subscene, youtube, srt, vtt',
    project_urls={
        'Bug Reports': 'https://github.com/Abohamada24/Sites/issues',
        'Source': 'https://github.com/Abohamada24/Sites',
        'Documentation': 'https://github.com/Abohamada24/Sites/blob/main/README.md',
    },
)