import json
from typing import Any, Text, Dict, List

import pandas
from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from DataManagement.MoviesRecommender import MoviesManager
from rasa_sdk.events import EventType

import random
import pickle5 as pickle


from UserManagement.User import User
from actions.extra_functions import get_gender, get_movie_sentence , get_trailer_url, default_responses, WAIT, MORE, ANOTHER


import pandas as pd


class BotFavouriteMovie(Action):

    def name(self) -> Text:
        return "action_bot_favourite_movie"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Yesterday")

        return []


class Greet(Action):

    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name_user = tracker.get_slot("name_user")
        manager = MoviesManager.getInstance()
        print(manager)
        if name_user is None:
            dispatcher.utter_message(text=f"Hello stranger! 👋")
            dispatcher.utter_message(text=f"I'm the movie bot. 🤖")
            return [SlotSet("new_user", "true")]
        else:
            dispatcher.utter_message(text=f"Hello {name_user}! Tell me, what can I do for you?")
            return [SlotSet("new_user", "false")]


class ActionSayName(Action):

    def name(self) -> Text:
        return "action_say_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name = tracker.get_slot("name_user")
        if not name:
            dispatcher.utter_message(text=f"I don't know your name. That's why I call you {name}")
        else:
            dispatcher.utter_message(text=f"Your name is {name}!")
        return []

class RecommendGenre(Action):

    def name(self) -> Text:
        return "action_recommend_genre"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name = tracker.get_slot("recommend_genre")
        
        sentiment =  tracker.latest_message['sentiment'][0]
        if str(sentiment["value"]) == "Positive":
                print("I'm positive")
                return [SlotSet("recommend_genre",name)]
        else:
                print("I'm negative")
                return [SlotSet("recommend_genre","")]


class ValidateUserForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_user_form"

    def validate_permission_name_user(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        # If the name is super short, it might be wrong.
        if len(slot_value) <= 1:
            dispatcher.utter_message(text=f"That's a very short response... I'm assuming you mis-spelled.")
            return {"permission_gender_user": None}
        else:
            entities = tracker.latest_message['entities']
            for e in entities:
                if str(e["entity"]) == "PERSON":
                    if "value" in e:
                        name = str(e["value"])
                        dispatcher.utter_message(text=f"It's very nice to meet you {name}!")
                        return {"permission_name_user": "true", "name_user": name}

            sentiment =  tracker.latest_message['sentiment'][0]
            if str(sentiment["value"]) == "Positive":
                return {"permission_name_user": "true"}
            if str(sentiment["value"]) == "Negative":
                n = random.randint(0,1000)
                name = "user" + str(n)
                dispatcher.utter_message(text=f"Then I'm going to call you {name}!")
                return {"permission_name_user": "false", "name_user": name}



            return {"permission_gender_user": "false"}


    def validate_name_user(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        # If the name is super short, it might be wrong.
        if len(slot_value) <= 1:
            dispatcher.utter_message(text=f"That's a very short name. I'm assuming you mis-spelled.")

        else:
            entities = tracker.latest_message['entities']
            for e in entities:
                if str(e["entity"]) == "PERSON":
                    if "value" in e:
                        name = str(e["value"])
                        dispatcher.utter_message(text=f"It's very nice to meet you {name}!")
                        return {"name_user": name}

            dispatcher.utter_message(text=f"I didn't catch your name. Make sure it's capitalized")
            return {"name_user": None}

    def validate_permission_gender_user(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        # If the name is super short, it might be wrong.

        if len(slot_value) <= 1:
            dispatcher.utter_message(text=f"That's a very short response... I'm assuming you mis-spelled.")

        else:
            gender, found = get_gender(slot_value)
            if found:
                return {"permission_gender_user": "true", "gender_user": str(gender)}

            sentiment =  tracker.latest_message['sentiment'][0]
            if str(sentiment["value"]) == "Positive":
                return {"permission_gender_user": "true"}
            if str(sentiment["value"]) == "Negative":
                return {"permission_gender_user": "false", "gender_user": "0"}

            return {"permission_gender_user": "false", "gender_user": "0"}

    def validate_gender_user(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        # If the name is super short, it might be wrong.
        if len(slot_value) <= 2:
            dispatcher.utter_message(text=f"Could you say that again? I'm assuming you mis-spelled.")
            return {"gender_user": None}
        else:
            gender, found = get_gender(slot_value)
            if found:
                return {"gender_user": str(gender)}

            dispatcher.utter_message(text=f"I didn't catch that. Could you say that again?")
            return {"gender_user": None}

    def validate_permission_age_user(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        sentiment =  tracker.latest_message['sentiment'][0]
        entities = tracker.latest_message['entities']
        for e in entities:
            if (e["entity"] == "CARDINAL" or e["entity"] == "age") and "value" in e:
                return {"permission_age_user": "true", "age_user": str(e["value"])}

        if str(sentiment["value"]) == "Positive":
            return {"permission_age_user": "true"}
        if str(sentiment["value"]) == "Negative":
            return {"permission_age_user": "false", "age_user": "0"}
        return {"permission_age_user": "true"}

    def validate_age_user(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        entities = tracker.latest_message['entities']
        for e in entities:
            if (e["entity"] == "CARDINAL" or e["entity"] == "age") and "value" in e:
                return {"age_user": str(e["value"])}
        dispatcher.utter_message(text=f"I didn't catch your age. Could you say it again?")
        return {"age_user": None}

    def validate_permission_initial_test_user( 
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        entities =  tracker.latest_message['sentiment'][0]

        if str(entities["value"]) == "Positive":
            return {"permission_initial_test_user": "true"}

        elif str(entities["value"]) == "Negative":
            return {"permission_initial_test_user": "false"}

        return {"permission_initial_test_user": "true"}

    def validate_year_user( 
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        entities =  tracker.latest_message['sentiment'][0]

        if str(entities["value"]) == "Positive":
            return {"year_user": "true"}

        elif str(entities["value"]) == "Negative":
            return {"year_user": "false"}

        return {"year_user": "true"}


class ValidateInitialTestForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_initial_test_form"

    def validate_movie_initial_test(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        user = tracker.get_slot("user_data")
        
        not_sure = tracker.get_slot("movie_not_sure")
        name_user = tracker.get_slot("name_user")
        last_movie = tracker.get_slot("last_movie")
        check_last_movie_intent = tracker.get_slot("check_last_movie_intent")
        movies = tracker.latest_message['movies'][0]
        sentiment =  tracker.latest_message['sentiment'][0]

        age = tracker.get_slot("age_user")
        gender = tracker.get_slot("gender_user")
        year = tracker.get_slot("year_user")

        if year is None:
            year = False
            
        if age is None:
            age = 0

        if gender is None:
            gender = 0

        manager = MoviesManager.getInstance()
        print(manager)
        if user is None:
            user = dict()
            user['like_list'] = []
            user['unlike_list'] = []
            user['not_care_list'] = []
            print("setting a value!!")
        else:
            print("already set!")

        print("like:")
        if user['like_list'] is not None:
            for m in user['like_list']:
                print(m)
        print()
        print("unlike:")
        if user['unlike_list'] is not None:
            for m in user['unlike_list']:
                print(m)
        print()
        print("not care:")
        if user['not_care_list'] is not None:
            for m in user['not_care_list']:
                print(m)
        print()

        if (len(user['like_list']) + len(user['unlike_list'])+ len(user['not_care_list']) ) >= 6:
                dispatcher.utter_message(text=f"Thanks {name_user}")
                return {"movie_initial_test": "true", "user_data": user, "movie_not_sure" : "true",  "check_last_movie_intent" : "false", "last_movie" : ".."}
    
        if check_last_movie_intent is not None : 
                
            if str(sentiment["value"]) == "Positive":                    
                user['like_list'].append(last_movie)
            elif str(sentiment["value"]) == "Negative":
                user['unlike_list'].append(last_movie)
            else:
                user['not_care_list'].append(last_movie)

            if (len(user['like_list']) + len(user['unlike_list'])+ len(user['not_care_list']) ) < 6:
                dispatcher.utter_message(default_responses(MORE))
            else:
                dispatcher.utter_message(text=f"Thanks {name_user}")
                return {"movie_initial_test": "true", "user_data": user, "movie_not_sure" : "true",  "check_last_movie_intent" : "false", "last_movie" : ".."}

            return {"user_data": user, "movie_initial_test":None, "check_last_movie_intent" : None , "movie_not_sure": None}
            
        # answer a yes no question
        if not_sure is not None:
            entities =  tracker.latest_message['sentiment'][0]

            if str(entities["value"]) == "Positive":
                user['like_list'].append(not_sure)
                dispatcher.utter_message(default_responses(WAIT))
                score, result = manager.recommend(not_sure,  user['like_list'] ,user['unlike_list'],user['not_care_list'], age=int(age), gender=gender)
                dispatcher.utter_message(text=f"based on this movie do you think you like {result.original_title.item()}?")
                dispatcher.utter_message(text=f"Here is a link to the trailer: {get_trailer_url(result.original_title.item())}")
                dispatcher.utter_message(text=f"Do you think you'll like this movie?")
                return {"movie_initial_test": None , "user_data": user, "check_last_movie_intent" : "true", "last_movie" : result.original_title.item()}
            else: 
                dispatcher.utter_message(text=f"Ohh ... Sorry then could you say the name again?")

            
                
            return {"movie_not_sure": None,"movie_initial_test": None , "user_data": user, "last_movie" : None, "check_last_movie_intent" : None }
        

        dispatcher.utter_message(text=f"let me see")
        found = movies["found"]
        movie = movies["name"]
        if found:
            user['like_list'].append(movie)
            
            print(f"found = {found}")
            print(f"entry = {movie}")
            
            dispatcher.utter_message(text=get_movie_sentence(movie))
            dispatcher.utter_message(default_responses(WAIT))
            score, result = manager.recommend(movie,  user['like_list'] ,user['unlike_list'],user['not_care_list'], int(age), gender=0)
            dispatcher.utter_message(text=f"I think you might like {result.original_title.item()}")
            dispatcher.utter_message(text=f"Here is a link to the trailer: {get_trailer_url(result.original_title.item())}")
            dispatcher.utter_message(text=f"Do you think you'll like this movie?")
            return {"movie_initial_test": None , "user_data": user, "check_last_movie_intent" : "true"  , "last_movie" : result.original_title.item()}
        
        else:
            dispatcher.utter_message(text=f"you are reffering to \"{movie}\", right?")
            return {"movie_initial_test": None , "movie_not_sure": movie, "user_data": user, "last_movie" : None, "check_last_movie_intent" : None }



class ValidateMovieForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_movie_form"

    def validate_permission_genre_movie(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        entities =  tracker.latest_message['sentiment'][0]
        genres =  tracker.latest_message['genres'][0]
        found = genres["found"]
        genre = genres["name"]
        
        user = tracker.get_slot("user_data")
        age = tracker.get_slot("age_user")
        gender = tracker.get_slot("gender_user")
        year = tracker.get_slot("year_user")

        if year is None:
            year = False
            
        if age is None:
            age = 0

        if gender is None:
            gender = 0

        manager = MoviesManager.getInstance()
        print(manager)
        if user is None:
            user = dict()
            user['like_list'] = ['The Avengers']
            user['unlike_list'] = ['The Shining']
            user['not_care_list'] = ['12 Angry Men']
            print("setting a value!!")
        else:
            print("already set!")

        print("like:")
        if user['like_list'] is not None:
            for m in user['like_list']:
                print(m)
        print()
        print("unlike:")
        if user['unlike_list'] is not None:
            for m in user['unlike_list']:
                print(m)
        print()
        print("not care:")
        if user['not_care_list'] is not None:
            for m in user['not_care_list']:
                print(m)
        print()

        print("HELOOOO I'm here: ",found)
        if found:
            print(genre)
            dispatcher.utter_message(default_responses(WAIT))
            score, result = manager.recommend_from_user_list(user['like_list'] ,user['unlike_list'],user['not_care_list'], age=int(age), gender=int(gender), genre=genre, time_important=year)
            dispatcher.utter_message(text=f"I think you might like {result.original_title.item()}")
            dispatcher.utter_message(text=f"Here is a link to the trailer: {get_trailer_url(result.original_title.item())}")
            dispatcher.utter_message(text=f"Do you think you'll like this movie?")
            return {"permission_genre_movie": "true", "recommend_genre_movie" : genre, "check_last_movie_intent" : "true", "last_movie" : result.original_title.item(), "recommend_movie_movie": None}

        if str(entities["value"]) == "Positive":
            print( "what a lovely user!")
            return {"permission_genre_movie": "true", "recommend_genre_movie" : None, "recommend_movie_movie" : None, "check_last_movie_intent" : None, "last_movie" : None}

        elif str(entities["value"]) == "Negative":
            print("No genre given! rude...")
            dispatcher.utter_message(default_responses(WAIT))
            score, result = manager.recommend_from_user_list(user['like_list'] ,user['unlike_list'],user['not_care_list'], age=int(age), gender=int(gender), genre=None, time_important=year)
            dispatcher.utter_message(text=f"I think you might like {result.original_title.item()}")
            dispatcher.utter_message(text=f"Here is a link to the trailer: {get_trailer_url(result.original_title.item())}")
            dispatcher.utter_message(text=f"Do you think you'll like this movie?")
            return {"permission_genre_movie": "false", "recommend_genre_movie" : "", "check_last_movie_intent" : "true", "last_movie" : result.original_title.item(), "recommend_movie_movie": None}

        
        return {"permission_genre_movie": "true", "recommend_movie_movie" : None ,"recommend_genre_movie" : None , "check_last_movie_intent" : None, "last_movie" : None}  
 

    def validate_recommend_genre_movie(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
    
        genres =  tracker.latest_message['genres'][0]
        movies = tracker.latest_message['movies'][0]
        found = genres["found"]
        genre = genres["name"]

        user = tracker.get_slot("user_data")
        age = tracker.get_slot("age_user")
        year = tracker.get_slot("year_user")
        if year is None:
            year = False
        gender = tracker.get_slot("gender_user")

        if age is None:
            age = 0

        if gender is None:
            gender = 0

        manager = MoviesManager.getInstance()
        if user is None:
            user = dict()
            user['like_list'] = ['The Avengers']
            user['unlike_list'] = ['The Shining']
            user['not_care_list'] = ['12 Angry Men']
            print("setting a value!!")
        else:
            print("already set!")

        print("like:")
        if user['like_list'] is not None:
            for m in user['like_list']:
                print(m)
        print()
        print("unlike:")
        if user['unlike_list'] is not None:
            for m in user['unlike_list']:
                print(m)
        print()
        print("not care:")
        if user['not_care_list'] is not None:
            for m in user['not_care_list']:
                print(m)
        print()

        if found:
            print(genre)
            dispatcher.utter_message(default_responses(WAIT))
            score, result = manager.recommend_from_user_list(user['like_list'] ,user['unlike_list'],user['not_care_list'], age=int(age), gender=int(gender), genre=genre, time_important=year)
            dispatcher.utter_message(text=f"I think you might like {result.original_title.item()}")
            dispatcher.utter_message(text=f"Here is a link to the trailer: {get_trailer_url(result.original_title.item())}")
            dispatcher.utter_message(text=f"Do you think you'll like this movie?")
            return {"recommend_genre_movie" : genre, "check_last_movie_intent" : "true", "last_movie" : result.original_title.item(), "recommend_movie_movie": None}

        else:
            return {"recommend_genre_movie": None, "check_last_movie_intent" : None, "last_movie" : None}
        
        
    def validate_recommend_movie_movie(  
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:   
        
        user = tracker.get_slot("user_data")
        age = tracker.get_slot("age_user")
        gender = tracker.get_slot("gender_user")
        year = tracker.get_slot("year_user")
        if year is None:
            year = False
        if age is None:
            age = 0

        if gender is None:
            gender = 0
        last_movie = tracker.get_slot("last_movie")
        genre = tracker.get_slot("recommend_genre_movie")
        if genre == "":
            genre = None
        check_last_movie_intent = tracker.get_slot("check_last_movie_intent")
        sentiment =  tracker.latest_message['sentiment'][0]


        manager = MoviesManager.getInstance()
        print(manager)
        if user is None:
            user = dict()
            user['like_list'] = ['The Avengers']
            user['unlike_list'] = ['The Shining']
            user['not_care_list'] = ['12 Angry Men']
            print("setting a value!!")
        else:
            print("already set!")

        print("like:")
        if user['like_list'] is not None:
            for m in user['like_list']:
                print(m)
        print()
        print("unlike:")
        if user['unlike_list'] is not None:
            for m in user['unlike_list']:
                print(m)
        print()
        print("not care:")
        if user['not_care_list'] is not None:
            for m in user['not_care_list']:
                print(m)
        print()


        if str(sentiment["value"]) == "Positive":                    
            user['like_list'].append(last_movie)
            dispatcher.utter_message(text=f"I am glad to hear that you like this movie! 😄")
            return {"recommend_movie_movie" : "true", "recommend_genre_movie": None, "permission_genre_movie": None}
        elif str(sentiment["value"]) == "Negative":
            user['unlike_list'].append(last_movie)
            dispatcher.utter_message(default_responses(ANOTHER))
            score, result = manager.recommend_from_user_list(user['like_list'] ,user['unlike_list'],user['not_care_list'], age=int(age), gender=int(gender), genre=genre, time_important=year)
            dispatcher.utter_message(text=f"Would you be interested in {result.original_title.item()}")
            dispatcher.utter_message(text=f"Here is a link to the trailer: {get_trailer_url(result.original_title.item())}")
            dispatcher.utter_message(text=f"Do you think you'll like this movie?")
            return {"check_last_movie_intent" : None, "last_movie" :  result.original_title.item(), "recommend_movie_movie" : None}
        else:
            user['not_care_list'].append(last_movie)
            
            dispatcher.utter_message(default_responses(ANOTHER))
            score, result = manager.recommend_from_user_list(user['like_list'] ,user['unlike_list'],user['not_care_list'], age=int(age), gender=int(gender), genre=genre, time_important=year)
            dispatcher.utter_message(text=f"Would you be interested in {result.original_title.item()}")
            dispatcher.utter_message(text=f"Here is a link to the trailer: {get_trailer_url(result.original_title.item())}")
            dispatcher.utter_message(text=f"Do you think you'll like this movie?")
            return {"check_last_movie_intent" : None, "last_movie" :  result.original_title.item(), "recommend_movie_movie" : None}

