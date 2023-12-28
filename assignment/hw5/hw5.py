import sqlite3
from faker import Faker
import random

fake = Faker()

# Connect to SQLite database (or create it if it doesn't exist)
mydb = sqlite3.connect('hw5.db')
cursor = mydb.cursor()

# Check if Artist table exists, if not, create it
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Artist (
        ArtistID INTEGER PRIMARY KEY,
        Name TEXT UNIQUE,
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
''')

# Check if Genre table exists, if not, create it
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Genre (
        GenreID INTEGER PRIMARY KEY,
        GenreName TEXT UNIQUE,
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Song (
        SongID INTEGER PRIMARY KEY,
        Title TEXT,
        ReleaseDate DATE,
        ArtistID INTEGER,
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ArtistID) REFERENCES Artist(ArtistID)        
    );
''')

# Check if SongGenre table exists, if not, create it
cursor.execute('''
    CREATE TABLE IF NOT EXISTS SongGenre (
        SongID INTEGER,
        GenreID INTEGER,
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (SongID) REFERENCES Song(SongID),
        FOREIGN KEY (GenreID) REFERENCES Genre(GenreID),
        PRIMARY KEY (SongID, GenreID)
    );
''')

# Check if Album table exists, if not, create it
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Album (
        AlbumID INTEGER PRIMARY KEY,
        Name TEXT,
        ReleaseDate DATE,
        ArtistID INTEGER,
        SongID INTEGER,
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ArtistID) REFERENCES Artist(ArtistID),
        FOREIGN KEY (SongID) REFERENCES Song(SongID)
    );
''')

# Check if User table exists, if not, create it
cursor.execute('''
    CREATE TABLE IF NOT EXISTS User (
        UserID INTEGER PRIMARY KEY,
        Username TEXT UNIQUE,
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
''')

# Check if Playlist table exists, if not, create it
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Playlist (
        PlaylistID INTEGER PRIMARY KEY,
        Title TEXT,
        CreatedDateTime DATETIME,
        UserID INTEGER,
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (UserID) REFERENCES User(UserID)
    );
''')

# Check if SongPlaylist table exists, if not, create it
cursor.execute('''
   CREATE TABLE IF NOT EXISTS SongPlaylist (
    SongID INTEGER,
    PlaylistID INTEGER,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SongID) REFERENCES Song(SongID),
    FOREIGN KEY (PlaylistID) REFERENCES Playlist(PlaylistID),
    PRIMARY KEY (SongID, PlaylistID) 
    );
''')

# Check if Rating table exists, if not, create it
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Rating (
        RatingID INTEGER PRIMARY KEY,
        RatingValue INTEGER CHECK (RatingValue BETWEEN 1 AND 5),
        RatedDate DATE,
        UserID INTEGER,
        SongID INTEGER,
        AlbumID INTEGER,
        PlaylistID INTEGER,
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (UserID) REFERENCES User(UserID),
        FOREIGN KEY (SongID) REFERENCES Song(SongID),
        FOREIGN KEY (AlbumID) REFERENCES Album(AlbumID),
        FOREIGN KEY (PlaylistID) REFERENCES Playlist(PlaylistID)
    );
''')

# Insert dummy data into the Artist table
for _ in range(100):
    cursor.execute("INSERT INTO Artist (Name) VALUES (?)", (fake.name(),))

# Insert dummy data into the Genre table
# for _ in range(100):
#     cursor.execute("INSERT INTO Genre (GenreName) VALUES (?)", (fake.word(),))
# Insert dummy data into the Genre table
for _ in range(100):
    genre_name = fake.word()

    # Print the genre name before attempting to insert
    print(f"Attempting to insert genre: {genre_name}")

    # Check if the genre name already exists
    cursor.execute("SELECT 1 FROM Genre WHERE GenreName = ?", (genre_name,))
    exists = cursor.fetchone()

    if not exists:
        # Insert if the genre name does not exist
        cursor.execute("INSERT INTO Genre (GenreName) VALUES (?)", (genre_name,))

# Insert dummy data into the Song table
for _ in range(100):
    artist_id = random.randint(1, 100)
    cursor.execute("INSERT INTO Song (Title, ReleaseDate, ArtistID) VALUES (?, ?, ?)",
                   (fake.word(), fake.date(), artist_id))

# Insert dummy data into the SongGenre table
for song_id in range(1, 101):
    genres = random.sample(range(1, 101), random.randint(1, 3))
    for genre_id in genres:
        cursor.execute("SELECT 1 FROM SongGenre WHERE SongID = ? AND GenreID = ?", (song_id, genre_id))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute("INSERT INTO SongGenre (SongID, GenreID) VALUES (?, ?)", (song_id, genre_id))

# Insert dummy data into the Album table
for _ in range(100):
    artist_id = random.randint(1, 100)
    cursor.execute("INSERT INTO Album (Name, ReleaseDate, ArtistID) VALUES (?, ?, ?)",
                   (fake.word(), fake.date(), artist_id))

# Insert dummy data into the User table
for _ in range(100):
    cursor.execute("INSERT INTO User (Username) VALUES (?)", (fake.user_name(),))

# Insert dummy data into the Playlist table
for _ in range(100):
    cursor.execute("INSERT INTO Playlist (Title, CreatedDateTime, UserID) VALUES (?, ?, ?)",
                   (fake.word(), fake.date_time(), random.randint(1, 100)))

# Insert dummy data into the Rating table
for _ in range(100):
    cursor.execute("INSERT INTO Rating (RatingValue, RatedDate, UserID, SongID, AlbumID, PlaylistID) VALUES (?, ?, ?, ?, ?, ?)",
                   (random.randint(1, 5), fake.date(), random.randint(1, 100), random.randint(1, 100),
                    random.randint(1, 100), random.randint(1, 100)))

# Insert dummy data into the Rating table with SongID only
for _ in range(50):
    cursor.execute("INSERT INTO Rating (RatingValue, RatedDate, UserID, SongID, AlbumID, PlaylistID) VALUES (?, ?, ?, ?, NULL, NULL)",
                   (random.randint(1, 5), fake.date(), random.randint(1, 100), random.randint(1, 100)))

# Insert dummy data into the Rating table with both AlbumID and PlaylistID as NULL
for _ in range(50):
    cursor.execute("INSERT INTO Rating (RatingValue, RatedDate, UserID, SongID, AlbumID, PlaylistID) VALUES (?, ?, ?, ?, NULL, NULL)",
                   (random.randint(1, 5), fake.date(), random.randint(1, 100), random.randint(1, 100)))

# Insert some ratings with AlbumID as NULL and others with PlaylistID as NULL
for _ in range(100):  # Corrected loop range
    cursor.execute("INSERT INTO Rating (RatingValue, RatedDate, UserID, SongID, AlbumID, PlaylistID) VALUES (?, ?, ?, ?, NULL, ?)",
                   (random.randint(1, 5), fake.date(), random.randint(1, 100), random.randint(1, 100), random.randint(1, 100)))

# Insert some ratings with PlaylistID as NULL and others with AlbumID as NULL
for _ in range(100):  # Corrected loop range
    cursor.execute("INSERT INTO Rating (RatingValue, RatedDate, UserID, SongID, AlbumID, PlaylistID) VALUES (?, ?, ?, ?, ?, NULL)",
                   (random.randint(1, 5), fake.date(), random.randint(1, 100), random.randint(1, 100), random.randint(1, 100)))

# Insert dummy data into the SongPlaylist table
for playlist_id in range(1, 101):
    # Each playlist is associated with 1 to 3 songs
    for _ in range(random.randint(1, 3)):
        # Keep generating a new random SongID until a unique combination is found
        while True:
            song_id = random.randint(1, 101)
            # Check if the combination already exists
            cursor.execute("SELECT 1 FROM SongPlaylist WHERE SongID = ? AND PlaylistID = ?", (song_id, playlist_id))
            exists = cursor.fetchone()
            if not exists:
                # Insert into SongPlaylist table
                cursor.execute("INSERT INTO SongPlaylist (SongID, PlaylistID) VALUES (?, ?)",
                               (song_id, playlist_id))
                break

# Commit the changes and close the database connection
mydb.commit()
#
# cursor.execute('''
#     SELECT GenreName AS genre, COUNT(SongID) AS number_of_songs
#     FROM Genre
#     LEFT JOIN SongGenre ON Genre.GenreID = SongGenre.GenreID
#     GROUP BY Genre.GenreID
#     ORDER BY number_of_songs DESC
#     LIMIT 3;
# ''')
#
# # Fetch the result
# result = cursor.fetchall()
#
# # Print the result
# print(result)
# cursor.execute('''
#     SELECT DISTINCT Artist.Name AS artist_name
#     FROM Artist
#     JOIN Song ON Artist.ArtistID = Song.ArtistID
#     WHERE Song.SongID IN (
#         -- Songs in albums
#         SELECT SongID FROM Album
#         WHERE Album.ArtistID = Artist.ArtistID
#
#         UNION
#
#         -- Singles (songs not in albums)
#         SELECT SongID FROM Song
#         WHERE Song.ArtistID = Artist.ArtistID
#     );
# ''')
#
# print('Find names of artists who have songs that are in albums as well as outside of albums (singles)')
# # Fetch the result
# result = cursor.fetchall()
#
# # Print the result
# print("Artist Names:")
# for row in result:
#     print(f"Artist Name: {row[0]}")
#
# cursor.execute('''
#     SELECT Album.Name AS album_name, AVG(Rating.RatingValue) AS avg_rating
#     FROM Album
#     JOIN Rating ON Album.AlbumID = Rating.AlbumID
#     WHERE Album.ReleaseDate BETWEEN '1990-01-01' AND '1999-12-31'
#     GROUP BY Album.AlbumID
#     ORDER BY avg_rating DESC
#     LIMIT 10;
# ''')
#
# # Fetch the result
# result = cursor.fetchall()
#
# # Print the result
# print("Top 10 albums with highest average user rating in the period 1990-1999:")
# print(f"{'Album Name':<20} {'Average User Rating':<20}")
# print("-" * 40)
# for row in result:
#     print(f"{row[0]:<20} {row[1]:<20}")
#
# print("started query for Top 3 most rated genres in the years 1991-1995:")
# cursor.execute('''
#     SELECT Genre.GenreName AS genre_name, COUNT(Rating.SongID) AS number_of_song_ratings
#     FROM Genre
#     JOIN SongGenre ON Genre.GenreID = SongGenre.GenreID
#     JOIN Song ON SongGenre.SongID = Song.SongID
#     JOIN Rating ON Song.SongID = Rating.SongID
#     WHERE strftime('%Y', Rating.RatedDate) BETWEEN '1991' AND '1995'
#     GROUP BY Genre.GenreID
#     ORDER BY number_of_song_ratings DESC
#     LIMIT 3;
# ''')
#
# # Fetch the result
# result = cursor.fetchall()
#
# # Print the result
# print("Top 3 most rated genres in the years 1991-1995:")
# for row in result:
#     print(f"Genre Name: {row[0]} ;;;; Number of Song Ratings: {row[1]}")
#
# cursor.execute('''
#     SELECT User.Username AS username, Playlist.Title AS playlist_title, AVG(Rating.RatingValue) AS average_playlist_rating
#     FROM User
#     JOIN Playlist ON User.UserID = Playlist.UserID
#     LEFT JOIN SongPlaylist ON Playlist.PlaylistID = SongPlaylist.PlaylistID
#     LEFT JOIN Rating ON SongPlaylist.SongID = Rating.SongID
#     GROUP BY User.UserID, Playlist.PlaylistID
#     HAVING AVG(Rating.RatingValue) >= 4.0;
# ''')
#
# # Fetch the result
# result = cursor.fetchall()
#
# # Print the result
# print("Users with playlists having an average rating of 4.0 or more:")
# print(f"{'Username':<20} {'Playlist Title':<20} {'Average Playlist Rating':<20}")
# print("-" * 60)
# for row in result:
#     print(f"{row[0]:<20} {row[1]:<20} {row[2]:.2f}")
#
#
# cursor.execute('''
#     SELECT User.Username AS username, COUNT(Rating.SongID) AS number_of_ratings
#     FROM User
#     JOIN Rating ON User.UserID = Rating.UserID
#     WHERE Rating.SongID IS NOT NULL AND Rating.AlbumID IS NULL AND Rating.PlaylistID IS NULL
#     GROUP BY User.UserID
#     ORDER BY number_of_ratings DESC
#     LIMIT 5;
# ''')
#
# # Fetch the result
# result = cursor.fetchall()
#
# print("Who are the top 5 users that have rated the most songs?")
# print(f"{'Username':<15} {'Number of Ratings':<15}")
# print("-" * 33)
# for row in result:
#     print(f"{row[0]:<17} {row[1]:<12}")
cursor.execute('''
SELECT Song.Title AS song_title, Artist.Name AS artist_name, COUNT(Rating.SongID) AS number_of_ratings
FROM Song
LEFT JOIN Album ON Song.SongID = Album.SongID
LEFT JOIN Rating ON Song.SongID = Rating.SongID
LEFT JOIN Artist ON Song.ArtistID = Artist.ArtistID
WHERE Album.SongID IS NULL
GROUP BY Song.SongID
ORDER BY number_of_ratings DESC
LIMIT 20;
''')

# Fetch the result
result = cursor.fetchall()

print(f"{'song_title':<15} {'artist_name':<15} {'number_of_ratings':<15}")
print("-" * 45)

for row in result:
    print(f"{row[0]:<15} {row[1]:<15} {row[2]:<15}")

mydb.close()
