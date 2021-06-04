
import json
from typing import Any, Text, Dict, List

import pandas
from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType
import random
import pickle5 as pickle

from UserManagement.User import User

from DataManagement.MoviesRecommender import MoviesManager
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
        if name_user is None:
            dispatcher.utter_message(text=f"Hello stranger!")
            dispatcher.utter_message(text=f"I'm the movie bot.")
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
            entities = tracker.latest_message['entities']
            for e in entities:
                if str(e["entity"]) == "gender" and "value" in e:
                    dispatcher.utter_message(text=f"Okay! Now I'll be able to provide more accurate results.")
                    return {"permission_gender_user": "true", "gender_user": str(e["value"])}

            sentiment =  tracker.latest_message['sentiment'][0]
            if str(sentiment["value"]) == "Positive":
                print("You said YEEES")
                return {"permission_gender_user": "true"}
            if str(sentiment["value"]) == "Negative":
                print("You said NOOOO")
                return {"permission_gender_user": "false", "gender_user": "nonbinary"}

            print("I assume you said NOOOO")
            return {"permission_gender_user": "false", "gender_user": "nonbinary"}

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
            entities = tracker.latest_message['entities']
            for e in entities:
                if str(e["entity"]) == "gender" and "value" in e:
                    dispatcher.utter_message(text=f"Okay! Now I'll be able to provide more accurate results.")
                    return {"gender_user": str(e["value"])}

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
            return {"permission_age_user": "false", "age_user": None}
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
        manager = MoviesManager.getInstance()
        print(manager)
        movies = tracker.latest_message['movies'][0]

        if user is None:
            user = dict()
            user['like_list'] = []
            user['unlike_list'] = []
            user['not_care_list'] = []
            print("setting a value!!")
        else:
            print("already set!")

        # answer a yes no question
        if not_sure is not None:
            entities =  tracker.latest_message['sentiment'][0]

            if str(entities["value"]) == "Positive":
                user['like_list'].append(not_sure)
                if len(user['like_list']) < 3:
                    dispatcher.utter_message(text=f"Could you give me another movie?")
            else: 
                dispatcher.utter_message(text=f"Ohh ... Sorry then could you say the name again?")

            if len(user['like_list']) >= 3:
                dispatcher.utter_message(text=f"Thanks {name_user}")
                return {"movie_initial_test": "true", "user_data": user, "movie_not_sure" : None}
                
            return {"movie_not_sure": None,"movie_initial_test": None , "user_data": user}
        

        dispatcher.utter_message(text=f"let me see")
        found = movies["found"]
        movie = movies["name"]
        if found:
            user['like_list'].append(movie)
            print(f"found = {found}")
            print(f"entry = {movie}")
            dispatcher.utter_message(text=f"Yeah! {movie} is cool")
            # pass name to function
            if len(user['like_list']) >= 3:
                dispatcher.utter_message(text=f"Thanks {name_user}")
                return {"movie_initial_test": "true", "user_data": user}
            dispatcher.utter_message(text=f"Could you give me another movie?")
            return {"movie_initial_test": None , "user_data": user}
            # If the name is super short, it might be wrong.
        else:
            dispatcher.utter_message(text=f"you are reffering to \"{movie}\", right?")
            return {"movie_initial_test": None , "movie_not_sure": movie, "user_data": user}
