import re
from bs4 import BeautifulSoup
from Firefox_DB_Manager import DB_Manager

# bookmark file downloaded from brave
BOOKMARK_FILE = """bookmarks_2_13_21.html"""

# first go through and get rid of extra info like the <p> and <DT> headers
edited = []
with open(BOOKMARK_FILE, 'r') as b_f:
    lines_list = b_f.readlines()
    for line in lines_list:
        line = re.sub("<p>|<DT>", "", line)
        edited.append(line)

# Quick aside, we want to keep the <DL> tags because they show when
# to start new folders

# now write our updates back to the file
with open(BOOKMARK_FILE, 'w') as b_f:
    b_f.writelines(edited)


# path to firefox bookmarks
FIREFOX_BOOKMARKS= """/Users/Chase/Library/Application Support
                      /Firefox/Profiles/fk36q28a.default-release/places.sqlite3"""


# first open it to read the tags in as objects using BeautifulSoup
with open(BOOKMARK_FILE) as b_f:

    soup = BeautifulSoup(b_f, 'html.parser')
    # find all h3 tags
    h3 = soup.find_all('h3')
    h3_counter = 0

    # find all a tags
    a_links = soup.find_all('a')
    a_counter = 0

# now step through the file to get proper structure of folders/files
with open(BOOKMARK_FILE) as b_f:
    position = 0
    position_stack = []
    parent = 3
    parent_stack = [3]
    parent_stack.insert(0, parent)
    db = DB_Manager("places.sqlite")
    lines = b_f.readlines()

    for line in lines:
        # h3s are folder names
        if "<H3 " in line:
            print(h3[h3_counter].string)
            folder_title = h3[h3_counter].string
            parent = db.add_folder(folder_title, parent)
            parent_stack.insert(0, parent)
            h3_counter += 1
        if "</DL>" in line:
            parent_stack.pop(0)
            parent = parent_stack[0]
        if "<A " in line:
            link_title = a_links[a_counter].string
            link_ref = a_links[a_counter]['href']
            db.add_bookmark(link_title, link_ref, parent)
            a_counter += 1

    db.cursor_commit()
    db.cursor_close()

