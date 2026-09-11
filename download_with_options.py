import sys
import yt_dlp
import os
from datetime import datetime

import config as cfg

# Create download folder
DOWNLOAD_FOLDER = "ytdowns"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
my_url = ''

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
	print("\n" + "="*96)

	print(f"Available formats for : {title}")
	print("="*96)
	print(f"{'#':<4} {'Res':<12} {'FPS':<12} {'Size':<10} {'Format':<18} {'Note':<20}")
	print("-"*96)

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

		print(f"{len(valid_formats):<4} {res:<12} {fps_str:<12} {size_str:<10} "
				f"{ext.upper():<18} {note:<20}")

	print("-"*80)
	return valid_formats


def download_with_choice(url):
	ydl_opts = cfg.gen_opts_options()

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
				print("-> No downloadable formats found.")
				return

			# Get user choice
			while True:
				try:
					choice = input(f"\n-> Enter choice {cfg.fr_yellow}(1-{len(valid_formats)}){cfg.fr_reset} or 'b' to skip: ")
					if choice.lower() == 'b':
						print("-> ⏭ Skipped.")
						return
					idx = int(choice) - 1
					if 0 <= idx < len(valid_formats):
						selected_format = valid_formats[idx]
						break
					else:
						print(f"-> Please enter a number between 1 and {len(valid_formats)}.")
				except ValueError:
					print("-> Invalid input. Enter a number.")

			# Prepare download
			format_id = selected_format['format_id']
			file_ext = selected_format['ext']
			
			# FIX: If it's video-only, grab the best audio and merge them
			download_format = format_id
			is_video_only = selected_format.get('acodec') == 'none' and selected_format.get('vcodec') != 'none'
			if is_video_only:
				download_format = f"{format_id}+bestaudio"
				file_ext = 'mp4' # Force mp4 extension so the merged file plays correctly

			safe_title = sanitize_filename(title)
			timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
			output_filename = f"{timestamp}_{safe_title}.{file_ext}"
			output_path = os.path.join(DOWNLOAD_FOLDER, output_filename)
			
			print(f"\n-> Downloading: {title} ")
			print(f"| Format: {selected_format['format']} ({format_id})")
			print(f"| Saving as: {output_filename}\n")
			
			# Download with progress
			ydl_opts_download = {
				'format': download_format,
				'merge_output_format': 'mp4', # Tells yt-dlp to use FFmpeg to glue them
				'outtmpl': output_path,
				'progress_hooks': [lambda d: download_hook(d, output_filename)],
			}

			with yt_dlp.YoutubeDL(ydl_opts_download) as ydl2:
				ydl2.download([url])

		except Exception as e:
			print(f"\n-> Error fetching video info: {str(e)}")


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
		print("\n-> Download completed!")


def main():
	global my_url

	print(f"YouTube Downloader {cfg.fr_yellow}(customized download){cfg.fr_reset}")
	print(cfg.saveInform)

	while True:
		if my_url == '':
			url = input("\n-> Enter YouTube URL (or 'quit' to exit): ").strip()
		else:
			url = my_url
			my_url = ''

		if not url or url.lower() in cfg.leaveList:
			print(cfg.leaveTxt)
			break

		download_with_choice(url)

		again = input("\n\t-> Download another video? (y/n): ").strip().lower()
		if again not in cfg.agreeList:
			print(cfg.leaveTxt)
			break


def quickie(url):
    global my_url

    my_url = url
    main()
    return True

if __name__ == "__main__":
	main()