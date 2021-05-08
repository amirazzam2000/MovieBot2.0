class Question:


    def __init__(self, question, genres):
        self.question = question
        self.genres = genres

    def get_question(self):
        return self.question

    def get_genres(self):
        return self.genres