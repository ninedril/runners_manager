from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from getpass import getpass
from datetime import date
import re

def launchChrome():
	op = Options()
	op.add_argument('user-data-dir=setting/profile')
	op.binary_location = 'bin/chrome/chrome.exe'
	driver = webdriver.Chrome('bin/chromedriver.exe', chrome_options=op)
	return driver

def findDeadlineIndex(driver):
    header_row = driver.find_element_by_xpath('//table[descendant::text()[contains(., "延長")]]').find_element_by_tag_name('tr')
    col_values = list(map(lambda x: x.text, header_row.find_elements_by_tag_name('th')))

    deadline_index = None
    for v in col_values:
        if v.find('期限日') != -1:
            deadline_index = col_values.index(v)
    
    return deadline_index
