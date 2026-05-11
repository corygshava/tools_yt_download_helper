from download_quick import main as quicky
from download_with_options import main as options
from searchyt import main as searchme

leave = False

while not leave:
    chosen = input("do you want a quick download or a customisable download\n\t1 -> quick\n\t2 -> customisable\n\t3 -> search YT\n\tq -> quit\n\nyour choice: ");

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

print("bye for now");