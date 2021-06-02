from typing import Any, Text, Dict, List
from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType

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

        name = tracker.get_slot("name")
        if not name:
            dispatcher.utter_message(text="I don't know your name. That's why I call you {name}")
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

        else:
            name = None
            entities = tracker.latest_message['entities']
            for e in entities:
                # print(f"e = {e}")
                if str(e["entity"]) == "PERSON" and "value" in e:
                    name = str(e["value"])
                    break

            if name is None:
                intents = tracker.latest_message['intent']

                if "confidence" not in intents:
                    for i in intents:
                        if str(i["name"]) == "affirm" and float(str(i["confidence"])) > 0.9:
                            return {"permission_name_user": "true"}
                        if str(i["name"]) == "deny" and int(str(i["confidence"])) > 0.9:
                            dispatcher.utter_message(text=f"In that case I'll call you user33")
                            return {"permission_name_user": "false", "name_user": "user33"}
                else:
                    if str(intents["name"]) == "affirm" and float(str(intents["confidence"])) > 0.9:
                        return {"permission_name_user": "true"}
                    if str(intents["name"]) == "deny" and float(str(intents["confidence"])) > 0.9:
                        dispatcher.utter_message(text=f"In that case I'll call you user33")
                        return {"permission_name_user": "false", "name_user": "user33"}

            else:
                dispatcher.utter_message(text=f"It's very nice to meet you {name}!")
                return {"permission_name_user": "true", "name_user": name}

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
            gender = None
            entities = tracker.latest_message['entities']

            for e in entities:
                if str(e["entity"]) == "gender" and "value" in e:
                    gender = str(e["value"])
                    break
            if gender is None:
                intents = tracker.latest_message['intent']

                if "confidence" not in intents:
                    for i in intents:
                        if str(i["name"]) == "affirm" and float(str(i["confidence"])) > 0.9:
                            return {"permission_gender_user": "true"}
                        if str(i["name"]) == "deny" and int(str(i["confidence"])) > 0.9:
                            return {"permission_gender_user": "false", "gender_user": "nonbinary"}
                else:
                    if str(intents["name"]) == "affirm" and float(str(intents["confidence"])) > 0.9:
                        return {"permission_gender_user": "true"}
                    if str(intents["name"]) == "deny" and float(str(intents["confidence"])) > 0.9:
                        return {"permission_gender_user": "false", "gender_user": "nonbinary"}
            else:
                return {"permission_gender_user": "true", "gender_user": gender}

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

        age = None
        entities = tracker.latest_message['entities']
        for e in entities:
            if (e["entity"] == "CARDINAL" or e["entity"] == "age") and "value" in e:
                age = str(e["value"])
                break
        if age is None:
            intents = tracker.latest_message['intent']
            if "confidence" not in intents:
                for i in intents:
                    if str(i["name"]) == "affirm" and float(str(i["confidence"])) > 0.9:
                        return {"permission_age_user": "true"}
                    if str(i["name"]) == "deny" and int(str(i["confidence"])) > 0.9:
                        return {"permission_age_user": "false", "age_user": "0"}
            else:
                if str(intents["name"]) == "affirm" and float(str(intents["confidence"])) > 0.9:
                    return {"permission_age_user": "true"}
                if str(intents["name"]) == "deny" and float(str(intents["confidence"])) > 0.9:
                    return {"permission_age_user": "false", "age_user": "0"}
        else:
            return {"permission_age_user": "true", "age_user": age}

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

        intents = tracker.latest_message['intent']

        if "confidence" not in intents:
            for i in intents:
                if str(i["name"]) == "affirm" and float(str(i["confidence"])) > 0.9:
                    return {"permission_initial_test_user": "true"}
                if str(i["name"]) == "deny" and int(str(i["confidence"])) > 0.9:
                    return {"permission_initial_test_user": "false"}
        else:
            if str(intents["name"]) == "affirm" and float(str(intents["confidence"])) > 0.9:
                return {"permission_initial_test_user": "true"}
            if str(intents["name"]) == "deny" and float(str(intents["confidence"])) > 0.9:
                return {"permission_initial_test_user": "false"}

class ValidateInitialTestForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_initial_test_form"


    def validate_movie_1_initial_test(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:


        # If the name is super short, it might be wrong.
        if len(slot_value) <= 1:
            dispatcher.utter_message(text=f"That's a very short name. I'm assuming you mis-spelled.")
            return {"movie_1": None}

        else:
            dispatcher.utter_message(text=f"Cool movie!")
            # pass name to function
            return {"movie_1": slot_value}

    def validate_movie_2_initial_test(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        # If the name is super short, it might be wrong.
        if len(slot_value) <= 1:
            dispatcher.utter_message(text=f"That's a very short name. I'm assuming you mis-spelled.")
            return {"movie_2": None}

        else:
            dispatcher.utter_message(text=f"Interesting choice")
            # pass name to function
            return {"movie_2": slot_value}

    def validate_movie_3_initial_test(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        # If the name is super short, it might be wrong.
        if len(slot_value) <= 1:
            dispatcher.utter_message(text=f"That's a very short name. I'm assuming you mis-spelled.")
            return {"movie_3": None}

        else:
            dispatcher.utter_message(text=f"Perfect!")
            # pass name to function
            return {"movie_3": slot_value}