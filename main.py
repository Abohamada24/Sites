# خلية: تحديث main.py

main_code = '''#!/usr/bin/env python3
"""
Sites - Subtitle Downloader
Main Entry Point
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from interactive import quick_download, InteractiveDownloader


def main():
    parser = argparse.ArgumentParser(
        description="🎬 Sites - Subtitle Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Inception"
  python main.py "https://youtube.com/watch?v=xxx"
  python main.py "The Matrix" --lang ara
  python main.py "tt0133093" --output ./my_subs
        """
    )
    
    parser.add_argument("input", nargs="?", help="Movie name, URL, or IMDB ID")
    parser.add_argument("--lang", "-l", default="ara", help="Language: ara, eng")
    parser.add_argument("--output", "-o", default="./subtitles", help="Output directory")
    
    args = parser.parse_args()
    
    if not args.input:
        parser.print_help()
        print("\\n💡 Examples:")
        print('   python main.py "Inception"')
        print('   python main.py "https://youtube.com/watch?v=xxx"')
        return
    
    # تنفيذ
    files = quick_download(
        args.input,
        language=args.lang,
        output_dir=args.output
    )
    
    if files:
        print(f"\\n🎉 Done! Downloaded {len(files)} file(s)")
    else:
        print("\\n⚠️ No files downloaded")


if __name__ == "__main__":
    main()
'''

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(main_code)

print("✅ تم تحديث main.py!")