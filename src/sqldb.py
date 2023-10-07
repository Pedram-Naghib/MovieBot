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
        INSERT INTO data (Title, imdbID, Year, Genre, Runtime, Actors, Plot, Ratings, Poster, Type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        '''
        cursor.execute(insert_data_query, data_to_insert)
        conn.commit()


def insert_file(data_to_insert, season_ep=False):
    if season_ep:
        data_to_insert += [season_ep[1:3], season_ep[-2:]]
        data_to_insert = tuple(data_to_insert)
        insert_data_query = '''
        INSERT INTO episodes (file_id, id, quality, caption, season, episode)
        VALUES (?, ?, ?, ?, ?, ?);
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
            SELECT * FROM data WHERE LOWER(Title) LIKE '%' || LOWER(?) || '%' LIMIT 20;
            '''
            data = cursor.execute(insert_data_query, (title,))
            data = list(data)
            if len(data) == 0:
                data = None
          else:
            insert_data_query = '''
            SELECT * FROM data ORDER BY ROWID DESC LIMIT 20;
            '''
            data = cursor.execute(insert_data_query)

          conn.commit()
          return data
      
      
def add_data(data):
     with sqlite3.connect('./database.db') as conn:
          cursor = conn.cursor()
          insert_data_query = '''
          INSERT INTO data (Title, imdbID, Year, Genre, Runtime, Director, Writers, Actors, Plot, Ratings, Poster, Type)
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
        SELECT Title FROM data WHERE imdbID = ?;
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


def get_series_quals(_id, season_ep):
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        season, episode = season_ep[1:3], season_ep[-2:]
        update_query = '''
        SELECT file_id, quality, caption FROM episodes WHERE id = ? AND season = ? AND episode = ?;
        '''

        data = cursor.execute(update_query, (_id, season, episode))
        conn.commit()
        return list(data)
# Commit the changes and close the connection

def season_ep_no(_id, season=False):
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        if season:
            data = cursor.execute("SELECT DISTINCT(episode) FROM episodes WHERE id = ? and season = ?", (_id, season))
        else:
            data = cursor.execute("SELECT DISTINCT(season) FROM episodes WHERE id = ?", (_id,))
        conn.commit()
    return data


def data_count():
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        data = cursor.execute("SELECT COUNT(*) FROM data;")
        return data

# finds movies in a specefic award in a certain year
def award_finder(award, year):
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        query = "SELECT Title, Year, imdbID FROM data WHERE imdbID IN (SELECT id FROM awards WHERE award = ? AND year = ?);"
        
        data = cursor.execute(query, (award, year))
        conn.commit()
        return list(data)


def get_data_by_id(id):
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM data WHERE imdbID = ?;"
        
        data = list(cursor.execute(query, (id,)))
        conn.commit()
        return data


def cd_extra(type, data_to_insert):
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        if type == 'cd':
            query = "INSERT INTO cd (id, fileids, cd_type, caption) VALUES (?, ?, ?, ?);"
            cursor.execute(query, data_to_insert)
        else:
            query = "INSERT INTO extra (id, fileids, type, caption) VALUES (?, ?, ?, ?);"
            cursor.execute(query, data_to_insert)

        conn.commit()


def cd_extra_exists(_id):
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        cd = 'SELECT id FROM cd WHERE id = ?;'
        extra = 'SELECT id FROM extra WHERE id = ?;'

        is_cd = list(cursor.execute(cd, (_id,)))
        is_extra = list(cursor.execute(extra, (_id,)))
        conn.commit()
        result = [is_cd, is_extra]
        return result


def get_cdextra_quals(_id, type):
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        if type == 'cd':
            query = "SELECT fileids, cd_type, caption FROM cd WHERE id = ?;"
            data = cursor.execute(query, (_id,))
        else:
            query = "SELECT fileids, type, caption FROM extra WHERE id = ?;"
            data = cursor.execute(query, (_id,))

        conn.commit()
        return list(data)


def save_user(user):
    with sqlite3.connect("./database.db") as conn:
        cursor = conn.cursor()
        query = "INSERT INTO users (id, username, fname, lname) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (user.id, user.username, user.first_name, user.last_name))
        conn.commit()