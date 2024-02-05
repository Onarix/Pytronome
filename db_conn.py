import sqlite3

conn = sqlite3.connect("db/songs.db")


def getBPM(song):
    response_bpm = None  # Default to None if not found
    query = "SELECT BPM FROM Songs WHERE Title=?"  # Using parameterized query

    res = conn.execute(query, (song,))

    for row in res:
        response_bpm = row[0]  # Assuming BPM is the first column in the result
        break  # Assuming you only want to retrieve the first matching BPM

    return response_bpm


def getSongs():
    res = conn.execute("SELECT * FROM Songs")
    songlist = dict()

    for row in res:
        songlist[row[0]] = [row[1], row[2], row[3]]

    return songlist


def addSong(title, artist, bpm):
    query = "INSERT INTO Songs (Title, Artist, BPM) VALUES (?, ?, ?)"
    print(f"Title: {title.lower()}, Artist: {artist}, BPM: {bpm}")
    conn.execute(
        query,
        (
            title.lower(),
            artist,
            bpm,
        ),
    )
    conn.commit()

def deleteSong(songID):
    query = "DELETE FROM Songs WHERE SongID=?"
    conn.execute(query, (songID,))
    conn.commit()
