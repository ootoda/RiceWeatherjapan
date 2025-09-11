# Rice Weather japan
ファミコン風　キャラクター会話ゲームです
お米の価格によって　主婦と農家と政治家がそれぞれの立場でしゃべります
プレイヤーは基本的に介入は出来ません。
テレビを見ている感覚です

## 対象
windows11

## ダウンロード
GitHubからダウンロードできます。以下のページの緑の「Code」ボタンを押してzipをダウンロードします。
https://github.com/ootoda/RiceWeatherjapan

## インストール
Pythonで作っています。初回起動時に　Pygameのインストールが必要となることがあります。
以下のコマンドを、コマンドプロンプトから入力して必要なものをダウンロードしてください。

pip install pygame pillow


## エラーが起こって起動しない
一瞬ウィンドウが開いて、すぐ閉じてしまう。などのエラーが起こる場合があります。

原因１：スペースを含むファイル名は、Pythonがファイル名を正しく認識できていないことが原因です。
この場合はコマンドラインを開いて、ファイル名を引用符で囲ってください。

python "Rice Weather japan_v1.7.py"

原因２：ファイル名を変更する：
スペースを含むファイル名は問題を起こしやすいので、ファイル名を変更することをお勧めします：

Rice Weather japan_v1.7.py　を　rice_weather_japan_v1.7.py　にリネームします。
もしくは
Rice.py　にします。

原因３：pythonが pygame という名前のモジュールを見つけられない
この問題を解決するには、Python環境に pygame ライブラリをインストールする必要があります。

・コマンドプロンプトまたはターミナルを開く:
・Windowsの場合、スタートメニューから「コマンドプロンプト」または「PowerShell」を検索して開きます。
・pip を使って pygame をインストールする:
・以下のコマンドを入力して実行してください。pip はPythonのパッケージインストーラーです。

pip install pygame

もし、複数のPythonバージョンがインストールされている場合や、特定のPython環境を使っている場合は、以下のように python -m pip を使うと確実です。

python -m pip install pygame

または、もし python3 コマンドを使用している場合は：

python3 -m pip install pygame

以上でインストールが正常に完了したら、再度Pythonスクリプトを実行してみてください。



## 使い方
Rice Weather japan_v1.7.py をクリックすると起動します。

## ライセンス
MIT License


