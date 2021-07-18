# normal library
import requests
import sqlite3

# my package
from my_package.bot.Bot import Bot
from my_package.bot.BotRegister import get_bot_data

from manaba import manaba_scrape

################################# manaba以外をスレイピングする場合はget_manaba_data()、get_homeworks()とmain()を修正する。##########################################

# LINE Notifyで取得messageを送信
def send_message(messages:list, bot:Bot):
    # 取得トークン
    TOKEN = bot.show_data()[3]
    # APIのURL
    api_url = 'https://notify-api.line.me/api/notify'
    # 送る内容
    if not messages:
        send_contents = '未提出のレポート課題はありません'
    else:
        send_contents = ""
        for i in range(len(messages)):
            class_name = messages[i][0]
            report = messages[i][1]
            difftime = messages[i][2]
            send_contents += f"\n授業名：{class_name}\nレポート名：{report}\n期限まで {difftime}\n"

    TOKEN_dic = {'Authorization': 'Bearer' + ' ' + TOKEN}
    send_dic = {'message': send_contents}

    requests.post(api_url, headers=TOKEN_dic, data=send_dic)

def main():
    bot = get_bot_data()
    if bot is not None:
        homework = manaba_scrape()
        if homework is None:
            exit()
        if homework is not None:
            send_message(homework, bot)

if __name__ == '__main__':
    main()
    