from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import string
import random
import time

driver = webdriver.Chrome()
count = 0

print('')

while(True):
    driver.get("https://lyonsmymug.ie/#/")

    code = ''.join(random.choices(string.digits, k=2)) + ''.join(random.choices(string.ascii_uppercase, k=5)) + ''.join(random.choices(string.digits + string.ascii_uppercase, k=0)) 
    
    codeIn = driver.find_element_by_id("code")
    codeIn.send_keys(code)

    submit = driver.find_element_by_class_name("submit")

    while("code not found" not in driver.page_source and "https://lyonsmymug.ie/#/" == driver.current_url): 
        submit.click()
        time.sleep(0.1)

    if("https://lyonsmymug.ie/#/" != driver.current_url):
        print(driver.current_url + " : " + code + '\n')
    else:
        driver.refresh()

    print(str(count).zfill(6),  end='\r')

    count += 1

