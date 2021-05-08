import json
import requests
import urllib
from DatabseMangement.DatabaseConnector import DatabaseConnector

TOKEN = "1647856948:AAHQuR604ulbthVjdAFCgrROaDiq87_qxE4"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


class BotManager:
    def __init__(self):
        self.url = URL  # comment
        self.database = DatabaseConnector()

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
        while True:
            text, chat = self.get_last_chat_id_and_text(self.get_updates())
            if (text, chat) != last_textchat:
                self.send_message(text, chat)
                last_textchat = (text, chat)
