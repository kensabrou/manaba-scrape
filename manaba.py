# 3rd party
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# normal library
import time
import datetime
import sqlite3
import tkinter
from tkinter import messagebox

# my package
from my_package.web.Web import Web
from my_package.web.WebRegister import register_web
from my_package.utils import url, scrape

# スクレイピングするwebのdbが存在するかを確認、なければ作成、あればデータを返す
def get_web_data():
    conn = sqlite3.connect('my.db')
    c = conn.cursor()
    data = None
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
    if data is None:
        c.execute("DELETE FROM webs WHERE name='manaba'")
        conn.commit()
        conn.close()
        return None
    web = Web(data[0], data[1], data[2], data[3], data[4])
    conn.commit()
    conn.close()
    return web

# manabaからレポート情報を取得
def manaba_scrape()-> list:
    # manabaログイン情報
    web = get_web_data()
    if web is None:
        return None

    # headlessモードで実行
    options = Options()
    options.add_argument('--headless')

    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

    browser.implicitly_wait(10)

    if url.checkURL(web.get_pageData('url')):
        browser.get(web.get_pageData('url'))
        time.sleep(1)
    else:
        error_message('指定されたページが存在しません。')
        return None

    # ログイン
    form_dict = {'/html/body/div/div[2]/div[1]/form/p[1]/input':web.get_pageData('id'),
                '/html/body/div/div[2]/div[1]/form/p[2]/input':web.get_pageData('password')}
    scrape.input_element(browser, form_dict)
    time.sleep(1)
    scrape.button_click(browser, '/html/body/div/div[2]/div[1]/form/p[3]/input')
    time.sleep(3)

    # コース一覧へ遷移
    try:
        scrape.button_click(browser, '/html/body/div[2]/div[1]/div[5]/div[2]/a/img')
        time.sleep(1)
    except:
        error_message('manabaのログインに失敗しました。')
        browser.quit()
        return None

    # 受講科目の表示を曜日形式に変更
    scrape.button_click(browser, '/html/body/div[2]/div[2]/div/div[1]/div[2]/ul/li[3]/a')
    time.sleep(1)

    # 授業名取得
    html = browser.page_source.encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    my_courses = soup.find_all('td', attrs={'class':'course-cell'})
    my_class = []
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
            my_class.append(f'{course_name}')
        else:
            my_class.append(None)
    time.sleep(1)
   
    # 課題
    report_and_difftime = []
    for inv,class_name in enumerate(my_class):
        # 未提出課題の有無を判定
        classworks = browser.find_elements_by_css_selector("div.courselistweekly-nonborder a")
        class_elem = classworks[inv*2]
        if class_name is not None:
            # 個々の授業にアクセス
            browser.execute_script("arguments[0].click();", class_elem)
            time.sleep(1)
            # レポート欄
            nonsubmit_report = browser.find_element_by_css_selector("div.course-menu-report span.my-unreadcount")
            time.sleep(1)
            if nonsubmit_report is not None:
                course_report = browser.find_element_by_css_selector("a#coursereport")
                browser.execute_script("arguments[0].click();", course_report)
                time.sleep(1)
                report_icon = browser.find_elements_by_css_selector("img[src='/icon-deadline-on.png']")
                reports = browser.find_elements_by_css_selector("h3.report-title a")
                deadlines = browser.find_elements_by_css_selector("td.border.center")
                time.sleep(1)
                for i in range(len(report_icon)):
                    deadline = deadlines[i+3].text
                    dt = datetime.datetime.strptime(deadline, "%Y-%m-%d %H:%M")
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    now = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M")
                    diff = dt - now
                    report_info = (class_name,reports[i].text,diff)
                    report_and_difftime.append(report_info)
                time.sleep(1)
            scrape.button_click(browser, '/html/body/div[2]/div[1]/div[5]/div[2]/a/img', 10)
            time.sleep(3)
    return report_and_difftime

def error_message(text:str):
    conn = sqlite3.connect('my.db')
    c = conn.cursor()
    c.execute("DELETE FROM webs WHERE name='manaba'")
    conn.commit()
    conn.close()
    root = tkinter.Tk()
    root.withdraw()
    messagebox.showerror('エラー',text)
    time.sleep(5)
    root.destroy()

if __name__=='__main__':
    a = manaba_scrape()
    print(a[0])