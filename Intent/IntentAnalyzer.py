import json


class IntentAnalyzer:

    def __init__(self):
        """
        BAG OF WORDS
        """
        # GREETINGS
        with open("BagOfWords/greeting.txt", "r", encoding="utf8") as f:
            self.greetings = [i.strip() for i in f.readlines()]

        # GOODBYE
        with open("BagOfWords/goodbye.txt", "r", encoding="utf8") as f:
            self.goodbye = [i.strip() for i in f.readlines()]

        """
        INTENT MAPPER
        """
        self.intent = []
        with open('IntentMapper.json') as json_file:
            data = json.load(json_file)
            context = 0
            for intent in data:  # for each question
                self.intent[intent.tag] = [intent.responses, context + 1]


if __name__ == '__main__':
    intentAnalyzer = IntentAnalyzer()
    print("done")
