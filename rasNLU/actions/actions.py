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
            dispatcher.utter_message(text=f"Hello stranger")
            return [SlotSet("new_user", "true")]
        else:
            dispatcher.utter_message(text=f"Hello {name_user}, tell me what I can do for you.")
            return [SlotSet("new_user", "false")]


class ActionSayName(Action):

    def name(self) -> Text:
        return "action_say_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name = tracker.get_slot("name")
        if not name:
            dispatcher.utter_message(text="I don't know your name.")
        else:
            dispatcher.utter_message(text=f"Your name is {name}!")
        return []


class ValidateNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_name_form"

    def validate_name_user(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""

        # If the name is super short, it might be wrong.
        print(f"First name given = {slot_value} length = {len(slot_value)}")
        if len(slot_value) <= 1:
            dispatcher.utter_message(text=f"That's a very short name. I'm assuming you mis-spelled.")
            return {"name_user": None}
        else:
            entities = tracker.latest_message['entities']
            for e in entities:
                if e["entity"].equals("PERSON"):
                    if "value" in e:
                        return {"PERSON": e["value"]}
            print(entities)
            dispatcher.utter_message(text=f"I didn't catch your name. What's your name?")
            return {"name_user": None}

    def validate_gender_user(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `last_name` value."""

        # If the name is super short, it might be wrong.
        print(f"Last name given = {slot_value} length = {len(slot_value)}")
        if len(slot_value) <= 2:
            dispatcher.utter_message(text=f"That's a very short name. I'm assuming you mis-spelled.")
            return {"gender_user": None}
        else:
            return {"gender_user": slot_value}

    def validate_age_user(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `last_name` value."""

        # If the name is super short, it might be wrong.
        print(f"Last name given = {slot_value} length = {len(slot_value)}")
        if len(slot_value) <= 2:
            dispatcher.utter_message(text=f"That's a very short name. I'm assuming you mis-spelled.")
            return {"age_user": None}
        else:
            entities = tracker.latest_message['entities']
            for e in entities:
                if e["entity"].equals("PERSON"):
                    if "value" in e:
                        return {"PERSON": e["value"]}
            print(entities)
            dispatcher.utter_message(text=f"I didn't catch your name. What's your name?")
            return {"age_user": None}
