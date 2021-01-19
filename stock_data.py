# Imports
from credentials import password, email
from data import stock_list_one

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import pprint, re, requests, io, time, random, string

# set up constants 
pp = pprint.PrettyPrinter(indent=4)

client = MongoClient()
db = client['stock_data']
db.drop_collection("current_data")
collection = db['current_data']

driver = webdriver.Chrome('/Users/Simone/Coding/chromedriver')
time.sleep(3)

data_to_store = {
    "company_name" : '/html/body/main/section/div[2]/div/div[1]/h1/div[2]/a',
    'current_price' : '/html/body/main/section/div[3]/div/div/div/div/div[2]/div/div[1]/span[1]',
    'percentage' : '/html/body/main/section/div[3]/div/div/div/div/div[2]/div/div[2]/div',
    'amount_changed' : '/html/body/main/section/div[3]/div/div/div/div/div[2]/div/div[1]/span[2]',
    'market_cap' : '/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[1]/td',
    'enterprise_value' : ' /html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[2]/td',
    'income' : '/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[3]/td', 
    'revenue' : '/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[1]/td', 
    'ebitda' : '/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[2]/td',
    'volume' : '/html/body/main/section/div[4]/div[1]/div[2]/div[2]/div[1]/table/tbody/tr[1]/td',
    'relative_volume' : '/html/body/main/section/div[4]/div[1]/div[2]/div[2]/div[1]/table/tbody/tr[2]/td'
    }

# functions
def sign_in(email=email, password=password):
   driver.get('https://wallmine.com')
   time.sleep(2)
   driver.find_element_by_xpath('/html/body/main/header/div/ul/li[1]/ul/li[3]/a').click() # click sign in
   time.sleep(1)
   driver.find_element_by_xpath('//*[@id="new_user"]/div[5]/div[1]/div[2]/a').click() #sign in with password
   # log in
   # verify on sign in page: 
   if "We're glad you're back!" in driver.page_source: 
       driver.find_element_by_xpath('//*[@id="user_email"]').send_keys(email)
       driver.find_element_by_xpath('//*[@id="user_password"]').send_keys(password)
       time.sleep(0.2)
       driver.find_element_by_xpath('//*[@id="new_user"]/div[5]/div[2]/div[1]/button').click()
       time.sleep(3)
       if 'US Markets' in driver.page_source: print('successfully signed in')
   else: 
        print('wrong page, start over')

def get_data(stock_array, criteria):
    # stock array is array of dicts with keys 'exchange' and 'stock_ticker'
    # criteria is dict of data you with to store with values of xpaths
    for stock in stock_array:
        driver.get(f"https://wallmine.com/{stock.get('exchange')}/{stock.get('stock_ticker')}")
        time.sleep(2)
        company_data = {}
        for attribute in criteria:
            company_data[attribute] = driver.find_element_by_xpath(criteria[attribute]).text
            # get percentage up or down
            if attribute == 'percentage': 
                if driver.find_element_by_xpath(criteria['percentage']).get_attribute('class') == 'badge badge-danger': company_data['percentage'] = '-' + company_data['percentage']
                else: company_data['percentage'] = '+' + company_data['percentage']
            if attribute in ['market_cap', 'income', 'revenue', 'ebitda', 'enterprise_value']:
                if company_data[attribute][-1] == 'B': 
                    company_data[attribute] = float(company_data[attribute][:-1].split('$')[1]) * 1000000000
                elif company_data[attribute][-1] == 'M': 
                    company_data[attribute] = float(company_data[attribute][:-1].split('$')[1]) * 1000000
                elif company_data[attribute][-1] == 'T':
                    company_data[attribute] = float(company_data[attribute][:-1].split('$')[1]) * 1000000000000
        company_data['ticker'] = stock.get('stock_ticker')
        company_data['exchange'] = stock.get('exchange')
        db_id = db.current_data.insert_one(company_data).inserted_id
        pp.pprint(db.current_data.find_one({"_id": db_id}))

# run program
sign_in(email, password)
get_data(stock_list_one, data_to_store)
