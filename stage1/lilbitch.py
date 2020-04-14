from selenium import webdriver as driver
from selenium.webdriver.chrome.options import Options
import pickle
from time import sleep

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-setuid-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
#chrome_options.add_argument("--user-data-dir=/mnt/c/Users/rmaloney/AppData/Local/Google/Chrome/User\ Data/Default")
drv = driver.Chrome(chrome_options=chrome_options)
drv.get("http://d158dc83.ngrok.io")
drv.delete_all_cookies()
drv.add_cookie({"name":"username","value":"Joe","domain":"d158dc83.ngrok.io"})
drv.add_cookie({"name":"sessionKey","value":"FLAG_4_QNZKPQ"})

#drv.get("http://www.google.com")
sleep(2)
print(drv.page_source)
#drv.save_screenshot('in.png')
#drv.close()