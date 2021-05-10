import sqlalchemy as sql
import pandas as pd
import pymysql

pymysql.install_as_MySQLdb()

DIALECT = "mysql"
USER = "MOVIE_USER"
PASS = "MOVIE_USER"
DATABASE = "MOVIES"


class DatabaseConnector:
    def __init__(self):
        engine = sql.create_engine('{}://{}:{}@localhost/{}'.format(DIALECT, USER, PASS, DATABASE))
        self.connection = engine.connect()
        self.metadata = sql.MetaData()

        self.users = sql.Table('USERS', self.metadata, autoload=True, autoload_with=engine)
        self.genres = sql.Table('GENRES', self.metadata, autoload=True, autoload_with=engine)

    # --------- USERS --------- #

    def add_user(self, user_id, name):
        df = self.get_user(user_id)
        if df.size == 0:
            query = sql.insert(self.users).values(id=user_id, name=name)
            self.connection.execute(query)

    def get_user(self, user_id) -> pd.DataFrame:
        query = sql.select([self.users]).where(self.users.columns.id == user_id)
        results = self.connection.execute(query).fetchall()
        df = pd.DataFrame(results)
        if df.size > 0:
            df.columns = results[0].keys()
        return df

    def get_all_users(self) -> pd.DataFrame:
        query = sql.select([self.users])
        results = self.connection.execute(query).fetchall()
        df = pd.DataFrame(results)
        df.columns = results[0].keys()
        return df

    # --------- GENRES --------- #

    def get_all_genres(self) -> pd.DataFrame:
        query = sql.select([self.genres])
        results = self.connection.execute(query).fetchall()
        df = pd.DataFrame(results)
        df.columns = results[0].keys()
        return df

    def get_genre_id_by_name(self, genre):
        query = sql.select(self.genres).where(self.genres.columns.genre == genre)
        results = self.connection.execute(query).fetchall()
        df = pd.DataFrame(results)
        return df
        #if df.size > 0:
         #   return results[0].keys()
        #else:
        #    return None

if __name__ == '__main__':
    db = DatabaseConnector()
    db.add_user(2, "hi")
    if db.get_user(3).empty:
        print("I don't know who you are")
    else:
        print("hi friend")
    print(db.get_all_users())
    print(db.get_all_genres())
    print(db.get_genre_id_by_name('drama'))
