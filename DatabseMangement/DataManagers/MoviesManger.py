import pandas as pd


class MoviesManager:
    def __init__(self):
        movies = pd.read_csv('Resources/IMDb_movies.csv')
        movies = movies.fillna('missing value')

        print(movies.shape)

