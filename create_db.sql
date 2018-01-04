CREATE TABLE songs (
    id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    title TEXT NOT NULL,
    group_name TEXT NOT NULL,
    lyrics TEXT,
    about TEXT,
    link TEXT
);

CREATE TABLE voting_record (
    memberid INTEGER,
    songid INTEGER,
    time DATETIME DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (songid) REFERENCES songs(id)
);

-- INSERT INTO songs (title, group_name)
-- VALUES
-- ('qq1', 'kevin'),
-- ('fr', 'jenny');
-- .header on
-- SELECT * FROM songs;
