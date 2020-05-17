import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchWindowException
import chromedriver_binary

# ブラウザ開始
driver = webdriver.Chrome()
driver.get('http://typingx0.net/sushida/play.html?soundless')
time.sleep(20)

# ゲーム開始前処理
canvas = driver.find_element_by_id('#canvas')
ActionChains(driver).move_to_element(canvas).move_by_offset(0, 50).click().perform() # スタートボタン押下
time.sleep(2)
ActionChains(driver).click().perform() # 5000円コースボタン押下
time.sleep(2)
ActionChains(driver).send_keys(Keys.SPACE).perform() # ゲームスタート

# ゲーム実行
for i in range(5000):
 try:
     ActionChains(driver).send_keys('abcdefghijklmnopqrstuvwxyz-!?,').perform()
 except NoSuchWindowException as e:
     break

# スクショ保存
time.sleep(10)
now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
driver.save_screenshot('./result_{0}.png'.format(now))

# ブラウザ終了
time.sleep(5)
driver.quit()

