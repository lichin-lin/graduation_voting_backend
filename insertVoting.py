import csv
import sqlite3

db = sqlite3.connect('songs.db')
with db:
    db.executemany(
        'INSERT INTO  voting_record (memberid, songid) VALUES (?, ?)',
        [('0316005', 1),
        ('0316015', 1)]
    )

preview = db.execute('SELECT * FROM voting_record LIMIT 3')
for row in preview:
    print(row)

# table 1 song
# id            INTERGER
# title         TEXT
# group_name    TEXT
# lyrics        TEXT
# about         TEXT
# link          TEXT

# table 2 voting record
# memberID      INTERGER
# songid        INTERGER (foreign key)
# time          DATETIME
#
