from fuzzywuzzy import process
import random
from youtubesearchpython import VideosSearch

def get_gender(string: str) -> int:

    non_binary = ['non-binary', 'other', 'gender fluid' ]
    male = ['male', 'Boy', 'man', 'guy' ]
    female = ['female', 'women', 'gal', 'girl', 'lady']
    
    ratios_nb = process.extract(string, non_binary)[0][1]
    ratios_m = process.extract(string, male)[0][1]
    ratios_f = process.extract(string, female)[0][1]
    
    ratios = [ratios_nb, ratios_m, ratios_f]

    max_value = max(ratios)

    if max_value < 80:
        return ratios.index(max_value), False

    return ratios.index(max_value), True
    




def get_movie_sentence(movie:str)->str:
    
    arr_sentences = [ movie + " is really good",  
                    movie + " is really good",
                    movie + " is very interesting",
                    movie + " is such a good movie",
                    "Good choice! I also like " + movie] 
    n = random.randint(0,len(arr_sentences) - 1)
    return arr_sentences[n]


def get_trailer_url(movie_name: str)->str:

    videosSearch = VideosSearch(movie_name + ' Trailer', limit = 1)

    link = videosSearch.result()['result'][0]['link']

    return link

WAIT = "wait"
MORE = "give_me_more"
ANOTHER = "another_one"
def default_responses(context: str):
    
    wait = [ "Wait one second...🎦", 
            "Looking for a movie 🍿" ,
            "I'm looking for the right movie.🎥", 
            "let me fetch a movie for you! 🎬", 
            "let me think pep pop pep pop 🤖"] 
     
    more = [ "Great! can you give me another movie name!",
            "Sweet! Give me another movie",
            "Another movie you like please",
            "Cool! could you give me another movie please.",
            "awesome ... I would appreciate it if you would give me another movie!",
            "you have a lovely taste! can you tell me another movie you like",
            "nice taste, try giving me one more movie from a different genre this time."]

    recommend_another = [ "ohh sorry ... let me try to find another one!",
                        "Let me see if I can find a movie you would like",
                        "In that case I'll look for another movie.",
                        "Okay! let me look for another one!",
                        "Let me find another movie..."]

    if context == "wait":
        n = random.randint(0,len(wait) - 1)
        return wait[n]
    elif context == "give_me_more":
        n = random.randint(0,len(more) - 1)
        return more[n]
    elif context == "another_one":
        n = random.randint(0,len(recommend_another) - 1)
        return recommend_another[n]