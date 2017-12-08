from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
from getpass import getpass
from datetime import date
import re

op = Options()
op.add_argument('user-data-dir=setting/profile')
op.binary_location = 'bin/chrome/chrome.exe'
dv = webdriver.Chrome('bin/chromedriver.exe', chrome_options=op)

dv.get('https://mylibrary.ritsumei.ac.jp/mylibrary/')

try:
    dv.find_element_by_xpath("/html/body//*[.='ログイン']").click()
except NoSuchElementException:
    pass

try:
    inputs = dv.find_elements_by_xpath('/html/body//form//input[@type="text" or @type="password"]')
    inputs[0].send_keys(input('Username: '))
    inputs[1].send_keys(getpass())
    inputs[0].submit()
except NoSuchElementException:
    pass

dv.find_element_by_xpath("/html/body//*[text()[contains(., '貸出') and contains(., '状況')]]").click()
dv.switch_to_window(dv.window_handles[1])
table_rows = dv.find_element_by_xpath('//table[descendant::text()[contains(., "延長")]]').find_elements_by_tag_name('tr')
first_row = table_rows.pop(0)
col_values = list(map(lambda x: x.text, first_row.find_elements_by_tag_name('th')))

deadline_index = None
for v in col_values:
    if v.find('期限日') != -1:
        deadline_index = col_values.index(v)

today = date.today()
for row in table_rows:
    items = row.find_elements_by_tag_name('td')
    m = re.search('(\d{,4})\D(\d{,2})\D(\d{,2})', items[deadline_index].text)
    deadline = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    if deadline == today:
        ext_bt = items.find_element_by_xpath('.//*[@*[contains(., "延長")] or text()[contains(., "延長")]]')
        ext_bt.click()
