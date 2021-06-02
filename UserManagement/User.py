from pandas import DataFrame
import pandas as pd

class User:
    LIKE = 1
    DISLIKE = 2
    DONT_CARE = 3

    MALE = 1
    FEMALE = 2
    NONBINARY = 0
    
    def __init__(self):
        self.user_movie_list : DataFrame = None
        self.user_hate_movie_list : DataFrame = None
        self.user_not_care_movie_list : DataFrame = None
    
    def addMovie(self, movie:DataFrame, preference : int):
        if preference == self.LIKE: 
            if self.user_movie_list is None:
                self.user_movie_list = pd.concat([movie])
            else:
                self.user_movie_list = self.user_movie_list.append([movie])

        elif preference == self.DISLIKE:
            if self.user_hate_movie_list is None:
                self.user_hate_movie_list = pd.concat([movie])
            else:
                self.user_hate_movie_list = self.user_hate_movie_list.append([movie])

        else:
            if self.user_not_care_movie_list is None:
                self.user_not_care_movie_list = pd.concat([movie])
            else:
                self.user_not_care_movie_list = self.user_not_care_movie_list.append([movie])

    def print(self):
        print(("like:"))
        if self.user_movie_list is not None:
            for i, m in self.user_movie_list.iterrows():
                print(m.original_title)
        print(("dislike:"))
        if self.user_hate_movie_list is not None:
            for i, m in self.user_hate_movie_list.iterrows():
                print(m.original_title)
        print(("not care:"))
        if self.user_not_care_movie_list is not None:
            for i, m in self.user_not_care_movie_list.iterrows():
                print(m.original_title)

    def getLikeList(self) -> DataFrame:
        return self.user_movie_list

    def getDislikeList(self) -> DataFrame:
        return self.user_hate_movie_list

    def getNotCareList(self) -> DataFrame:
        return self.user_not_care_movie_list 