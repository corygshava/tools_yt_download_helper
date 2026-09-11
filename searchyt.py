# Mostly AI slop

# qwen_py_ytsearch.py
import yt_dlp
import pyperclip
import config as cfg

from download_quick import quickie
from download_with_options import quickie as custom

usequick = False

def search_youtube(query, max_results=10):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'noplaylist': True,
    }

    search_url = f"ytsearch{max_results}:{query}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(search_url, download=False)
            return result.get('entries', [])
        except Exception as e:
            print(f"❌ Search failed: {str(e)}")
            return []

def main():
    leaveme = False

    while not leaveme:
        print("YouTube Video Search Tool")
        print("Enter a search query to find videos\n")

        while True:
            query = input("-> Search YouTube: ").strip()
            if not query:
                print("-> Please enter a valid query.\n")
                continue
            break

        print(f"\n⁕ Searching for: '{query}'...\n")
        results = search_youtube(query, max_results=10)

        if not results:
            print("ಠ_ಠ No results found. Check your internet or try another query.")
            return

        print("^_^ Search Results:")
        print("-" * 96)

        for idx, video in enumerate(results, start=1):
            title = video.get('title', 'No Title')
            duration = video.get('duration', 0)
            mins, secs = (duration // 60, duration % 60) if duration else (0, 0)
            dur_str = f"{int(mins):02d}:{int(secs):02d}" if duration else "--:--"
            view_count = video.get('view_count', 0)
            views = f"{view_count:,}" if view_count else "N/A"

            print(f"{idx:2}. {title}")
            print(f"     Duration: {dur_str} | Views: {views}")
            print()

        print("-" * 80)

        # Let user choose
        while True:
            try:
                choice = input(f"-> Select video {cfg.fr_yellow}(1-{len(results)}){cfg.fr_reset} or 'b' to go back: ").strip()
                if choice.lower() == 'b':
                    print("-> Exiting search...")
                    return
                idx = int(choice) - 1
                if 0 <= idx < len(results):
                    selected = results[idx]
                    break
                else:
                    print(f"-> Please enter a number between 1 and {len(results)}.")
            except ValueError:
                print("-> Invalid input. Enter a number.")

        video_url = f"https://www.youtube.com/watch?v={selected['id']}"

        # Copy to clipboard
        # pyperclip.copy(video_url)
        # print(f"\n-> URL copied to clipboard:")
        print(f"->{cfg.fr_green}URL:{cfg.fr_reset} {video_url}")

        npt = input('\ndo you want customizable downloads? (y/n)')
        usequick = npt in cfg.agreeList

        if(usequick):
            custom(video_url)
        else:
            quickie(video_url)

        leavethis = input("-> search again (y/n): ")

        leaveme = leavethis == "n"

        """
        print(f"Now open 'qwen_py_ytdownloadermain.py' and paste the link to download.")

        # Optional: auto launch the main downloader
        launch = input("\nPress Enter to launch the downloader now, or 'n' to exit: ").strip()
        if launch.lower() != 'n':
            import subprocess
            subprocess.run([sys.executable, "qwen_py_ytdownloadermain.py"])
        """

if __name__ == "__main__":
    main()