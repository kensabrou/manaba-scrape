from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

import tkinter
from tkinter import ttk
import time
import sqlite3

from my_package.bot.Bot import Bot
from my_package.utils import scrape

class BotRegister(tkinter.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('LineNotify登録フォーム')
        self.master.geometry('500x250')
        self.grid(column=0, row=0, sticky=tkinter.NSEW, padx=5, pady=10)

        self.create_widgets()

    def create_widgets(self) -> dict:
        # create wedget (email add registered in Line) and place them
        self.email_label = ttk.Label(self, text='Lineメールアドレス')
        self.email_label.grid(column=0, row=0, pady=7)
        self.email_box = ttk.Entry(self)
        self.email_box.grid(column=1, row=0, sticky=tkinter.EW, padx=5, pady=5, ipady=7)

        # create wedget (password registered in Line) and place them
        self.password_label = ttk.Label(self, text='Lineパスワード')
        self.password_label.grid(column=0, row=1, pady=7)
        self.password_box = ttk.Entry(self, show='*')
        self.password_box.grid(column=1, row=1, sticky=tkinter.EW, padx=5, pady=5, ipady=7)

        # create wedget (bot name you will use)
        self.name_label = ttk.Label(self, text='Bot名')
        self.name_label.grid(column=0, row=2, pady=7)
        self.name_box = ttk.Entry(self)
        self.name_box.grid(column=1, row=2, sticky=tkinter.EW, padx=5, pady=5, ipady=7)

        # create buttom and place them
        self.registerBtn = ttk.Button(self, text='登録', command=self.certificate_bot)
        self.registerBtn.grid(column=1, row=4, pady=5)

        # set column extension ratio 
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)

        # set row extension ratio
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)

        # make the top level widget correnpond to extension
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
    
    def create_table(self, col_list:list) -> None:
        conn = sqlite3.connect("my.db")
        c = conn.cursor()
        key_list = []
        for key in col_list:
            key_list.append(key)
        table_col = ' text,'.join(key_list)
        c.execute(f"CREATE TABLE IF NOT EXISTS bots ({table_col})")
        conn.commit()
        conn.close()

    def register(self, info_dic:dict, commit=True) -> None:
        
        conn = sqlite3.connect("my.db")
        c = conn.cursor()
        # create table if the table does not exist.
        type_list = []
        for key in info_dic.keys():
            type_list.append(f':{key}')
        types = ','.join(type_list)
        try:
            # insert data to the database.
            c.execute(f"INSERT INTO bots VALUES ({types})", info_dic)
            # self.quit()
        except:
            pass
        # commit changes to the database.
        if commit:
            conn.commit()
        conn.close()

    def certificate_bot(self):
        email = self.email_box.get()
        password = self.password_box.get()
        name = self.name_box.get()
        bot = Bot(email, password, name)
        success = self.create_bot(bot)
        if success:
            info_dic = self.form_output(bot)
            self.register(info_dic)

    def quit(self):
        self.master.destroy()

    def form_output(self, bot:Bot) -> dict:
        email, pw, name, token = bot.show_data()
        return {'line_email':email, 'line_password':pw, 'name':name, 'token':token}

    def create_bot(self, bot:Bot) -> bool:
        # データベースにテーブルを作成
        self.create_table(['line_email', 'line_password', 'name', 'token'])
        # headlessモードで実行
        options = Options()
        options.add_argument('--headless')
        browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        browser.get('https://notify-bot.line.me/ja/')
        time.sleep(2)
        scrape.button_click(browser, '/html/body/div/header/div/div/a')
        time.sleep(2)

        form_dict = {'/html/body/div/div/div/div[1]/form/div[2]/input':bot.show_data()[0],
                        '/html/body/div/div/div/div[1]/form/div[3]/input':bot.show_data()[1]}
        scrape.input_element(browser, form_dict)
        scrape.button_click(browser, '/html/body/div/div/div/div[1]/form/div[4]/input')
        time.sleep(3)

        try:
            code = browser.find_element_by_xpath('/html/body/div[3]/div/div/p[1]').text
            info_dic = self.form_output(bot)
            self.register(info_dic, commit=False)
            self.quit()
        except:
            browser.quit()
            self.quit()
            return False
        time.sleep(2)
        show_auth_code(code)

        scrape.button_click(browser, '/html/body/div/header/div/div/p', t=180)
        time.sleep(2)
        scrape.button_click(browser, '/html/body/div/header/div/div/ul/li[1]/a')
        time.sleep(2)
        scrape.button_click(browser, '/html/body/div/div/section[2]/div[1]/ul/li[1]/a')
        time.sleep(2)
        form_dict = {'/html/body/div/div/section[2]/div[2]/div/div[1]/div[1]/div/input': bot.show_data()[2]} 
        try:
            scrape.input_element(browser, form_dict)
        except:
            browser.quit()
            self.quit()
            return False
        time.sleep(2)

        scrape.button_click(browser, '/html/body/div/div/section[2]/div[2]/div/div[1]/div[2]/div/div[2]/ul/li[1]/div[2]')
        time.sleep(3)
        scrape.button_click(browser, '/html/body/div/div/section[2]/div[2]/div/div[1]/div[3]/ul/li/a')
        time.sleep(3)
        token = browser.find_element_by_xpath('/html/body/div/div/section[2]/div[2]/div/div[2]/div[1]/input').get_attribute('value')
        bot.set_token(token)
        info_dic = self.form_output(bot)
        self.register(info_dic)
        browser.quit()
        self.quit()
        return True

def show_auth_code(code):
    main_window = tkinter.Tk()
    main_window.title('Line認証コード')
    main_window.geometry('250x250')
    main_frame = ttk.Frame(main_window)
    main_frame.grid(column=0, row=0)
    code_label = ttk.Label(main_frame, text=code, font=('', 50))
    code_label.grid(column=0, row=0)
    button = ttk.Button(main_frame, text='認証完了', command=lambda:main_window.destroy())
    button.grid(column=0, row=1, pady=20)
    main_window.grid_columnconfigure(0, weight=1)
    main_window.grid_rowconfigure(0, weight=1)
    main_window.mainloop()


def register_bot():
    root = tkinter.Tk()
    form = BotRegister(root)
    form.mainloop()

if __name__ == '__main__':
    register_bot()