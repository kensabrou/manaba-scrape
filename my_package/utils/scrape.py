from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

# スクレイプ単純化のための関数のパッケージです

# ボタンのクリック
def button_click(browser, xpath, t=3):
    button = WebDriverWait(browser, t).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    browser.execute_script("arguments[0].click();", button)

# フォーム記入
def input_element(browser, form:dict, t=3):
    for xpath in form:
        element = WebDriverWait(browser, t).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        element.send_keys(form[xpath])
        time.sleep(2)