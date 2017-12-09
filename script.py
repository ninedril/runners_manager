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
    if(len(inputs) != 2): raise NoSuchElementException()
    inputs[0].send_keys(input('Username: '))
    inputs[1].send_keys(getpass())
    inputs[0].submit()
except NoSuchElementException:
    pass

dv.find_element_by_xpath("/html/body//*[text()[contains(., '貸出') and contains(., '状況')]]").click()
dv.switch_to_window(dv.window_handles[1])
try:
    header_row = dv.find_element_by_xpath('//table[descendant::text()[contains(., "延長")]]').find_element_by_tag_name('tr')
except NoSuchElementException:
    raise Exception('No book can be extended!')

col_values = list(map(lambda x: x.text, header_row.find_elements_by_tag_name('th')))

deadline_index = None
for v in col_values:
    if v.find('期限日') != -1:
        deadline_index = col_values.index(v)

#import pdb; pdb.set_trace()

today = date.today()

is_checked = True
while is_checked:
    tables = dv.find_elements_by_xpath('//table[descendant::text()[contains(., "延長")]]')
    table = next(filter((
        lambda t:
        list(map(lambda r: r.text, t.find_element_by_tag_name('tr').find_elements_by_tag_name('th')))
        == col_values
    ), tables))
    table_rows = table.find_elements_by_tag_name('tr')[1:]

    for row in table_rows:
        items = row.find_elements_by_tag_name('td')
        m = re.search('(\d{,4})\D(\d{,2})\D(\d{,2})', items[deadline_index].text)
        deadline = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if deadline == today:
            try:
                ext_bt = row.find_element_by_xpath('.//*[@*[contains(., "延長")] or text()[contains(., "延長")]]')
                ext_bt.click()
                break
            except NoSuchElementException:
                continue
        else:
            is_checked = False
            break
    else:
        break

if input('Close the browser?(y/n)') == 'y':
    for w in dv.window_handles:
        dv.switch_to_window(w)
        dv.close()
    dv.quit()