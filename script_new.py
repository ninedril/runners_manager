# import
import requests
from urllib.error import HTTPError
import lxml.html
import pandas
import datetime
import pdb


class SessionWrapper:
    def __init__(self):
        self._session = requests.Session()
        self.result = None

    def get(self, url):
        """
        GET

        Parameters
        ----------
        url: str
            移動先のURL
        """
        r = self._session.get(url)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        self.result = r

    def post(self, url, data={}, form_xpath=''):
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
        if form_xpath:
            form_elem = self.xpath(form_xpath)[0]
            input_elems = form_elem.xpath('.//input')
            for elem in input_elems:
                if elem.name not in data:
                    data[elem.name] = elem.value
        pdb.set_trace()
        r = self._session.post(url, data=data)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        self.result = r

    def xpath(self, xpath):
        """
        xpathで今のページの要素を抽出する

        Parameters
        ----------
        xpath: str
            抽出したい要素のxpath表現
        """
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

    @property
    def encoding(self):
        return self.result.encoding


def get_source_of_HtmlElement(HtmlElement, encoding):
    """
    HtmlElementオブジェクトのHTMLを文字列として取得

    Parameters
    ----------
    HtmlElement: lxml.html.HtmlElement
        取得したHtmlElementオブジェクト

    encoding: str
        Htmlのエンコーディングを指定
    """
    s = lxml.html.tostring(HtmlElement, encoding=encoding)
    s = s.decode(encoding)
    return s


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

    # 1. SessionWrapperでログインする
    session = SessionWrapper()
    session.get(LOGIN_URL)
    session.post('https://runners.ritsumei.ac.jp/opac/opac_search/', data={
        'userid': LOGIN_ID,
        'passwd': LOGIN_PASS
    }, form_xpath=LOGIN_FORM_XPATH)

    # 2. 貸出状況ページに移動し、テーブルをDataFrame化する
    session.get('https://runners.ritsumei.ac.jp/opac/odr_stat/?lang=0')
    table_elem = session.xpath('//table[@id="datatables_re"]')[0]
    table_elem_source = get_source_of_HtmlElement(table_elem, session.encoding)
    df = pandas.read_html(table_elem_source)[0]

    # 3. DataFrameを整形し、「返却期限日」が今日になっている本の「資料番号」を取得
    today = datetime.date.today()
    df['返却期限日'] = pandas.to_datetime(df['返却期限日'])
    bookid_list = list(df[(df['返却期限日'] - today).dt.days == 0]['資料番号'])
    bookid_list = [str(e).strip() for e in bookid_list]
    bookid_str = ','.join(bookid_list)

    # 4. 資料番号をPOST送信する（bookid, extchk）
    session.post('https://runners.ritsumei.ac.jp/opac/odr_stat/?lang=0', data={
        'bookid': bookid_str,
        'extchk[]': bookid_list,
        'reqCode': 'extre',
        'disp': 're'
    }, form_xpath='//form[@id="srv_odr_stat_re"]')

    pass
