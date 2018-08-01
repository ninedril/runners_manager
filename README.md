# runners_manager
Auto Extending of Rits Runners

立命館大学図書館の蔵書システムであるRUNNERS（https://runners.ritsumei.ac.jp/opac/opac_search/?lang=0）
の貸出延長を定期的に自動で行う簡易スクリプト。
返却期限の1日前を通知する、メールアラート機能付き。

＝＝＝ 必要な情報 ＝＝＝
・RUNNERSのIDとパスワード
・メールアドレスとログインパスワード

＝＝＝ 設定手順（上級者向け） ＝＝＝
1.taskschd.mscを起動し、付属の「Runners Extender.xml」をインポート
2.カレントディレクトリをダウンロードしたフォルダにする。
3.引数の「user_id」「password」「メールアドレス」「メールアドレスのパスワード」をそれぞれRunnersのID、パスワード、メールアドレス、メールアドレスログインパスワードにする
4.定期起動する時間を再設定（初期値は10:25）

＝＝＝ 設定手順（初級者向け）＝＝＝
1.Windows + Rで出てくるボックスに「taskschd.msc」を入力し実行
2.右側のバー「操作」→「タスクのインポート」→「操作タブ」→「編集ボタン」を押す
3.「引数の追加」の「user_id」「password」「メールアドレス」「メールアドレスのパスワード」を自分のものに書き換える。
  user_id: RunnersのID
  password: Runnersのパスワード
4.「開始」の部分にダウンロードしたフォルダのパスを設定する
