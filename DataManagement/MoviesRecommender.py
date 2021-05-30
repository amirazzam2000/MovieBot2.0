import pandas as pd
import datetime as dt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import cosine_similarity
import difflib
import numpy as np 
import math 
import array


class MoviesManager:
    def __init__(self):
        movies_df = pd.read_csv('../Resources/modified_movies.csv', low_memory=False)
        movies_df.sort_values(by=['avg_vote'], inplace=True, ascending=False)
        self.rating = pd.read_csv('../Resources/IMDb_ratings.csv', low_memory=False)
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
    def recommendation(self, title):

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
            return True, self.sub_movies[self.sub_movies['original_title'] == title]
        elif self.fuzzy_search(title)[0] in self.indices.keys():
            #print("did you mean" ,self.fuzzy_search(title)[0], "?")
            return False, self.sub_movies[self.sub_movies['original_title'] == self.fuzzy_search(title)[0]]
    
    def similarityFactor(self, movie1:pd.DataFrame, movie2 : pd.DataFrame, script_similarity):
        similarity = 0

        value1 = np.array(movie1['director_encoded'].strip("[").strip("]").split(), dtype=int)
        value2 = np.array(movie2['director_encoded'].strip("[").strip("]").split(), dtype=int)
        padding = abs(value1.shape[0] - value2.shape[0])
        value1 = np.pad(value1, (padding, 0), 'constant') if value1.shape[0] < value2.shape[0] else value1
        value2 = np.pad(value2, (padding, 0), 'constant') if value1.shape[0] > value2.shape[0] else value2
        similarity_factor = 0.1 *difflib.SequenceMatcher(a= value1, b=value2).ratio()

        value1 = np.array(movie1['writer_encoded'].strip("[").strip("]").split(), dtype=int)
        value2 = np.array(movie2['writer_encoded'].strip("[").strip("]").split(), dtype=int)
        padding = abs(value1.shape[0] - value2.shape[0])
        value1 = np.pad(value1, (padding, 0), 'constant') if value1.shape[0] < value2.shape[0] else value1
        value2 = np.pad(value2, (padding, 0), 'constant') if value1.shape[0] > value2.shape[0] else value2
        similarity_factor += 0.1 * difflib.SequenceMatcher(a= value1, b=value2).ratio()

        value1 = np.array(movie1['encoded_genre'].strip("[").strip("]").split(), dtype=int)
        value2 = np.array(movie2['encoded_genre'].strip("[").strip("]").split(), dtype=int)
        padding = abs(value1.shape[0] - value2.shape[0])
        value1 = np.pad(value1, (padding, 0), 'constant') if value1.shape[0] < value2.shape[0] else value1
        value2 = np.pad(value2, (padding, 0), 'constant') if value1.shape[0] > value2.shape[0] else value2
        similarity_factor += 0.3 * difflib.SequenceMatcher(a= value1, b=value2).ratio()

        similarity_factor += 0.1 * ((movie2['avg_vote'] - 6.5)/3.5)
        
        #print( "movies: " ,movie1['original_title'].item(), " : ", movie2['original_title'])
        similarity_factor += 0.4 * script_similarity
        return similarity_factor 
    
    def recommend(self, movie):
        recommend_score = 0
        aux = 0
        movies_list = self.recommendation(movie['original_title'])
        movies_list = movies_list[1:math.floor(len(movies_list)*0.1)]
        for m in movies_list: 
            found, name = self.getMovieName(m[2])
            for index,  n in name.iterrows():
                aux = self.similarityFactor(movie,n, m[1] )
                if aux > recommend_score and n["original_title"] != movie["original_title"]:
                    recommend_score = aux
                    movie_to_recommend = name

        return recommend_score, movie_to_recommend


if __name__ == '__main__':
    MoviesManager = MoviesManager()

    movie = input('Please enter the movie name:')
    found, entry = MoviesManager.getMovieName(movie)

    for index,  e in entry.iterrows():
        score, result = MoviesManager.recommend(e)
        print("similarity factor: ", score)
        #print(result)
        print("movie name: ", result['original_title'].item())
