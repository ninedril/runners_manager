from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

import re, time, glob, time, os, shutil, math

from getpass import getpass

from pyvirtualdisplay import Display

def produceChrome(config_dir='setting/profile'):
	op = Options()
	op.add_argument('user-data-dir=' + config_dir)
	op.binary_location = 'bin/chrome/chrome.exe'
	driver = webdriver.Chrome('bin/chromedriver.exe', chrome_options=op)
	return driver

#HeadlessなChromeを起動する
def ghostChrome():
	virtual_display = Display(visible=False)
	virtual_display.start()
	virtual_display.redirect_display(True)
	driver = produceChrome()
	virtual_display.redirect_display(False)
	return driver

if __name__ == '__main__':
	dv = ghostChrome()
	# mylibrary login
	dv.get('https://mylibrary.ritsumei.ac.jp/mylibrary/')
	dv.find_element_by_xpath("/html/body//*[.='ログイン']").click()
	username = input('Username:')
	password = getpass()
	
	