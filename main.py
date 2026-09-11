from download_quick import main as quicky
from download_with_options import main as options
from searchyt import main as searchme

import config as cfg

# init(autoreset = True)
leave = False

while not leave:
    chosen = input(f"do you want a {cfg.fr_green}quick download{cfg.fr_reset} or a {cfg.fr_yellow}something else{cfg.fr_reset}\n\t1 -> quick\n\t2 -> customisable\n\t3 -> search YT\n\tq -> quit\n\nyour choice: ");

    if (chosen == "1"):
        print("continuing with the quick option\n")
        quicky()
    elif (chosen == "2"):
        print("continuing with the advanced option\n")
        options()
    elif (chosen == "3"):
        print("continuing with the search option\n")
        searchme()
    else:
        leave = True
    pass

print("bye for now, :)");