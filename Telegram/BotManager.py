import json
import requests
import urllib
from DatabseMangement.DatabaseConnector import DatabaseConnector
from NLP.SentimentAnalyzer import SentimentAnalyzer

TOKEN = "1647856948:AAHQuR604ulbthVjdAFCgrROaDiq87_qxE4"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


class BotManager:
    def __init__(self):
        self.url = URL  # comment
        self.database = DatabaseConnector()
        self.sentimentAnalyzer = SentimentAnalyzer()
        self.db = DatabaseConnector()

    def get_url(self, url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def get_json_from_url(self, url):
        content = self.get_url(url)
        js = json.loads(content)
        return js

    def get_updates(self, offset=None):
        url = URL + "getUpdates"
        if offset:
            url += "?offset={}".format(offset)
        js = self.get_json_from_url(url)
        return js

    def get_last_update_id(self, updates):
        update_ids = []
        for update in updates["result"]:
            update_ids.append(int(update["update_id"]))
        return max(update_ids)

    def echo_all(self, updates):
        for update in updates["result"]:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            self.send_message(text, chat)

    def get_last_chat_id_and_text(self, updates):
        num_updates = len(updates["result"])
        last_update = num_updates - 1
        text = updates["result"][last_update]["message"]["text"]
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        return (text, chat_id)

    def send_message(self, text, chat_id):
        text = urllib.parse.quote_plus(text)
        url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
        self.get_url(url)

    def chat(self):
        last_textchat = (None, None)
        flag = False
        intent = -1
        while True:

            text, chat = self.get_last_chat_id_and_text(self.get_updates())

            if (text, chat) != last_textchat:

                if text.lower() == "hello":
                    flag = False

                if not flag:
                    if text.lower() == "hello":

                        if self.db.get_user(chat).empty:  # New user ( not in the database)
                            self.send_message("Welcome! 👋", chat)
                            self.send_message("I'm the movie bot. What's your name?", chat)
                            intent = 1

                        else:  # Existing user
                            self.send_message("Do you want to do a really quick test now?", chat)
                            self.send_message("I just want to know what kind of movies you like 🍿", chat)

                else:
                    if intent == 1:
                        self.send_message("Hi " + text + "! I'm very happy to meet you.", chat)
                        self.db.add_user(chat, text)
                    else:
                        if self.sentimentAnalyzer.analyze_sentence(text) == "Positive":
                            self.send_message("Great 😄", chat)
                            self.send_message("Let's get started", chat)
                        else:
                            self.send_message("Okay! Just let me know if you ever want to do the test", chat)

                flag = not flag
                last_textchat = (text, chat)
