# import
import requests
from urllib.error import HTTPError
import lxml.html


class SessionWrapper:
    def __init__(self, session):
        self._session = requests.Session()
        self.result = None

    """
    GET

    Parameters
    ----------
    url: str
        移動先のURL
    """

    def get(self, url):
        r = self._session.get(url)
        r.raise_for_status()
        self.result = r

    """
    POST

    Parameters
    ----------
    url: str

    data: dict
        送信するデータ（辞書形式）

    form_xpath: str
        フォームの内容も送信したければ、xpathでフォーム指定
    """

    def post(self, url, data={}, form_xpath=''):
        if form_xpath:
            form_elem = self.xpath(form_xpath)[0]
            input_elems = form_elem.findall('input')
            for elem in input_elems:
                v = elem.get('value')
                data[elem.get('name')] = v
        r = self._session.post(url, data=data)
        r.raise_for_status()
        self.result = r

    """
    xpathで今のページの要素を抽出する

    Parameters
    ----------
    xpath: str
        抽出したい要素のxpath表現
    """

    def xpath(self, xpath):
        htmldoc = lxml.html.fromstring(self.result.text)
        result = htmldoc.xpath(xpath)
        return result

    @property
    def text(self):
        result = ''
        if self.result.text:
            result = self.result.text
        return result

    @property
    def url(self):
        result = ''
        if self.result.url:
            result = self.result.url
        return result

    @property
    def content(self):
        result = b''
        if self.result.content:
            result = self.result.content
        return result


### エラー定義 ###
class SiteChangedException(Exception):
    pass


if __name__ == '__main__':
    ### 一般設定ここから ###
    LOGIN_ID = 'cp0006fx'
    LOGIN_PASS = 'Jby1k3hy'
    LOGIN_URL = 'https://runners.ritsumei.ac.jp/opac/opac_search/?loginMode=disp&lang=0'
    LOGIN_FORM_XPATH = '//form[@id="opac_login_disp"]'
    ### 一般設定ここまで ###
    # 1. SessionWrapperでログイン
    session = SessionWrapper()
    session.get(LOGIN_URL)
    session.post()

    # 2. 貸出状況ページに移動し、テーブルの行をループする

    # 3. 条件に一致する書籍のみ、POST送信して延長。4からやり直し

    pass
