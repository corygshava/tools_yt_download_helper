import os

DOWNLOAD_FOLDER = "ytdowns"
DOWNLOAD_FOLDER_MUSIC = "ytmusica"
COOKIE_FILE = "runtime/cookies.txt"

# runtime stuff
leaveList = ['quit', 'exit', 'q','leave','nope','no','fuck off']
leaveTxt = "\nGoodbye, see you soon :)\n"
agreeList = ['y', 'yes','fuck yeah','yeah','ok']
saveInform = f"videos saved to ./{DOWNLOAD_FOLDER}"

# terminal colors
from colorama import  init, Fore, Back, Style
init(autoreset = True)

fr_reset = Fore.RESET
fr_green = Fore.GREEN
fr_blue = Fore.BLUE
fr_yellow = Fore.YELLOW
fr_red = Fore.RED


# pass the hook for the timer
def gen_opts_nermal(h):
	return  {
		# 'format': 'bestvideo+bestaudio/best',		# Grabs best video and best audio separately
		'format': 'bestvideo[height<=360]+bestaudio/best',
		'merge_output_format': 'mp4',				# Glues them together into an MP4
		'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
		'progress_hooks': [h],
		'cookiefile': COOKIE_FILE, 					# Keep your cookie fix!
	}

def gen_opts_options():
	 # old format (doesnt work anyway)
	return {
        'quiet': True,
        'format': 'bestvideo+bestaudio/best',  # Allows seeing combined and mergeable formats
        'noplaylist': True,
        'cookiefile': 'cookies.txt',           # Prevents 403 / DPAPI errors
    }
