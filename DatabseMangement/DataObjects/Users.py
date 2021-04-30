

class Users:
    def __init__(self):
        self.name = ""
        self.age = -1  # -1 : is not defined, 0 : if the user doesn't want to specify
        self.gender = -1  # -1 : not defined, 0 : non-binary, 1 : female, 2 :male
        self.disliked_movies = []
        self.liked_movies = []
        self.potential_movies = []
        self.conversation_pointer = 0


