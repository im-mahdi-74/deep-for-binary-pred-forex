
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
 
from enum import Enum
import os 

import chromedriver_autoinstaller
import undetected_chromedriver

#Settings
HIDDEN_CHROME = False
UNDETECTED_CHROME = False  #use this if the website detects bot

#Constants
WEBSITE_URL = 'https://pocketoption.com/en/cabinet'
DATA_FOLDER_NAME = 'pocketoption_data'
HOME_DIR = os.path.expanduser('~')
DATA_DIR = os.path.join(HOME_DIR,DATA_FOLDER_NAME)

#dont touch the following constants
SYMBOL_ELEMENT_CLASS_NAME = 'current-symbol'
SEARCH_BAR_CLASS_NAME = 'search__field'
BUY_BUTTON_CLASS = 'btn-call'
SELL_BUTTON_CLASS = 'btn-put'
CURRENCY_ELEMENTS_CLASS = 'alist__label'
CURRENCY_PAYOUT_CLASS = 'alist__payout'



class WebHandler:
    def __init__(self,driver:webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(self.driver,10)
        self.action_chain = ActionChains(self.driver)
        self.symbol_element = None
        self.buy_button = None
        self.sell_button = None
        self.search_element = None
        self.currency_element = None
    def click_on_buy(self):
        self.action_chain.click(self.symbol_element).perform()
        self.buy_button.click()


    def click_on_sell(self):
        self.action_chain.click(self.symbol_element).perform()
        self.buy_button.click()

    def relocate_elements(self):
        self.symbol_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,SYMBOL_ELEMENT_CLASS_NAME)))
        self.buy_button = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,BUY_BUTTON_CLASS)))
        self.buy_button = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,SELL_BUTTON_CLASS)))

    def locate_search_bar(self):
        """This Function should only be used after clicking on symbol_element"""

        self.search_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,SEARCH_BAR_CLASS_NAME)))

    def locate_currency(self,key:str):
        
        if not self.search_element:raise Exception("You should locate the search_element first")

        self.search_element.send_keys(key)
        elements = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,CURRENCY_ELEMENTS_CLASS)))
        for element in elements:
            element_text = element.text
            if element_text == key:
                self.currency_element = element
                paytout_text = element.find_element(By.XPATH,"./..").find_element(By.CLASS_NAME,CURRENCY_PAYOUT_CLASS).text
                return int(paytout_text.replace('%',''))
        else:
            raise Exception(f"Could not find currency element {key}")
        

    def reload_website(self):
        self.driver.get(WEBSITE_URL)
        self.relocate_elements()
        self.search_element = None
        self.currency_element = None

import time
import datetime
import json

class Actions(Enum):
    NONE = 'NONE'
    BUY = 'BUY'
    SELL = 'SELL'

class Application:
    def __init__(self):
        self.driver = self.start_driver(HIDDEN_CHROME,UNDETECTED_CHROME)
        self.handler = WebHandler(self.driver)
        self.handler.reload_website()
    def close_driver(self):
        try:self.driver.close()
        except:pass
    def start_driver(self,headless = True,undetected = False):
        """headless for invisible driver - use for debugging.   
        use undetected if the website recognizes you as robot"""

        chrome_options = Options()
        chrome_options.add_argument('--ignore-ssl-errors=yes')
        chrome_options.add_argument('--ignore_certificate_errors')
        chrome_options.add_argument(f'--user-data-dir={DATA_DIR}')
        chrome_options.set_capability('pageLoadStrategy','eager')

        if headless: chrome_options.add_argument('--headless=new')

        chrome_service = Service(chromedriver_autoinstaller.install(no_ssl=True))

        if(undetected):
            return undetected_chromedriver.Chrome(service=chrome_service,options=chrome_options)
        else:
            return webdriver.Chrome(service=chrome_service,options=chrome_options)
    
    @staticmethod        # This function turns the key value to what is written in website
    def __refine_key(string:str):
        return (string[0:3]+'/'+string[3:6]).upper()
    
    def process_keys(self,keys:dict):
        for key in keys:
            action = keys[key].upper()
            refined_key = self.__refine_key(key)
            try:
                self.__process_refined_key(refined_key,action)
            except Exception as e:
                print(f"Exception for {key},{action}: {e}")

    def __process_refined_key(self,key:str,action):
        self.handler.symbol_element.click()
        self.handler.locate_search_bar()
        payout = self.handler.locate_currency(key) # this function returns payout value
        self.handler.currency_element.click()
        if action==Actions.BUY.name:
            self.handler.click_on_buy()
        elif action==Actions.SELL.name:
            self.handler.click_on_sell()
        else:
            print(f"action {action} is not a valid action")
         

def read_json_file(file_path):

    data = {}
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # اگر فایل خراب، خالی یا وجود نداشته باشد
            data = {}
    
    return data

         



def run(): 
    while True: 
        try : 
            if (datetime.datetime.now().minute + 1) % 5 == 0 and(datetime.datetime.now().second + 1) >= 59:
                order = read_json_file('order.json')  # order is dict  example : {'EURUSD' : 'BUY'}
                if order : 
                    app.process_keys(order)  
                    time.sleep(1)
            time.sleep(0.5)
        except Exception as s : 
            print(s)
            time.sleep(10)



app = Application()
input('LOGIN IN THE WEBSITE')
run()
# app.close_driver()



