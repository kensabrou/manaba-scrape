class Bot:
    
    def __init__(self, email, password, bot_name):
        self.__email = email
        self.__password = password
        self.__name = bot_name
        self.__token = None

    def set_token(self, token):
        self.__token = token

    def show_data(self):
        return self.__email, self.__password, self.__name, self.__token
