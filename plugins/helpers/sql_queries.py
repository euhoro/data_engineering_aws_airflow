class SqlQueries:
    
    # Apped or delete load to tables indication(0=append, 1=delete and load)
    APPEND_OR_DELETE_LOAD = 1
    
    # DROP TABLES
    staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
    staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
    songplay_table_drop = "DROP TABLE IF EXISTS songplays"
    user_table_drop = "DROP TABLE IF EXISTS users"
    song_table_drop = "DROP TABLE IF EXISTS songs"
    artist_table_drop = "DROP TABLE IF EXISTS artists"
    time_table_drop = "DROP TABLE IF EXISTS time"

    # CREATE TABLES
    staging_events_table_create= ("""
        CREATE TABLE IF NOT EXISTS staging_events(
        artist VARCHAR,
        auth VARCHAR,
        firstName VARCHAR,
        gender CHAR(1),
        itemInSession INTEGER,
        lastName VARCHAR,
        length FLOAT,
        level VARCHAR,
        location VARCHAR,
        method VARCHAR,
        page VARCHAR,
        registration FLOAT,
        sessionId INTEGER,
        song VARCHAR,
        status INTEGER,
        ts BIGINT,
        userAgent VARCHAR,
        userId INTEGER);
    """)

    staging_songs_table_create = ("""
        CREATE TABLE IF NOT EXISTS staging_songs (
            num_songs INTEGER,
            artist_id VARCHAR,
            artist_latitude FLOAT,
            artist_longitude FLOAT,
            artist_location VARCHAR,
            artist_name VARCHAR,
            song_id VARCHAR,
            title VARCHAR,
            duration FLOAT,
            year INTEGER);
    """)

    songplay_table_create = ("""
        CREATE TABLE IF NOT EXISTS songplay (
        songplay_id VARCHAR NOT NULL PRIMARY KEY,
        start_time TIMESTAMP,
        user_id INTEGER,
        level VARCHAR,
        song_id VARCHAR,
        artist_id VARCHAR,
        session_id INTEGER,
        location VARCHAR,
        user_agent VARCHAR);
    """)

    user_table_create = ("""
        CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER NOT NULL PRIMARY KEY,
        first_name VARCHAR,
        last_name VARCHAR,
        gender CHAR(1),
        level VARCHAR);
    """)

    song_table_create = ("""
        CREATE TABLE IF NOT EXISTS songs (
        song_id VARCHAR NOT NULL PRIMARY KEY,
        title VARCHAR,
        artist_id VARCHAR,
        year INTEGER,
        duration FLOAT);    
    """)

    artist_table_create = ("""
        CREATE TABLE IF NOT EXISTS artists (
        artist_id VARCHAR NOT NULL PRIMARY KEY,
        name VARCHAR,
        location VARCHAR ,
        latitude FLOAT ,
        longitude FLOAT);    
    """)

    time_table_create = ("""
        CREATE TABLE IF NOT EXISTS time (
        start_time TIMESTAMP NOT NULL PRIMARY KEY,
        hour INTEGER,
        day INTEGER,
        week INTEGER,
        month INTEGER,
        year INTEGER,
        weekday VARCHAR);    
    """)

    # STAGING TABLES

    staging_copy = """
        copy staging_events 
        from '{}' 
        ACCESS_KEY_ID '{}'
        SECRET_ACCESS_KEY '{}'
        format as json '{}' 
        compupdate off 
        region '{}';
    """

    # FINAL TABLES


    songplay_table_insert = ("""
        INSERT INTO songplay (
            songplay_id,
            start_time,
            user_id ,
            level ,
            song_id ,
            artist_id ,
            session_id ,
            location ,
            user_agent)
        
        SELECT
            md5(events.sessionid || events.start_time) songplay_id,
            events.start_time, 
            events.userid, 
            events.level, 
            songs.song_id, 
            songs.artist_id, 
            events.sessionid, 
            events.location, 
            events.useragent
            FROM (SELECT TIMESTAMP 'epoch' + ts/1000 * interval '1 second' AS start_time, *
        FROM staging_events
        WHERE page='NextSong') events
        LEFT JOIN staging_songs songs
        ON events.song = songs.title
            AND events.artist = songs.artist_name
            AND events.length = songs.duration
    """)
    
    user_table_insert = ("""
        INSERT INTO users (
            user_id,
            first_name,
            last_name,
            gender,
            level)
            
        SELECT distinct
            se.userId,
            se.firstName,
            se.lastName,
            se.gender,
            se.level
        FROM staging_events se
        WHERE page='NextSong'        
    """)

    song_table_insert = ("""
        INSERT INTO songs (
            song_id,
            title,
            artist_id,
            year,
            duration)
            
        SELECT
            ss.song_id,
            ss.artist_name,
            ss.artist_id,
            ss.year,
            ss.duration
            
        FROM staging_songs ss
    """)

    artist_table_insert = ("""
        INSERT INTO artists (
            artist_id,
            name,
            location,
            latitude,
            longitude)
        SELECT
            ss.artist_id,
            ss.artist_name,
            ss.artist_location,
            ss.artist_latitude,
            ss.artist_longitude
           
        FROM staging_songs ss
    """)

    time_table_insert = ("""
        INSERT INTO time (
            start_time,
            hour,
            day,
            week,
            month,
            year,
            weekday)
         SELECT
            start_time,
            EXTRACT(HOUR FROM start_time),
            EXTRACT(DAY FROM start_time),
            EXTRACT(WEEK FROM start_time),
            EXTRACT(MONTH FROM start_time),
            EXTRACT(YEAR FROM start_time),
            EXTRACT(WEEKDAY FROM start_time)       
         FROM songplay 
    """)
    
    data_quality_tests = [
        {
            'test_sql': "SELECT COUNT(*) FROM {}",
            'expected_result': -1
        }
    ]