# Mostly AI slop

import sys
import yt_dlp
import os
from datetime import datetime

DOWNLOAD_FOLDER = "ytdowns"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def get_output_filename(template):
    safe_title = "".join(c for c in template if c.isalnum() or c in (' ', '-', '_')).strip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{safe_title}.mp4"

def hook(d):
    if d['status'] == 'downloading':
        downloaded = d.get('downloaded_bytes', 0)
        total = d.get('total_bytes', 0)
        speed = d.get('speed', 0)
        eta = d.get('eta', 0)

        if total > 0:
            percent = (downloaded / total) * 100
        else:
            percent = 0

        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        speed_mbps = speed / (1024 * 1024) if speed else 0

        mins, secs = divmod(int(eta), 60) if eta else (0, 0)

        bar_length = 20
        filled = int(bar_length * percent // 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        sys.stdout.write(f"\r{bar} {percent:5.1f}% | {downloaded_mb:.1f}/{total_mb:.1f} MB | "
                         f"{speed_mbps:.1f} MB/s | ETA {mins:02d}:{secs:02d}      ")
        sys.stdout.flush()

    elif d['status'] == 'finished':
        print("\n✅ Download completed, now converting...")

def download_video(url):
    # doesnt work
    # ydl_opts = {
    #     'format': 'best[ext=mp4]',
    #     'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
    #     'progress_hooks': [hook],
    # }

    # works but the format is sometimes not available
    # ydl_opts = {
    #     'format': 'best[ext=mp4]',
    #     'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
    #     'progress_hooks': [hook],
    #     # 'cookiesfrombrowser': ('chrome',), # <--- Add this line (use 'firefox', 'edge', etc. if needed)
    #     'cookiefile': 'cookies.txt',
    # }

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best', # Grabs best video and best audio separately
        'merge_output_format': 'mp4',         # Glues them together into an MP4
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'progress_hooks': [hook],
        'cookiefile': 'runtime/cookies.txt',          # Keep your cookie fix!
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        original_title = info.get('title', 'video')
        downloaded_ext = info.get('ext', 'mp4')

        # Rename with timestamp
        old_file = os.path.join(DOWNLOAD_FOLDER, f"{original_title}.{downloaded_ext}")
        new_filename = get_output_filename(original_title)
        new_file = os.path.join(DOWNLOAD_FOLDER, new_filename)

        if os.path.exists(old_file):
            os.rename(old_file, new_file)
            print(f"💾 Saved as: {new_filename}")

def main():
    print("YouTube Downloader (yt-dlp)")
    while True:
        url = input("\n🔗 Enter YouTube URL (or 'quit' to exit): ").strip()
        if not url or url.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break

        try:
            download_video(url)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

        again = input("\n🔁 Download another? (y/n): ").strip().lower()
        if again not in ['y', 'yes']:
            print("👋 Goodbye!")
            break

if __name__ == "__main__":
    main()