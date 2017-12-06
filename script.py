from selenium import webdriver
from selenium.webdriver.chrome.options import Options

op = Options()
op.add_argument('user-data-dir=setting/profile')
op.binary_location = 'bin/chrome/chrome.exe'
dv = webdriver.Chrome('bin/chromedriver.exe', chrome_options=op)

dv.get('https://mylibrary.ritsumei.ac.jp/mylibrary/')
dv.find_element_by_xpath("/html/body//*[.='ログイン']").click()

inputs = dv.find_elements_by_xpath('/html/body//form//input[@type="text" or @type="password"]')
inputs[0].send_keys(input('Username: '))
inputs[1].send_keys(getpass())
inputs[0].submit()

dv.find_element_by_xpath("/html/body//*[text()[contains(., '貸出') and contains(., '状況')]]").click()

dv.switch_to_window(dv.window_handles[1])
table_lines = dv.find_element_by_xpath('//table[descendant::text()[contains(., "延長")]]').find_elements_by_tag_name('tr')
col_values = list(map(lambda x: x.text, table_lines[0].find_elements_by_tag_name('th')))
