import sqlite3

"""Handles database transactions of Firefox places.sqlite database"""

""" schema for moz_bookmarks table
id - INT
type - INT [this sets whether or not it is a folder (1 for link, 2 for folder)]
fk - INT (default NULL) [this foreign key is what we need in order to link the
         bookmark to it's url in moz_places]
parent - INT
position - INT
title - LONGVARCHAR
keyword_id - INT
folder_type - TEXT
dateAdded - INT
lastModified - INT
guid - TEXT
syncStatus - INT (not NULL default 0)
syncChangeCounter - INT (not null default 1)
"""

""" schema for moz_places
id - INT
url - LONGVARCHAR
currently don't use the rest
"""

class DB_Manager:

    def __init__(self, path):
        conn = sqlite3.connect(path)
        self._cur = conn.cursor()
        self.bk_table = "moz_bookmarks"
        self.url_table = "moz_places"


    def add_bookmark(self, title, url, parent_id, position):
        try:
            fk = self.add_url(url)
            self._cur.execute("INSERT INTO %s VALUES(type=1, fk=?, parent=?, position=?, title=?)" % self.bk_table, (fk, parent_id, position, title))
        except sqlite3.Error as e:
            raise e

    # returns id of the item just added
    def add_folder(self, title, parent_id, position):
        try:

            self._cur.execute("INSERT INTO %s VALUES(type=2, parent=?, title=?, position=?)" % self.bk_table, (parent_id, title, position))
            return self._cur.lastrowid
        except sqlite3.Error as e:
            raise e

    """First check if url is in history already:
        if it is, get id 
        else create entry in places and get id"""
    def add_url(self, url: str) -> int:
        try:
            self._cur.execute("SELECT id FROM %s WHERE url=?" % self.url_table, (url,))
            index = self._cur.fetchone()
            if index is not None:
                return index[0]
            else:
                self._cur.execute("INSERT INTO %s(url) VALUES (?)" % self.url_table, (url,))
                return self._cur.lastrowid
        except sqlite3.Error as e:
            raise e

    "id in this case is id from moz_places (or fk from moz_bookmarks)"
    def get_url_from_id(self, id) -> str:
        try:
            # for some reason it is not letting me put the table in using the ? format
            self._cur.execute("SELECT url FROM %s WHERE id=?" % self.url_table, (id,))
            return self._cur.fetchone()[0]
        except sqlite3.Error as e:
            raise e

    def cursor_close(self):
        self._cur.close()

    def cursor_commit(self):
        self._cur.connection.commit()


if __name__ == '__main__':
    PATH = 'places.sqlite'
    bkmk_db = DB_Manager(PATH)
    print(bkmk_db.get_url_from_id(88))
    print(bkmk_db.add_url("https://chasefierro.com"))
    parent = 5
    parent = bkmk_db.add_folder("things", parent)
    parent = bkmk_db.add_folder("more things", parent)
    bkmk_db.add_bookmark("website I like", "https://my_awesome_website.com", parent)
    bkmk_db.add_bookmark("website I also like", "https://my_tia_awesome_website.com", parent)
    bkmk_db.cursor_commit()
    bkmk_db.cursor_close()

