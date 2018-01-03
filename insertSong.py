import csv
import sqlite3

with open('./songs.csv', newline='') as f:
    csv_reader = csv.DictReader(f)
    songs = [
        (row['曲名'], row['團體名'])
        for row in csv_reader
    ]
    print(songs)

with open('create_db.sql') as f:
    create_db_sql = f.read()

db = sqlite3.connect('songs.db')
with db:
    db.executescript(create_db_sql)

with db:
    db.executemany(
        'INSERT INTO  songs (title, group_name) VALUES (?, ?)',
        songs
    )

preview = db.execute('SELECT * FROM songs LIMIT 3')
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
