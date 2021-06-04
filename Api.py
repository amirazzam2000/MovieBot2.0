import pickle
from flask import Flask, request
from DataManagement.MoviesRecommender import MoviesManager
import json
import pandas as pd
app = Flask(__name__)
app.config["DEBUG"] = True
#with open("Resources\manger.pkl" , "rb") as file:
#    manager = pickle.loads(file)

manager = MoviesManager.getInstance()
print(manager)


@app.route('/recommend', methods=['GET'])
def home():
    entry = request.args.get('movie_name')
    movie_list_like = request.args.get('like')
    movie_list_like = json.loads(movie_list_like)
    movie_list_hate = request.args.get('hate')
    movie_list_hate = json.loads(movie_list_hate)
    movie_list_not_care = request.args.get('not_care')
    movie_list_not_care = json.loads(movie_list_not_care)
    age = request.args.get('age')
    gender = request.args.get('not_care') 
    genre = "Action"

    like = None
    for string in movie_list_like:
        if like is None:
            like = pd.concat([manager.getMovieName(string)])
        else:
            like = like.append([manager.getMovieName(string)])

    hate = None
    for string in movie_list_hate:
        if hate is None:
            hate = pd.concat([manager.getMovieName(string)])
        else:
            hate = like.append([manager.getMovieName(string)])
    
    not_care = None
    for string in movie_list_not_care:
        if not_care is None:
            not_care = pd.concat([manager.getMovieName(string)])
        else:
            not_care = not_care.append([manager.getMovieName(string)])

    score, result = manager.recommend(entry, like,  hate , not_care, age=age, gender=gender)

    return "{'score' = " + str(score) + ", 'result' =" +  str(result) + "}"

app.run()