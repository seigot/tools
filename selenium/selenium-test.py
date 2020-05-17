# coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import chromedriver_binary

# ブラウザを開く。
driver = webdriver.Chrome()
# Googleの検索TOP画面を開く。
driver.get("https://www.google.co.jp/")

# 検索語として「selenium」と入力し、Enterキーを押す。
search = driver.find_element_by_name('q') 
search.send_keys("selenium automation")
search.send_keys(Keys.ENTER)
# タイトルに「Selenium - Web Browser Automation」と一致するリンクをクリックする。
#element = driver.find_element_by_partial_link_text("SeleniumHQ Browser Automation")
#element = driver.find_element_by_link_text("WebDriver")
element = driver.find_element_by_partial_link_text("Selenium")
element.click()

# 5秒間待機してみる。
sleep(5)
# ブラウザを終了する。
driver.close()
