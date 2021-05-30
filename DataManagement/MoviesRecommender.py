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


class MoviesManager:
    def __init__(self):
        movies_df = pd.read_csv('../Resources/modified_movies.csv',low_memory=False)
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

    
    def similarityFactor(self, movie1:pd.DataFrame, movie2 : pd.DataFrame, script_similarity):
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
        
        similarity_factor += 0.3 * ( (movie2['avg_vote'].values[0])/10 )
        
        similarity_factor += 0.2 * script_similarity

        return similarity_factor 
    
    def recommend(self, movie):
        recommend_score = 0
        aux = 0
        movies_list = self.find_similar_based_on_plot(movie['original_title'].item())
        movies_list = movies_list[1:math.floor(len(movies_list)*0.1)]
        for m in movies_list: 
            found, name = self.getMovieName(m[2])
            aux = self.similarityFactor(movie,name, m[1] )
            if aux > recommend_score : 
                recommend_score = aux
                movie_to_recommend = name
        return recommend_score, movie_to_recommend


if __name__ == '__main__':
    MoviesManager = MoviesManager()
    
    movie=input(blue('Please enter the movie name:'))
    while(movie!="exit"):
        found, entry = MoviesManager.getMovieName(movie)
        score, result = MoviesManager.recommend(entry)
        print(green("similarity factor: "), yellow(score))
        print( green("movie name: "), red(result['original_title'].item() ))
        movie=input(blue('Please enter the movie name (enter "exit" to leave):')) 

