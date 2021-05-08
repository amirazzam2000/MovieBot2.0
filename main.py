import time
from Telegram.BotManager import BotManager
from DatabseMangement.DataManagers.MoviesManger import MoviesManager

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

if __name__ == '__main__':
    test_question()
