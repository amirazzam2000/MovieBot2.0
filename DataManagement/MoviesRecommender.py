import pandas as pd
import datetime as dt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import cosine_similarity
from colors import blue, red, yellow, green
import difflib
import numpy as np 
import math 
import array
from pandas import DataFrame
from  UserManagement.User import User

MALE = 1
FEMALE = 2
NONBINARY = 0

class MoviesManager:
    def __init__(self):
        movies_df = pd.read_csv('Resources/modified_movies.csv',low_memory=False)
        movies_df.sort_values(by=['total_votes'], inplace=True, ascending=False)
        
        self.sub_movies = movies_df[movies_df['language'].str.contains('English', case=False)] 
        self.sub_movies.reset_index(drop=True, inplace=True)

        self.init_TFIDF()


    def init_TFIDF(self):
        tfidf = TfidfVectorizer(stop_words='english')
        #Replace NaN with an empty string
        self.sub_movies['description']=self.sub_movies['description'].fillna('')
        #Construct the required TF-IDF matrix by fitting and transforming the data
        tfidf_matrix = tfidf.fit_transform(self.sub_movies['description'])
        self.cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        self.indices = pd.Series(self.sub_movies.index, index=self.sub_movies['original_title']).drop_duplicates()

    def similarity(self, word, pattern):
        return difflib.SequenceMatcher(a=word.lower(), b=pattern.lower()).ratio()

    def fuzzy_search(self, title):
        threshold = 0.6
        output = []
        outputWeight = []
        for lookup in self.sub_movies['original_title']:
            s =self.similarity(title, lookup) 
            if s > threshold:
                m = self.sub_movies[self.sub_movies['original_title'] == lookup].original_title
                try:
                    output.append(m.item())
                    outputWeight.append(s*10000)
                except Exception:
                    pass
                #print(sub_movies[sub_movies['original_title'] == lookup].original_title)

        zipped_lists = zip(outputWeight,output)
        sorted_zipped_lists = sorted(zipped_lists, reverse=True)
        sorted_list1 = [element for _, element in sorted_zipped_lists]

        return sorted_list1

    def find_similar_based_on_plot(self, title):

        if title in self.indices.keys():
            idx=self.indices[title]
        elif self.fuzzy_search(title)[0] in self.indices.keys():
            idx=self.indices[self.fuzzy_search(title)[0]]
            print("did you mean" ,self.fuzzy_search(title)[0], "?")

        idx = idx[0] if(isinstance(idx, list) or (not np.isscalar(idx)) ) else idx
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:len(sim_scores)]
        #print(sim_scores)
        movie_indices = [[i[0], i[1],  self.sub_movies['original_title'].iloc[i[0]]] for i in sim_scores]

        return movie_indices 

    def getMovieName(self, title):

        if title in self.indices.keys():
            return True, self.sub_movies[self.sub_movies['original_title'] == title].iloc[[0]]
        elif self.fuzzy_search(title)[0] in self.indices.keys():
            print("did you mean" ,self.fuzzy_search(title)[0], "?")
            return False, self.sub_movies[self.sub_movies['original_title'] == self.fuzzy_search(title)[0]].iloc[[0]]


    def getMoveRating(self, movie : DataFrame , age:int, gender:int):
        age_group = [0, 18, 30, 45]
        age_group = [abs(age_group[i]-age) for i in range(len(age_group))]
        group = age_group.index(min(age_group))
        attribute = ""
        attribute2 = ""

        if gender == 0 and age == 0:
            attribute = "avg_vote"
            attribute2 = "avg_vote"
        else:
            if gender == 0:
                attribute += "allgenders_"
                attribute2 += "allgenders_"
                
            elif gender == 1:
                attribute += "males_"
                attribute2 += "males_"
            else:
                attribute += "females_"
                attribute2 += "females_"

            if age == 0:
                attribute += "allages_avg_vote"
                attribute2 += "allages_votes"
            elif group == 0: # group 0
                attribute += "0age_avg_vote"
                attribute2 += "0age_votes"
            elif group == 1: # group 18
                attribute += "18age_avg_vote"
                attribute2 += "18age_votes"
            elif group == 1: # group 30
                attribute += "30age_avg_vote"
                attribute2 += "30age_votes"
            else: #group 45
                attribute += "45age_avg_vote"
                attribute2 += "45age_votes"
        

        avg = movie[attribute].values[0]
        num_voters = movie[attribute2].values[0]

        # rating (WR) = (v ÷ (v+m)) × R + (m ÷ (v+m)) × C 
        # R = average for the movie (mean) = (Rating)
        # v = number of votes for the movie = (votes)
        # m = minimum votes required to be listed in the Top 250 (currently 3000)
        # C = the mean vote across the whole report (currently 6.9)
        M = 3000
        C = 6
        rating = ( num_voters / (num_voters + M )) * avg + (M / (num_voters + M)) * C

        return rating
    
    def similarityFactor(self, movie1: DataFrame, movie2 : DataFrame, script_similarity, age=0, gender=0):
        similarity = 0

        value1 = np.array(movie1['director_encoded'].values[0].strip("[").strip("]").split(), dtype=int)
        value2 = np.array(movie2['director_encoded'].values[0].strip("[").strip("]").split(), dtype=int)
        padding = abs(value1.shape[0] - value2.shape[0])
        value1 = np.pad(value1, ( padding ,0), 'constant') if value1.shape[0] < value2.shape[0] else value1
        value2 = np.pad(value2, ( padding ,0), 'constant') if value1.shape[0] > value2.shape[0] else value2
        
        similarity_factor = 0.1 *difflib.SequenceMatcher(a= value1, b=value2).ratio()
        

        value1 = np.array(movie1['writer_encoded'].values[0].strip("[").strip("]").split(), dtype=int)
        value2 = np.array(movie2['writer_encoded'].values[0].strip("[").strip("]").split(), dtype=int)
        padding = abs(value1.shape[0] - value2.shape[0])
        value1 = np.pad(value1, ( padding ,0), 'constant') if value1.shape[0] < value2.shape[0] else value1
        value2 = np.pad(value2, ( padding ,0), 'constant') if value1.shape[0] > value2.shape[0] else value2
        
        similarity_factor += 0.1 * difflib.SequenceMatcher(a= value1, b=value2).ratio()

        value1 = np.array(movie1['encoded_genre'].values[0].strip("[").strip("]").split(), dtype=int)
        value2 = np.array(movie2['encoded_genre'].values[0].strip("[").strip("]").split(), dtype=int)
        padding = abs(value1.shape[0] - value2.shape[0])
        value1 = np.pad(value1, ( padding ,0), 'constant') if value1.shape[0] < value2.shape[0] else value1
        value2 = np.pad(value2, ( padding ,0), 'constant') if value1.shape[0] > value2.shape[0] else value2
        
        similarity_factor += 0.3 * difflib.SequenceMatcher(a= value1, b=value2).ratio()
        
        r = self.getMoveRating(movie2, age, gender)
        similarity_factor += 0.3 * (r/10)

        
        
        similarity_factor += 0.2 * script_similarity

        
        return similarity_factor , r
    
    def recommend(self, movie):
        recommend_score = 0
        aux = 0
        movies_list = self.find_similar_based_on_plot(movie['original_title'].item())
        movies_list = movies_list[1:math.floor(len(movies_list)*0.1)]
        for m in movies_list: 
            found, name = self.getMovieName(m[2])
            s,r =self.similarityFactor(movie,name, m[1] )
            aux = s
            if aux > recommend_score : 
                recommend_score = aux
                movie_to_recommend = name
        return recommend_score, movie_to_recommend


    def recommend_from_user_list(self, user_movie_list: DataFrame, user_hate_movie_list:DataFrame, user_not_care_movie_list:DataFrame, age = 0, gender = NONBINARY):
        recommend_score = 0
        aux = 0
        the_list = []
        movie_to_recommend = None
        portion = 0.1/len(user_movie_list)
        for index, movie in user_movie_list.iterrows():
            movies_list = self.find_similar_based_on_plot(movie['original_title'])
            movies_list = movies_list[1:math.floor(len(movies_list)*portion)]
            the_list.extend(movies_list)
        the_list = [list(x) for x in set(tuple(x) for x in the_list)]
        the_list = sorted(the_list, key=lambda x: x[1], reverse=True)
        print(len(the_list))
        for m in the_list: 
            found, name = self.getMovieName(m[2])
            if (user_movie_list is not None and  name.original_title.isin(user_movie_list.original_title).astype(bool).all()):
                continue
            if (user_hate_movie_list is not None and name.original_title.isin(user_hate_movie_list.original_title).astype(bool).all()):
                continue
            if (user_not_care_movie_list is not None and name.original_title.isin(user_not_care_movie_list.original_title).astype(bool).all()):
                continue
            aux = 0
            aux_hate = 0
            if user_movie_list is not None:
                for index in range(len(user_movie_list)):
                    user_m = user_movie_list.iloc[[index]]
                    s, r = self.similarityFactor(user_m ,name, m[1], age, gender )
                    aux += s
            if user_hate_movie_list is not None:
                for index in range(len(user_hate_movie_list)):
                    user_m = user_hate_movie_list.iloc[[index]]
                    s, r = self.similarityFactor(user_m ,name, m[1], age, gender )
                    aux_hate += s
            aux = aux - 0.4 * aux_hate
            aux /= len(user_movie_list)
            if aux > recommend_score : 
                recommend_score = aux
                movie_to_recommend = name
                print(r)

        return recommend_score, movie_to_recommend

