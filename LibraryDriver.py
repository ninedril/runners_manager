import pdb
from selenium import webdriver


class LibraryDriver:
    def __init__(self):


op = webdriver.ChromeOptions()
pdb.set_trace()
op.binary_location = 'bin/chrome/App/Chrome-bin/chrome.exe'
dv = webdriver.Chrome('bin/chromedriver.exe', chrome_options=op)
dv.implicitly_wait(10)


if __name__ == '__main__':
    pass
