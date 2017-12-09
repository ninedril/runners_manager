from function import *
from selenium.common.exceptions import *
import datetime

class LoanStatusManager:
    def __init__(self, driver):
        self.wd = driver
        self.__deadline_index = self.__findDeadlineIndex()
        self.__today = datetime.datetime.today()
    
    def extend(self):
        while self.__extendFirstMatchedBook():
            pass

    def __findDeadlineIndex(self):
        return findDeadlineIndex(self.wd)

    def __extendFirstMatchedBook(self):
        table_rows = self.wd.find_element_by_xpath('//table[descendant::text()[contains(., "延長")]]').find_elements_by_tag_name('tr')

        for row in table_rows:
            items = row.find_elements_by_tag_name('td')
            m = re.search('(\d{,4})\D(\d{,2})\D(\d{,2})', items[self.__deadline_index].text)
            deadline = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            if deadline == self.__today:
                try:
                    ext_bt = items.find_element_by_xpath('.//*[@*[contains(., "延長")] or text()[contains(., "延長")]]')
                    ext_bt.click()
                    return True
                except NoSuchElementException:
                    continue
            else:
                return False

        raise Exception('No book can be extended!')
        
