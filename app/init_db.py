import psycopg2
import csv
from difflib import SequenceMatcher

def is_isrc(string):
    '''
    Checks (veeeery naively) if the string argument is a valid ISRC.
    '''
    return len(string) == 12


def similarity_score(a, b):
    '''
    Returns a similarity score between strings a and b.
    '''
    return SequenceMatcher(None, a, b).ratio()


def duration_similarity(m, n):
    '''
    Returns a similarity score between durations m and n.
    '''
    if m == n:
        return 1.0
    if not m and not n:
        return 0.5
    return 0


def connect_to_db(host, dbname, user, password):
    '''
    Connects to the specified DB using provided credentials.
    '''
    return psycopg2.connect(host=host, dbname=dbname, user=user, password=password)


def table_exists(connection, table_name):
    '''
    Returns True if the specified table exists in the database.
    '''
    cursor = connection.cursor()
    query = '''
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_name=%s
    );
    '''
    cursor.execute(query, (table_name,))
    exists = cursor.fetchone()[0]
    cursor.close()
    return exists


def create_sound_recordings_table(connection):
    '''
    Creates the table structure for storing sound recordings.
    '''
    if table_exists(connection, 'sound_recordings'):
        print("Table 'sound_recordings' already exists in your DB.")
        return
    cursor = connection.cursor()
    query = '''
    CREATE TABLE sound_recordings (
        id          serial          PRIMARY KEY,
        isrc        character(12),
        artist      varchar(100),
        title       varchar(100),
        duration    int,
        UNIQUE(isrc, artist, title, duration)
    );
    '''
    cursor.execute(query)
    cursor.close()
    connection.commit()
    print("Table 'sound_recordings' successfully created.\n")


def create_matching_recordings_table(connection):
    '''
    Creates the table structure for storing matching scores.
    '''
    if table_exists(connection, 'matching_recordings'):
        print("Table 'matching_recordings' already exists in your DB.")
        return
    cursor = connection.cursor()
    query = '''
    CREATE TABLE matching_recordings (
        match_id        serial          PRIMARY KEY,
        match_rec_id    int             REFERENCES sound_recordings (id),
        score           real            NOT NULL,
        rec_isrc        character(12),
        rec_artist      varchar(100),
        rec_title       varchar(100),
        rec_duration    int,
        UNIQUE(match_rec_id, rec_isrc, rec_artist, rec_title, rec_duration)
    )
    '''
    cursor.execute(query)
    cursor.close()
    connection.commit()
    print("Table 'matchin_recordings' successfully created.\n")


def store_song_recording(connection, recording):
    '''
    Stores a specific recording in the database.
    '''
    cursor = connection.cursor()
    artist = recording['artist']
    title = recording['title']
    isrc = recording['isrc']
    duration = recording['duration'] if recording['duration'] else 0
    if not is_isrc(isrc):
        print("Warning! The following recording's ISRC either doesn't exist or the format is incorrect.")
        print("It might be an invalid recording.")
    query = '''
    INSERT INTO sound_recordings (artist, title, isrc, duration)
        VALUES (%s, %s, %s, %s);
    '''
    try:
        cursor.execute(query, (artist, title, isrc, duration))
        print("Recording succesfully imported.")
    except psycopg2.IntegrityError:
        print("The recording already exists in the database.")
    cursor.close()
    connection.commit()
    print("\tISRC: {}\n\tTitle: {}\n\tArtist: {}\n\tDuration: {}\n".format(isrc, title, artist, duration))


def store_matching_recordings(connection, rec_id, score, recording):
    '''
    Stores the matching <score> between a new recording and one
    already in the db (<rec_id>).
    '''
    cursor = connection.cursor()
    artist = recording['artist']
    title = recording['title']
    isrc = recording['isrc']
    duration = recording['duration'] if recording['duration'] else 0
    query = '''
    INSERT INTO matching_recordings (
        match_rec_id, 
        rec_artist, 
        rec_title, 
        rec_isrc, 
        rec_duration,
        score
    )
        VALUES (%s, %s, %s, %s, %s, %s);
    '''
    try:
        cursor.execute(query, (rec_id, artist, title, isrc, duration, score))
        print("Matching recordings succesfully saved (with recording {}).".format(rec_id))
    except psycopg2.IntegrityError:
        print("The matching recordings already exist in the database (with recording {}).".format(rec_id))
    cursor.close()
    connection.commit()


def get_artists(connection):
    '''
    Gets unique artists from the db.
    '''
    cursor = connection.cursor()
    query = '''
    SELECT DISTINCT artist FROM sound_recordings;
    '''
    cursor.execute(query)
    artists = cursor.fetchall()
    cursor.close()
    return artists


def get_titles(connection):
    '''
    Gets unique titles from the db.
    '''
    cursor = connection.cursor()
    query = '''
    SELECT DISTINCT title FROM sound_recordings;
    '''
    cursor.execute(query)
    titles = cursor.fetchall()
    cursor.close()
    return titles


def get_all_recordings(connection):
    '''
    Returns all the recordings.
    '''
    cursor = connection.cursor()
    query = '''
    SELECT * 
    FROM sound_recordings;
    '''
    cursor.execute(query)
    recordings = cursor.fetchall()
    cursor.close()
    return recordings


def get_recording_from_isrc(connection, isrc):
    '''
    Returns the recording (if any) with the specified ISRC.
    '''
    cursor = connection.cursor()
    query = '''
    SELECT * 
    FROM sound_recordings 
    WHERE isrc=%s;
    '''
    cursor.execute(query, (isrc,))
    recording = cursor.fetchall()
    cursor.close()
    return recording


def get_recording_from_id(connection, rec_id):
    '''
    Returns the recording (if any) with the specified ISRC.
    '''
    cursor = connection.cursor()
    query = '''
    SELECT * 
    FROM sound_recordings 
    WHERE id=%s;
    '''
    cursor.execute(query, (rec_id,))
    recording = cursor.fetchall()
    cursor.close()
    return recording


def get_recordings_from_artist(connection, artist):
    '''
    Returns the recordings performed by a specific artist.
    '''
    cursor = connection.cursor()
    query = '''
    SELECT * 
    FROM sound_recordings 
    WHERE artist=%s;
    '''
    cursor.execute(query, (artist,))
    recording = cursor.fetchall()
    cursor.close()
    return recording


def match_recording(connection, recording):
    '''
    Given a recording, it matches it against those stored in the db.
    Yields the 
    '''
    isrc = recording['isrc']
    artist = recording['artist']
    title = recording['title']
    duration = recording['duration'] if recording['duration'] else 0
    print("\n")
    print(recording)
    for rec in get_all_recordings(connection):
        score = 100 if isrc == rec[1] else 0
        score += 75 * similarity_score(artist, rec[2])
        score += 50 * similarity_score(title, rec[3])
        score += 25 * duration_similarity(duration, rec[4])
        yield (rec[0], score)
        # if score > 75:
        #     print(rec, score)


def get_recording_from_csv(path_to_csv):
    '''
    Iterator which yields recordings stored in a csv file.
    '''
    with open(path_to_csv) as csv_file:
        reader = csv.reader(csv_file)
        for idx, line in enumerate(reader):
            if idx == 0: continue   # skip CSV title
            recording = {
                'artist': line[0],
                'title': line[1],
                'isrc': line[2],
                'duration': line[3]
            }
            yield recording


def import_csv_recordings(connection, path_to_csv):
    '''
    Imports recordings stored into a CSV file into the database.
    '''
    for recording in get_recording_from_csv(path_to_csv):
        store_song_recording(connection, recording)


def match_csv_recordings(connection, path_to_csv):
    '''
    Matches recordings stored into a CSV file against
    those already stored into the database.
    '''
    for recording in get_recording_from_csv(path_to_csv):
        for recording_id, similarity_score in match_recording(connection, recording):
            store_matching_recordings(connection, recording_id, similarity_score, recording)


if __name__ == "__main__":
    from metamatcher.settings import DATABASES

    default_credentials = DATABASES['default']
    db_host = default_credentials['HOST']
    db_name = default_credentials['NAME']
    db_user = default_credentials['USER']
    db_pass = default_credentials['PASSWORD']
    
    conn = connect_to_db(host=db_host, dbname=db_name, user=db_user, password=db_pass)
    create_sound_recordings_table(conn)
    create_matching_recordings_table(conn)

    sound_recordings_path = './reports/sound_recordings.csv'
    import_csv_recordings(conn, sound_recordings_path)

    recordings_to_match_path = './reports/sound_recordings_input_report.csv'
    match_csv_recordings(conn, recordings_to_match_path)
    
