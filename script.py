from selenium import webdriver
from selenium.common.exceptions import *
from getpass import getpass
from datetime import date
import re, time, sys

from function import *


locators = {
    ''
}


import smtplib
from email.mime.text import MIMEText

class MailSender:
    def __init__(self, my_address, my_pswd):
        self.my_address = my_address
        self.my_pswd = my_pswd
    
    def send(self, to_addr, subject, text=""):
        msg = MIMEText(text)
        msg['Subject'] = subject
        msg['From'] = self.my_address
        msg['To'] = to_addr

        smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpobj.ehlo()
        smtpobj.starttls()
        smtpobj.ehlo()
        smtpobj.login(self.my_address, self.my_pswd)
        smtpobj.sendmail(self.my_address, to_addr, msg.as_string())
        smtpobj.close()


def login_sso_page(driver):
    # 1st condition: 
    elems = driver.find_elements_by_xpath('/html/body//form//input[@type="text" or @type="password"]')
    boolean_1st = bool(elems == 2)
    # 2nd
    return ''

def display_element(driver, elem):
    ancestors = elem.find_elements_by_xpath('./ancestor::*')
    for e in ancestors:
        if not(e.is_displayed()):
            driver.execute_script('arguments[0].setAttribute("style", "display: initial")', e)

log("Start running the program.")

first_url = "https://runners.ritsumei.ac.jp/opac/opac_search"

dv = webdriver.Chrome('../chromedriver.exe')
dv.implicitly_wait(10)

dv.get('https://runners.ritsumei.ac.jp/opac/opac_search/?loginMode=disp&lang=0&opkey=&cmode=0&smode=0&ssosw=1')

try:
    dv.find_element_by_xpath("https://runners.ritsumei.ac.jp/opac/opac_search").click()
except NoSuchElementException:
    pass

inputs = dv.find_elements_by_xpath('/html/body//form//input[@type="text" or @type="password"]')
if(len(inputs) != 2): 
    print(len(inputs))
    raise NoSuchElementException()
#inputs[0].send_keys(input('Username: '))
inputs[0].send_keys(sys.argv[1])
#inputs[1].send_keys(getpass())
inputs[1].send_keys(sys.argv[2])
inputs[0].submit()

mail_addr = sys.argv[3]
mail_pswd = sys.argv[4]

for e in dv.find_elements_by_xpath("/html/body//*[text()[contains(., '貸出') and contains(., '状況')]]"):
    try:
        e.click()
        break
    except:
        continue

try:
    dv.switch_to_window(dv.window_handles[1])
except:
    pass

try:
    header_row = dv.find_element_by_xpath('//table[descendant::text()[contains(., "延長")]]').find_element_by_tag_name('tr')
except NoSuchElementException:
    #raise Exception('No book can be extended!')
    print("alert('No book can be extended!')")
    log("No book can be extended! Exit.")
    dv.execute_script("alert('No book can be extended!')")
    time.sleep(4)
    exit_browser(dv)

col_values = list(map(lambda x: x.text, header_row.find_elements_by_tag_name('th')))

deadline_index = None
for v in col_values:
    if v.find('期限日') != -1:
        deadline_index = col_values.index(v)

#import pdb; pdb.set_trace()

today = date.today()

is_checked = True
has_mail_sent = False
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
        log('Due date is ' + str(deadline))
        if deadline == today:
            try:
                ext_bt = row.find_element_by_xpath('.//*[self::input or self::a][@*[contains(., "延長")] or text()[contains(., "延長")]]')
                if not(ext_bt.is_displayed()):
                    display_element(dv, ext_bt)
                ext_bt.click()
                log("    ==> Returned.")
                break
            except NoSuchElementException:
                continue
        elif (deadline - today).days == 1:
            try:
                ext_bt = row.find_element_by_xpath('.//*[self::input or self::a][@*[contains(., "延長")] or text()[contains(., "延長")]]')
            except NoSuchElementException:
                ms = MailSender(mail_addr, mail_pswd)
                ms.send(mail_addr, subject='!!!Return library books on tomorrow!!!')
                is_checked = False
                break
        else:
            is_checked = False
            break
    else:
        break

dv.execute_script("alert('Possible books were returned!')")
log("Possible books were returned. Exit.")
time.sleep(4)
exit_browser(dv)