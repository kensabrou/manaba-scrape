# 3rd party
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# normal library
import time
import requests
import sqlite3

# my package
from my_package.web.Web import Web
from my_package.bot.Bot import Bot
from my_package.utils import url, scrape
from my_package.bot.BotRegister import register_bot
from my_package.web.WebRegister import register_web

################################# manaba以外をスレイピングする場合はget_manaba_data()、get_homeworks()とmain()を修正する。##########################################

# LINEアカウント情報を用いてLINE Notifyサービスと連携する
def get_bot_data():
    conn = sqlite3.connect('my.db')
    c = conn.cursor()
    data = None
    bot = None
    try:
        c.execute("SELECT * FROM bots")
        data = c.fetchone()
        if data is None:
            register_bot()
            data = c.fetchone()
    except:
        register_bot()
        c.execute("SELECT * FROM bots")
        data = c.fetchone()
    if data is None:
        conn.close()
        return None
    bot = Bot(data[0], data[1], data[2])
    bot.set_token(data[3])
    conn.commit()
    conn.close()
    return bot

# スクレイピングするwebのdbが存在するかを確認、なければ作成、あればデータを返す
def get_manaba_data() -> Web:
    conn = sqlite3.connect('my.db')
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM webs WHERE name = 'manaba'")
        data = c.fetchone()
        if data is None:
            register_web(default_name='manaba', default_url='https://ct.ritsumei.ac.jp/ct/home')
            c.execute("SELECT * FROM webs WHERE name = 'manaba'")
            data = c.fetchone()
    except:
        register_web(default_name='manaba', default_url='https://ct.ritsumei.ac.jp/ct/home')
        c.execute("SELECT * FROM webs WHERE name = 'manaba'")
        data = c.fetchone()
    web = Web(data[0], data[1], data[2], data[3], data[4])
    conn.commit()
    conn.close()
    return web

# manabaからレポート情報を取得
def get_homeworks() -> list:
    # manabaログイン情報
    web = get_manaba_data()

    # headlessモードで実行
    options = Options()
    options.add_argument('--headless')

    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

    if url.checkURL(web.get_pageData('url')):
        browser.get(web.get_pageData('url'))
        time.sleep(3)
    else:
        register_web(default_name=web.get_pageData('name'), default_id=web.get_pageData('id'), default_password=web.get_pageData('password'))
        return None
    
    form_dict = {'/html/body/div/div[2]/div[1]/form/p[1]/input':web.get_pageData('id'),
                '/html/body/div/div[2]/div[1]/form/p[2]/input':web.get_pageData('password')}
    scrape.input_element(browser, form_dict)
    time.sleep(3)
    scrape.button_click(browser, '/html/body/div/div[2]/div[1]/form/p[3]/input')
    time.sleep(3)

    # コース一覧へ遷移
    try:
        scrape.button_click(browser, '/html/body/div[2]/div[1]/div[5]/div[2]/a/img')
        time.sleep(3)
    except:
        browser.quit()
        print('fail to login. Check your id and password registered.')
        conn = sqlite3.connect('my.db')
        c = conn.cursor()
        c.execute("DELETE FROM webs WHERE name='manaba'")
        conn.commit()
        conn.close()
        register_web(default_name=web.get_pageData('name'), default_url=web.get_pageData('url'))
        return None

    # 受講科目の表示を曜日形式に変更
    scrape.button_click(browser, '/html/body/div[2]/div[2]/div/div[1]/div[2]/ul/li[3]/a')
    time.sleep(3)

    # 科目＆課題
    html = browser.page_source.encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    my_courses = soup.find_all('td', attrs={'class':'course-cell'})
    # print(my_courses[0].prettify())
    homeworks = []
    for course in my_courses:
        # 授業名
        course_name = course.find('a').text.split(' § ')
        name = []
        for cls_name in course_name:
            name.append(cls_name.split(':')[1])
        course_name = ' § '.join(name)
        # 課題
        homework = course.find('img', attrs={'src':'/icon-coursedeadline-on.png'})
        if homework is not None:
            homeworks.append(f'\n{course_name}: レポートがあります')
        else:
            pass
    return homeworks

# LINE Notifyで取得massageを送信
def send_message(messages:list, bot:Bot):
    # 取得トークン
    TOKEN = bot.show_data()[3]
    # APIのURL
    api_url = 'https://notify-api.line.me/api/notify'
    # 送る内容
    if not messages:
        send_contents = '未提出のレポート課題はありません'
    else:
        send_contents = '\n'.join(messages)

    TOKEN_dic = {'Authorization': 'Bearer' + ' ' + TOKEN}
    send_dic = {'message': send_contents}

    requests.post(api_url, headers=TOKEN_dic, data=send_dic)

def main():
    bot = get_bot_data()
    if bot is None:
        bot = get_bot_data()
    if bot is not None:
        homework = None
        while homework is None:
            homework = get_homeworks()
        send_message(homework, bot)

if __name__ == '__main__':
    main()
    