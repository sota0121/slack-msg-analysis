# ユーザー検索プロジェクト

## 目的

- slackの投稿メッセージをユーザーごとに分析
- 任意の分野に対して、誰が詳しいか（誰に聞けば答えが得られそうか）を返してくれるシステムを作る

## 現段階の構想

各モジュールは「slack分析コンペ-チーム2」などで作ったモジュールを活用することも検討している

1. DB蓄積（定期実行）
   1. slack >> (slackAPIで抽出) >> (整形/変換) >> Bigquery(取り込み)
2. ユーザー検索
   1. (入力) >> Dataportalなど >> Bigquery（全文検索・類似度検索など）

## Getting started

1. パッケージ用意(rootディレクトリにて)
   1. pipenv
      1. `pipenv install`
   2. conda
      1. `conda create -n [ENV_NAME] python=3.7`
2. チャンネル一覧ファイルの作成
   1. 仮想環境に入る
   2. `python list_channel_info.py > chlist_to_get.csv`
   3. ※不要なチャンネルがあれば消してください
   4. ※以降の処理ではファイルに記述された全てのチャンネルのメッセージを処理対象とします
3. メインスクリプトの実行
   1. 仮想環境に入る
   2. `python main.py`

### 出力されるファイル

- <font color=blue>**chlist_to_get.csv**</font>
  - チャンネル一覧
  - 「2. チャンネル一覧ファイルの作成」にて
- <font color=blue>**collect_msgs.json**</font>
  - ユーザーごとの投稿メッセージ
  - 「3. メインスクリプトの実行」にて生成
  - ※まだノイズデータが含まれています
- <font color=blue>**userinfo.csv**</font>
  - ユーザー情報一覧（ユーザーIDとユーザー名）
  - 「3. メインスクリプトの実行」にて生成
- <font color=blue>**frequency_of_words.json**</font>
  - 投稿メッセージの語単位の頻度データをユーザーごとにまとめたもの
  - 「3. メインスクリプトの実行」にて生成
  - ※今は固定で名詞のみを処理対象としています

## 各スクリプトの役割

### main.py

- メインのスクリプト
- slackからの情報抽出
- 情報の整形、変換
- Bigqueryへの取り込み

### slackapp.py

- Slackから情報を抽出するためのモジュール

### vectorizer.py

- 投稿メッセージ情報の変換を担うモジュールの一つ
- count vectorizer

### list_channel_info.py

- slackの全チャンネル名をCSV形式で標準出力する
- main.pyにてターゲットにするチャンネルを "chlist_to_get.csv" から読み取るようにしているが
- そのCSVファイル作成のサポートをする
- 使い方は `python list_channel_info.py > chlist_to_get.csv`
