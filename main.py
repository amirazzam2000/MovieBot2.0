import time

from Telegram.BotManager import BotManager

from  UserManagement.User import User
from colors import blue, red, yellow, green
from DataManagement.MoviesRecommender import MoviesManager

def main():
    bot = BotManager()
    last_update_id = None
    while True:
        updates = bot.get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = bot.get_last_update_id(updates) + 1
            bot.echo_all(updates)
        time.sleep(0.5)


def test_main():
    movies = MoviesManager()

def test_question():
    bot = BotManager()
    bot.chat()


def recommend():
    manager = MoviesManager()
    user = User()
    
    age=int(input(blue('what is your age: ')))
    gender=int(input(blue('what is your gender (0. nonbinary / 1. male / 2. female):')))

    movie=input(blue('Please enter the name of a movie that you like:'))
    found, entry = manager.getMovieName(movie)
    user.addMovie(entry, user.LIKE)

    while(True):
        movie=input(blue('Please enter the name of a movie (enter "exit" to leave / enter "recommend" to recommend a movie):'))
        if (movie == "recommend"):
            score, result = manager.recommend_from_user_list(user.getLikeList(),user.getDislikeList(),user.getNotCareList(), age=age, gender=gender)
            print(green("similarity factor: "), yellow(score))
            print( green("movie name: "), red(result['original_title'].item()))

            like=int(input(blue('do you like this movie (1. yes / 2. no / 3. don\'t care about it):')))
            user.addMovie(result, like)
        elif movie == "exit":
            break
        else:
            found, entry = manager.getMovieName(movie)
            like=int(input(blue('do you like this movie (1. yes / 2. no / 3. don\'t care about it):')))
            user.addMovie(entry, like)
        
        user.print()

if __name__ == '__main__':
    # sentimentAnalysis = SentimentAnalyzer()
    # questionManger = QuestionsManager()
    recommend()
