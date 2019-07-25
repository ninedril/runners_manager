# import
import requests
from urllib.error import HTTPError
import lxml.html
import pandas
import datetime
import wx
import pdb


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


class SiteChangedException(Exception):
    pass


class TaskBarIcon(wx.adv.TaskBarIcon):
    '''
    View
    '''

    def __init__(self, frame, icon_path, tray_tip=''):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        icon = wx.Icon(wx.Bitmap(icon_path))
        self.SetIcon(icon, tray_tip)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.app.on_taskbar_l_dclick)

    @property
    def app(self):
        return wx.GetApp()


class app(wx.App):
    '''
    Model
    '''

    def OnInit(self):
        # view
        frame = wx.Frame(False)
        self.SetTopWindow(frame)
        TaskBarIcon(frame, 'logo.ico', '立命館図書館の延長自動化')
        # model
        # setting

    def on_taskbar_l_dclick(self, evt):
        pass

    def main(self, evt):
        pass


class RunnersManager:
    """
    入力: LOGIN_ID, LOGIN_PASS
    動作: 
    出力: 
    """

    def __init__(self, setting_obj={}):
        # 設定ファイルを読み込む
        if(os.path.)

    def main(self):
        ### 一般設定ここから ###
        LOGIN_ID = ''
        LOGIN_PASS = ''
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


if __name__ == '__main__':
    pass
