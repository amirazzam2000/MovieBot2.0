import time

from Telegram.BotManager import BotManager

from  UserManagement.User import User
from colors import blue, red, yellow, green
from DataManagement.MoviesRecommender import MoviesManager
import pickle
import time

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
    init_time = time.time()
    user = User()
    try:
        with open('Resources/manger.pkl', 'rb') as file:
            manager = pickle.load(file)
            print("reading from file")
    except IOError:
        manager = MoviesManager()
    print(time.time()-init_time)
    age=int(input(blue('what is your age: ')))
    gender=int(input(blue('what is your gender (0. nonbinary / 1. male / 2. female):')))
    time_aux=(input(blue('do you care about the year the movie came out? (y/n): ')))
    if(time_aux == "y"):
        time_important = True
    else:
        time_important = False

    movie=input(blue('Please enter the name of a movie that you like:'))
    found, entry = manager.getMovieName(movie)
    user.addMovie(entry, user.LIKE)

    movie=input(blue('Please enter the name of a movie that you like:'))
    found, entry2 = manager.getMovieName(movie)
    user.addMovie(entry2, user.LIKE)

    movie=input(blue('Please enter the name of a movie that you like:'))
    found, entry3 = manager.getMovieName(movie)
    while not found:
        movie=input(blue('Sorry I didn\'t get that please enter the name of a movie that you like:'))
        found, entry3 = manager.getMovieName(movie)
    user.addMovie(entry3, user.LIKE)

    score, result = manager.recommend(entry, user.getLikeList(),user.getDislikeList(),user.getNotCareList(), age=age, gender=gender)
    print(green("similarity factor: "), yellow(score))
    print( green("movie name : "), red(result['original_title'].item()))
    like=int(input(blue('do you like this movie (1. yes / 2. no / 3. don\'t care about it):')))
    user.addMovie(result, like)

    score, result = manager.recommend(entry2, user.getLikeList(),user.getDislikeList(),user.getNotCareList(), age=age, gender=gender)
    print(green("similarity factor: "), yellow(score))
    print( green("movie name : "), red(result['original_title'].item()))
    like=int(input(blue('do you like this movie (1. yes / 2. no / 3. don\'t care about it):')))
    user.addMovie(result, like)

    score, result = manager.recommend(entry3, user.getLikeList(),user.getDislikeList(),user.getNotCareList(), age=age, gender=gender)
    print(green("similarity factor: "), yellow(score))
    print( green("movie name : "), red(result['original_title'].item()))
    like=int(input(blue('do you like this movie (1. yes / 2. no / 3. don\'t care about it):')))
    user.addMovie(result, like)

    print(blue('the test is now over you can write "recommend" to get a recommendation or add more movies you like/hate'))

    while(True):
        genre = input(blue('what genre of movies you feel like watching today:'))
        movie = input(blue('Please enter the name of a movie (enter "exit" to leave / enter "recommend" to recommend a movie):'))
        if (movie == "recommend"):
            score, result = manager.recommend_from_user_list(user.getLikeList(),user.getDislikeList(),user.getNotCareList(), age=age, gender=gender, genre=genre, time_important=time_important)
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
'''
coraline: 

like:
Avatar
Hacksaw Ridge
Hidden Figures
The Martian
Harry Potter and the Goblet of Fire
The Untouchables
Arrival
X-Men: Days of Future Past
In the Family
Lucy
12 Years a Slave
Slumdog Millionaire
The Imitation Game
The Lord of the Rings: The Return of the King
The Lord of the Rings: The Two Towers
The Lord of the Rings: The Fellowship of the Ring

pentagon papers
bridge of spies
Sully
Da Vinci Code
The polar Express
Rise of the Guardians
Now you see me
Invictus
The Intern
The Devil Wears Prada
Mamma Mia!

dislike:
Harry Potter and the Deathly Hallows: Part 1
Allegiant
Justice League
Dark Phoenix
Aquaman
Schindler's List
Letters from Iwo Jima
not care:
'''