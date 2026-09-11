import sys
import yt_dlp
import os
from datetime import datetime

# Create download folder
DOWNLOAD_FOLDER = "ytdowns"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def get_readable_size(bytes_val):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"


def sanitize_filename(name):
    """Remove invalid characters from filename"""
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()


def show_format_menu(formats, title):
    """Display available formats for user to choose"""
    print("\n" + "="*80)
    print(f"🎥 SELECT FORMAT FOR: {title}")
    print("="*80)
    print(f"{'#':<4} {'Res':<8} {'FPS':<5} {'Size':<10} {'Format':<12} {'Note':<20}")
    print("-"*80)

    valid_formats = []
    for f in formats:
        # Only show formats with video
        if f.get('vcodec') == 'none' or f.get('acodec', 'none') == 'none' and 'DASH' in f.get('format_note', ''):
            continue  # Skip DASH-only parts unless needed

        res = f.get('resolution', 'unknown')
        if res == 'audio only':
            res = 'N/A'

        fps = f.get('fps', '')
        fps_str = f"{fps}fps" if fps else ""

        size = f.get('filesize') or f.get('filesize_approx')
        size_str = get_readable_size(size) if size else "Unknown"

        ext = f['ext']
        format_id = f['format_id']
        vcodec = f.get('vcodec', 'unknown')
        acodec = f.get('acodec', 'none')

        note = f.get('format_note', '') or ""

        # Label combined vs. DASH
        if 'acodec' in f and f['acodec'] != 'none' and 'vcodec' in f and f['vcodec'] != 'none':
            kind = "Combined"
        else:
            kind = "Video-only" if f['acodec'] == 'none' else "Audio-only"
            note = f"{note} ({kind})".strip()

        valid_formats.append(f)

        print(f"{len(valid_formats):<4} {res:<8} {fps_str:<5} {size_str:<10} "
              f"{ext.upper():<6} {note:<20}")

    print("-"*80)
    return valid_formats


def download_with_choice(url):
    # old format (doesnt work anyway)
    # ydl_opts = {
    #     'quiet': True,
    #     'format': 'bestaudio/best',  # Just to fetch info
    #     'noplaylist': True,
    # }

    ydl_opts = {
        'quiet': True,
        'format': 'bestvideo+bestaudio/best',  # Allows seeing combined and mergeable formats
        'noplaylist': True,
        'cookiefile': 'cookies.txt',           # Prevents 403 / DPAPI errors
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract video info
            info = ydl.extract_info(url, download=False)
            title = info['title']
            formats = info['formats']
            ext = info.get('ext', 'mp4')

            # Show menu
            valid_formats = show_format_menu(formats, title)

            if not valid_formats:
                print("❌ No downloadable formats found.")
                return

            # Get user choice
            while True:
                try:
                    choice = input(f"\nEnter choice (1-{len(valid_formats)}) or 'b' to skip: ")
                    if choice.lower() == 'b':
                        print("⏭️  Skipped.")
                        return
                    idx = int(choice) - 1
                    if 0 <= idx < len(valid_formats):
                        selected_format = valid_formats[idx]
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(valid_formats)}.")
                except ValueError:
                    print("Invalid input. Enter a number.")

            # Prepare download
            format_id = selected_format['format_id']
            file_ext = selected_format['ext']

            safe_title = sanitize_filename(title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{timestamp}_{safe_title}.{file_ext}"
            output_path = os.path.join(DOWNLOAD_FOLDER, output_filename)

            print(f"\n🚀 Downloading: {title}")
            print(f"📌 Format: {selected_format['format']} ({format_id})")
            print(f"💾 Saving as: {output_filename}\n")

            # Download with progress
            ydl_opts_download = {
                'format': format_id,
                'outtmpl': output_path,
                'progress_hooks': [lambda d: download_hook(d, output_filename)],
            }

            with yt_dlp.YoutubeDL(ydl_opts_download) as ydl2:
                ydl2.download([url])

        except Exception as e:
            print(f"\n❌ Error fetching video info: {str(e)}")


def download_hook(d, filename):
    """Progress hook for download"""
    if d['status'] == 'downloading':
        percent = d.get('downloaded_bytes', 0)
        total = d.get('total_bytes', 0)
        speed = d.get('speed', 0)
        eta = d.get('eta', 0)

        if total > 0:
            pct = (percent / total) * 100
        else:
            pct = 0

        downloaded_mb = percent / (1024 * 1024) if percent else 0
        total_mb = total / (1024 * 1024) if total else 0
        speed_mbps = speed / (1024 * 1024) if speed else 0

        mins, secs = divmod(int(eta), 60) if eta else (0, 0)

        bar_len = 20
        filled = int(bar_len * pct // 100)
        bar = "█" * filled + "░" * (bar_len - filled)

        sys.stdout.write(f"\r{bar} {pct:5.1f}% | {downloaded_mb:.1f}/{total_mb:.1f} MB | "
                         f"{speed_mbps:.1f} MB/s | ETA {mins:02d}:{secs:02d}      ")
        sys.stdout.flush()

    elif d['status'] == 'finished':
        print("\n✅ Download completed!")


def main():
    print("YouTube Quality Selector (yt-dlp)")
    print("📁 Videos saved to: ./ytdowns")

    while True:
        url = input("\n🔗 Enter YouTube URL (or 'quit' to exit): ").strip()
        if not url or url.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break

        download_with_choice(url)

        again = input("\n🔁 Download another video? (y/n): ").strip().lower()
        if again not in ['y', 'yes']:
            print("👋 Goodbye!")
            break


if __name__ == "__main__":
    main()