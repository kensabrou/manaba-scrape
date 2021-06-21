# normal library
import json
import sqlite3

class Web:

    def __init__(self, name:str, url:str, id=None, password=None, email=None):
        self.__name = name
        self.__url = url 
        self.__id = id
        self.__password = password
        self.__email = email
    
    # get page data
    def get_pageData(self, key):
        page_dict = {'name':self.__name,
                     'url':self.__url,
                     'id':self.__id,
                     'password':self.__password,
                     'email':self.__email}
        data = page_dict[key]
        return data
