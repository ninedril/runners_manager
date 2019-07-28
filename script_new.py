# import
import requests
from urllib.error import HTTPError
import lxml.html
import pandas
import datetime
import wx
import wx.adv
import pdb
import re
import sys
import json

# 関数定義


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

# クラス定義


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
        # pdb.set_trace()
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
        return self.result.text if self.result.text else ''

    @property
    def url(self):
        return self.result.url if self.result.url else ''

    @property
    def content(self):
        return self.result.content if self.result.content else b''

    @property
    def encoding(self):
        return self.result.encoding


class SiteChangedException(Exception):
    pass


def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.AppendItem(item)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())

    return item


class TaskBarIcon(wx.adv.TaskBarIcon):
    '''
    View
    '''

    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon('logo.ico', '立命館図書館の延長自動化')
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.on_extend)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Extend', self.on_extend)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)

        return menu

    @property
    def app(self):
        return wx.GetApp()

    def set_icon(self, path, tray_tip):
        icon = wx.Icon(wx.Bitmap(path))
        self.SetIcon(icon, tray_tip)

    def set_traytip(self, tray_tip):
        self.SetIcon(self.icon, tray_tip)

    def on_extend(self, evt):
        self.app.on_taskbar_l_dclick(evt)

    def on_exit(self, evt):
        wx.CallAfter(self.Destroy)
        self.frame.Close()


class App(wx.App):
    '''
    Model
    '''

    def OnInit(self):
        # view
        frame = wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        # model
        # setting
        with open('setting.json', 'r', encoding='utf-8') as f:
            self.S = json.load(f)

        print('launch app')
        return True

    def on_taskbar_l_dclick(self, evt):
        self.main(evt)

    def main(self, evt):
        S = self.S

        # Variable
        LOGIN_ID = S['user']['site_info']['auth']['login_id']
        LOGIN_PASS = S['user']['site_info']['auth']['login_pass']
        DAYS_TO_EXTEND = S['user']['program']['behavior']['extension']['days_to_extend']
        DAYS_TO_ALERT = S['user']['program']['behavior']['alert']['days_to_alert']
        today = datetime.date.today()

        # Main
        RM = RunnersManager()
        RM.login(LOGIN_ID, LOGIN_PASS)
        books = RM.get_borrowed_books()
        books_to_extend = RM.filter_extendable_books(books, DAYS_TO_EXTEND, today)
        books_to_alert = RM.filter_unextendable_books(books, DAYS_TO_ALERT, today)
        RM.extend_books(books_to_extend)


class BorrowedBook:
    '''
    貸し出し中の本を表現するクラス
    '''

    def __init__(self):
        # 本を識別する固有のID
        self.bookid = ''
        # 書籍名
        self.title = ''
        # 返却期限日。Date型
        self.deadline = None
        # 延長した回数
        self.extended_num = -1
        # 予約人数
        self.preserve_num = -1
        # 延長可能かどうか
        self.is_extendable = True

    def get_days_to_deadline(self, starndard_date=datetime.date.today()):
        """
        返却期限日まで残された日数。

        Parameters
        ----------
        starndard_date: datetime.date, default datetime.date.today()
            基準となる日付。デフォルトで呼び出した時の日付。

        Returns
        ----------
        result: int, default -1
            残りの日数。
        """
        result = -1
        if self.deadline:
            result = (self.deadline - starndard_date).days
        return result


class RunnersManager:
    """
    入力: LOGIN_ID, LOGIN_PASS
    動作: runnersにログインし、該当の図書貸出を延長する
    出力: もう延長できない本のタイトルと期限日をリストで返却

    ※略語※
    lst: loan_status_table の略
    """

    def __init__(self):
        self.session = SessionWrapper()

    def login(self, login_id: str, login_pass: str):
        """
        Runnersにログインする。

        Parameters
        ----------
        login_id: str
            RunnersのログインID
        login_pass: str
            Runnersのログインパスワード
        """
        login_url = 'https://runners.ritsumei.ac.jp/opac/opac_search/?loginMode=disp&lang=0'
        post_url = 'https://runners.ritsumei.ac.jp/opac/opac_search/'
        login_form_xpath = '//form[@id="opac_login_disp"]'

        session = self.session
        session.get(login_url)
        session.post(post_url, data={
            'userid': login_id,
            'passwd': login_pass
        }, form_xpath=login_form_xpath)

    def get_borrowed_books(self) -> list:
        """
        貸出中の本をBorrowedBookオブジェクトのリストで取得し返す
        入力: ログイン済みself.session
        出力: BorrowedBookオブジェクトのリスト

        Returns
        ----------
        result: list[BorrowedBook]
            貸出中の本のリスト
        """
        result = []

        loan_status_url = 'https://runners.ritsumei.ac.jp/opac/odr_stat/?lang=0'
        loan_status_table_xpath = '//table[@id="datatables_re"]'
        lst_colname__bookid = '資料番号'
        lst_colname__title = '資料名'
        lst_colname__deadline = '返却期限日'
        lst_colname__deadline_regex = r'(\d{4})\D(\d{1,2})\D(\d{1,2})'
        lst_colname__extended_num = '継続回数'
        lst_colname__preserve_num = '予約有無'

        session = self.session
        # 貸出状況ページに移動し、テーブルをDataFrame化する
        session.get(loan_status_url)
        table_elem = session.xpath(loan_status_table_xpath)[0]
        table_elem_source = get_source_of_HtmlElement(table_elem, session.encoding)
        df = pandas.read_html(table_elem_source)[0]

        # BorrowedBookオブジェクトを生成してリストに格納する
        for index, row in df.iterrows():
            book = BorrowedBook()
            # bookid
            book.bookid = str(row[lst_colname__bookid]).strip()
            # title
            book.title = row[lst_colname__title]

            # deadline
            deadline_m = re.search(lst_colname__deadline_regex, row[lst_colname__deadline])
            if not deadline_m:
                raise Exception(
                    "サイト上の返却期限日のフォーマットが異なっています。\nget_borrowed_books()内「lst_colname__deadline_regex」の記述を見直してください。")
            year = int(deadline_m.group(1))
            month = int(deadline_m.group(2))
            day = int(deadline_m.group(3))
            book.deadline = datetime.date(year=year, month=month, day=day)

            # extended_num
            extended_num_m = re.findall(r'\d{1,2}', row[lst_colname__extended_num])
            if len(extended_num_m) != 1:
                raise Exception("サイト上の延長回数のフォーマットが異なっています。\nget_borrowed_books()内の正規表現を見直してください。")
            book.extended_num = int(extended_num_m[0])

            # preserve_num
            preserve_num_m = re.findall(r'\d{1,2}', row[lst_colname__preserve_num])
            if len(preserve_num_m) != 1:
                raise Exception("サイト上の予約人数のフォーマットが異なっています。\nget_borrowed_books()内の正規表現を見直してください。")
            book.preserve_num = int(preserve_num_m[0])

            # is_extendable
            if book.extended_num < 2 and book.preserve_num == 0:
                book.is_extendable = True
            else:
                book.is_extendable = False

            result.append(book)
        return result

    def filter_unextendable_books(self, borrowed_books, days_until_deadline, standard_date):
        """
        これ以上延長できず、かつ返却期限日まで残り指定日数以内の本をフィルタする

        Parameters
        ----------
        borrowed_books: list[BorrowedBook]
            貸出中の本のBorrowedBookリスト
        days_until_deadline: int
            返却期限日までの残り日数
        standard_date: datetime.date
            残り日数を数える基準となる日時

        Return
        ----------
        result: list[BorrowedBook]
            フィルタされた本のBorrowedBookリスト
        """
        if not borrowed_books or not isinstance(borrowed_books, list):
            raise Exception(sys._getframe().f_code.co_name + ": 貸出中の本が入力されていません。")
        if not isinstance(borrowed_books[0], BorrowedBook):
            raise Exception(sys._getframe().f_code.co_name + ": 貸出中の本が正しいオブジェクトになっていません。")
        result = []
        result = [e for e in borrowed_books if not e.is_extendable]
        result = [e for e in result if e.get_days_to_deadline(standard_date) <= days_until_deadline]
        return result

    def filter_extendable_books(self, borrowed_books, days_until_deadline, standard_date):
        """
        延長可能で、かつ返却期限日まで残り指定日数以内の本をフィルタする

        Parameters
        ----------
        borrowed_books: list[BorrowedBook]
            貸出中の本のBorrowedBookリスト
        days_until_deadline: int
            返却期限日までの残り日数
        standard_date: datetime.date
            残り日数を数える基準となる日時

        Return
        ----------
        result: list[BorrowedBook]
            フィルタされた本のBorrowedBookリスト
        """
        if not borrowed_books or not isinstance(borrowed_books, list):
            raise Exception(sys._getframe().f_code.co_name + ": 貸出中の本が入力されていません。")
        if not isinstance(borrowed_books[0], BorrowedBook):
            raise Exception(sys._getframe().f_code.co_name + ": 貸出中の本が正しいオブジェクトになっていません。")
        result = []
        result = [e for e in borrowed_books if e.is_extendable]
        result = [e for e in result if e.get_days_to_deadline(standard_date) <= days_until_deadline]
        return result

    def extend_books(self, borrowed_books: list):
        """
        貸出中の本を延長する。

        Parameters
        ----------
        borrowed_books: list[BorrowedBook]
            延長したい本のBorrowedBookリスト
        """
        if not borrowed_books or not isinstance(borrowed_books, list):
            raise Exception(sys._getframe().f_code.co_name + ": 貸出中の本が入力されていません。")
        if not isinstance(borrowed_books[0], BorrowedBook):
            raise Exception(sys._getframe().f_code.co_name + ": 貸出中の本が正しいオブジェクトになっていません。")

        loan_status_url = 'https://runners.ritsumei.ac.jp/opac/odr_stat/?lang=0'
        loan_status_form_xpath = '//form[@id="srv_odr_stat_re"]'
        loan_post_url = 'https://runners.ritsumei.ac.jp/opac/odr_stat/?lang=0'

        session = self.session
        # 貸出状況確認ページに移動する
        if session.url != loan_status_url:
            session.get(loan_status_url)

        # データを用意する
        bookid_list = [e.bookid for e in borrowed_books]
        bookid_str = ','.join(bookid_list)

        # POST送信する（bookid, extchk）
        session.post(loan_post_url, data={
            'bookid': bookid_str,
            'extchk[]': bookid_list,
            'reqCode': 'extre',
            'disp': 're'
        }, form_xpath=loan_status_form_xpath)


if __name__ == '__main__':
    app = App(False)
    app.MainLoop()
