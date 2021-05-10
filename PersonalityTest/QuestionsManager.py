import json

from PersonalityTest.Question import Question


class QuestionsManager:

    def __init__(self):
        self.questions = []

        with open('questions.json') as json_file:
            data = json.load(json_file)

            for q in data: # for each question
                aux_genres = []

                for g in q['genres']: # for each genre
                    aux_genres.append([g['name'], g['weight']])

                question = Question(q['question'], aux_genres);
                self.questions.append(question)

    def get_questions(self):
        return self.questions


if __name__ == '__main__':
    questionManger = QuestionsManager()
    print("Hi")
