import tkinter
from tkinter import ttk
import sqlite3

class WebRegister(tkinter.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('webページ登録フォーム')
        self.master.geometry('500x280')
        self.grid(column=0, row=0, sticky=tkinter.NSEW, padx=5, pady=10)

        self.create_widgets()

        # create table in database
        self.create_table()

    def create_widgets(self):
        # create wedget (page name) and place them
        self.name_label = ttk.Label(self, text='登録ページ名')
        self.name_label.grid(column=0, row=0, pady=7)
        self.name_box = ttk.Entry(self)
        self.name_box.grid(column=1, row=0, sticky=tkinter.EW, padx=5, pady=5, ipady=10)

        # create wedget (page url) and place them
        self.url_label = ttk.Label(self, text='URL')
        self.url_label.grid(column=0, row=1, pady=7)
        self.url_box = ttk.Entry(self)
        self.url_box.grid(column=1, row=1, sticky=tkinter.EW, padx=5, pady=5, ipady=10)

        # create wedget using for login and place them
        self.id_label = ttk.Label(self, text='ID')
        self.id_label.grid(column=0, row=2, pady=7)
        self.id_box = ttk.Entry(self)
        self.id_box.grid(column=1, row=2, sticky=tkinter.EW, padx=5, pady=5, ipady=10)

        self.password_label = ttk.Label(self, text='パスワード')
        self.password_label.grid(column=0, row=3, pady=7)
        self.password_box = ttk.Entry(self, show='*')
        self.password_box.grid(column=1, row=3, sticky=tkinter.EW, padx=5, pady=5, ipady=10)

        self.email_label = ttk.Label(self, text='メールアドレス')
        self.email_label.grid(column=0, row=4, pady=7)
        self.email_box = ttk.Entry(self)
        self.email_box.grid(column=1, row=4, sticky=tkinter.EW, padx=5, pady=5, ipady=10)

        # create buttom and place them
        self.registerBtn = ttk.Button(self, text='登録', command=self.register, state='normal')
        self.registerBtn.grid(column=1, row=5, pady=5)

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

    # create table in my.db
    def create_table(self) -> None:
        conn = sqlite3.connect("my.db")
        c = conn.cursor()
        col_list = ['name', 'url', 'id', 'password', 'email']
        column = []
        for col in col_list:
            column.append(col)
        table_col = ' text,'.join(column)
        c.execute(f"CREATE TABLE IF NOT EXISTS webs ({table_col})")
        conn.commit()
        conn.close()

    def register(self) -> None:
        conn = sqlite3.connect("my.db")
        c = conn.cursor()
        # create table if the table does not exist.
        type_list = []
        for key in self.form_output():
            type_list.append(f':{key}')
        types = ','.join(type_list)
        try:
            # insert data to the database.
            c.execute(f"INSERT INTO webs VALUES ({types})", self.form_output())
            self.quit()
        except:
            pass
        # commit changes to the database.
        conn.commit()
        conn.close()

    def quit(self):
        self.master.destroy()

    def designate_default(self, default_name:str, default_url:str, default_id:str, default_password:str, default_email:str):
        self.name_box.insert(0, default_name)
        self.url_box.insert(0, default_url)
        self.id_box.insert(0, default_id)
        self.password_box.insert(0, default_password)
        self.email_box.insert(0, default_email)

    def form_output(self):
        return {'name':self.name_box.get(), 'url':self.url_box.get(), 'id':self.id_box.get(), 'password':self.password_box.get(), 'email':self.email_box.get()}


def register_web(default_name='', default_url='', default_id='', default_password='', default_email=''):
    root = tkinter.Tk()
    form = WebRegister(root)
    form.designate_default(default_name, default_url, default_id, default_password, default_email)
    form.mainloop()

