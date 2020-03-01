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
