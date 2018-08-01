from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from getpass import getpass
from datetime import date
import sys, re, time, datetime

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

def exit_browser(wd):
    for w in wd.window_handles:
        wd.switch_to_window(w)
        wd.close()
        time.sleep(0.5)
    wd.quit()
    sys.exit(0)

def log(text):
	with open('mylog.log', 'a') as f:
		f.write("[" + str(datetime.datetime.today()) + "] " + text + "\n")

# [WebElements] =>
def click_each_elems(elements):
    for e in elements:
        try:
            e.click()
        except:
            continue
