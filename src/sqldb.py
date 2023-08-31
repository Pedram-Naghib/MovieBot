from dotenv import load_dotenv, find_dotenv
from src.constants import AWARDS
from telebot.types import Message
from src import bot
import sqlite3



# Insert data into the table
def insert_data(data_to_insert):
    '''
    data_to_insert: Title, imdbID, Year, Genre, Runtime, Actors, Plot, Ratings, Type
    '''
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        insert_data_query = '''
        INSERT INTO media (Title, imdbID, Year, Genre, Runtime, Actors, Plot, Ratings, Poster, Type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        '''
        cursor.execute(insert_data_query, data_to_insert)
        conn.commit()


def insert_file(data_to_insert, series=False):
    if series:
        insert_data_query = '''
        INSERT INTO episodes (id, season_number, episode_number, message_id, caption)
        VALUES (?, ?, ?, ?, ?);
        '''
    else:
        insert_data_query = '''
        INSERT INTO movies (file_ids, id, quality, caption)
        VALUES (?, ?, ?, ?);
        '''
        
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        cursor.execute(insert_data_query, data_to_insert)
        conn.commit()


def insert_user(data_to_insert):
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        insert_data_query = '''
        INSERT INTO User (id, username, fname, lname, vip, uses)
        VALUES (?, ?, ?, ?, ?, ?);
        '''
        cursor.execute(insert_data_query, data_to_insert)
        conn.commit()


def update_media(col, value, finder): #ToDo
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        update_query = f'''
        UPDATE Movies
        SET "{col}" = ?
        WHERE imdbID = ?;
        '''

        cursor.execute(update_query, (value, finder))
        conn.commit()
        
# gets data when user is inputing movie/series name in inline
def get_data(title=None):
     with sqlite3.connect('./database.db') as conn:
          cursor = conn.cursor()
          if title:
            insert_data_query = '''
            SELECT * FROM media WHERE LOWER(Title) LIKE '%' || LOWER(?) || '%';
            '''
            data = cursor.execute(insert_data_query, (title,))
          else:
            insert_data_query = '''
            SELECT * FROM media;
            '''
            data = cursor.execute(insert_data_query)

          conn.commit()
          return data
      
      
def add_data(data):
     with sqlite3.connect('./database.db') as conn:
          cursor = conn.cursor()
          insert_data_query = '''
          INSERT INTO media (Title, imdbID, Year, Genre, Runtime, Director, Writers, Actors, Plot, Ratings, Poster, Type)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
          '''
          rating = data['imdbRating'] + ' ' + data['imdbVotes']
          cursor.execute(insert_data_query, (data['Title'], data['imdbID'], data['Year'], data['Genre'],
                                             data['Runtime'], data['Director'], data['Writer'], data['Actors'],
                                             data['Plot'], rating, data['Poster'], data['Type']))
          conn.commit()


def exists(_id):
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        update_query = '''
        SELECT Title FROM media WHERE imdbID = ?;
        '''

        data = cursor.execute(update_query, (_id,))
        conn.commit()
        if list(data):
            return True
        return False


def add_awards(_id, awards):
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()

        for award, years in awards.items():
            for year in years:
                cursor.execute(f"""INSERT INTO awards (id, award, year) VALUES (?, ?, ?);""",
                               (_id, AWARDS[award], year))
        conn.commit()


def get_movie_quals(_id):
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        update_query = '''
        SELECT file_ids, quality, caption FROM movies WHERE id = ?;
        '''

        data = cursor.execute(update_query, (_id,))
        conn.commit()
        return list(data)


def map_id(message_id, file_id):
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        insert_data_query = '''
        INSERT INTO idmap (message_id, file_id)
        VALUES (?, ?);
        '''
        cursor.execute(insert_data_query, (message_id, file_id))
        conn.commit()
# Commit the changes and close the connection

