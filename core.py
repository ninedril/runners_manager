from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
import lxml.html
import re, time, glob, time, os, shutil, math
from mutagen.mp3 import MP3
from pyvirtualdisplay import Display

def produceChrome(config_dir='user-data-dir=/mnt/hdd/Development/Selenium/Chrome'):
	op = Options()
	op.add_argument(config_dir)
	driver = webdriver.Chrome("/mnt/hdd/Development/Selenium/chromedriver", chrome_options=op)
	return driver

#HeadlessなChromeを起動する
def ghostChrome():
	virtual_display = Display(visible=False)
	virtual_display.start()
	virtual_display.redirect_display(True)
	driver = produceChrome()
	virtual_display.redirect_display(False)
	return driver

class Mp3Getter:
	def __init__(self):
		self.dv = ghostChrome()
	#曲の複数のダウンロードページへのURLのリスト
	def down_mp3(self, at):
		self.main(at)

	#TorF: 適切なURL達が手に入ったかどうか
	def get_urls(self, search_word):
		if not search_word:
			print('Enter a search word')
			return False
		try:
			self.dv.get("http://junglevibe20.net/tracks/" + search_word + ".html")
			url_list = [e.get('onclick') for e in lxml.html.fromstring(self.dv.page_source).xpath('//*[@class="downloadButton"]')]
			res_list = [re.search(r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", e).group(0) for e in url_list]
			if res_list:
				print('Got the URL list of DL-pages')
				return res_list
			else:
				print('No DL-page')
				return False
		except:
			print('Page was modified')
			return False
	def handle_popup(self):
		try:
			self.dv.switch_to_alert().accept()
		except:
			pass
	#共有のドライバーが必ずダウンロードページを開いている状態で呼び出すこと!
	#TorF: DLボタンが押せたかどうか
	def kick_button(self):
		pat = re.compile(r'https?://junglevibe20\.net')
		init_url = self.dv.current_url
		while True:
			dl_buttons = self.dv.find_elements_by_xpath('//a[contains(@href, ".mp3")]')
			if len(dl_buttons) != 1:
				print('Not found Download Button')
				return False
			try:
				dl_buttons[0].click()
			except WebDriverException:
				self.dv.find_element_by_tag_name('body').click()
				self.handle_popup()
				self.dv.get(init_url)
				self.handle_popup()
				continue
			break
		print('DL button was kicked!')
		return True
	#For only serial download. Return file_path
	def wait_for_downloaded(self):
		while True:
			time.sleep(2)
			files = glob.glob('/mnt/hdd/Development/Selenium/download/*.mp3')
			if len(files) == 1:
				return files[0]
			continue
	def exit(self):
		self.dv.quit()
	def main(self, artist_title):
		dl_pages = self.get_urls(artist_title)
		if not dl_pages:
			print('No music...')
			return False
		for page in dl_pages:
			self.dv.get(page)
			if not self.kick_button():
				continue
			mp3_path = self.wait_for_downloaded()
			bitrate = mp3_check(mp3_path)
			if bitrate:
				shutil.move(mp3_path, '/mnt/hdd/Development/Selenium/download/' + str(bitrate) + '.cnd')
				if bitrate == 320:
					break
			else:
				os.remove(mp3_path)
		cnd_list = glob.glob('/mnt/hdd/Development/Selenium/download/*.cnd')
		if not cnd_list:
			print("This music doesn't exist")
			return False
		mp3_dir = os.environ['HOME'] + '/Music/'
		best_mp3 = '/mnt/hdd/Development/Selenium/download/' + str(max(list(map(lambda x: int(x[-7:-4]), cnd_list)))) + '.cnd'
		shutil.copy(best_mp3, mp3_dir + artist_title + '.mp3')
		#For clean-up
		for p in glob.iglob('/mnt/hdd/Development/Selenium/download/*.cnd'):
			os.remove(p)
		print('Downloaded to "' + os.environ['HOME'] + '/Music/"')

#ファイルを落としたら実行
def mp3_check(path):
	try:
		 f = MP3(path)
	except:
		return False
	if f.info.length < 150:
		return False
	br = math.floor(f.info.bitrate/1000)
	if br == 320:
		return 320
	elif br <= 127:
		return False
	else:
		return br
