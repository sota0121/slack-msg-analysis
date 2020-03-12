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
4. wordcloudの生成（collect_msgs.jsonがあれば良い）
   1. 仮想環境に入る
   2. `python wc_from_collectmsgs.py`

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
- <font color=blue>**wordcloud_img/[user_id].png**</font>
  - ユーザーごとにwordcloudを生成し、画像ファイルとして保存したもの
  - 「4. wordcloudの生成」にて生成

## 各スクリプトの役割

### main.py

- メインのスクリプト
- slackからの情報抽出
- 情報の整形、変換
  - 除去文字列
    - 「●●に参加しました」というチャンネル参加時のメッセージ
    - URL
- Bigqueryへの取り込み(未実装)

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

### wc_from_collectmsgs.py

- collect_msgs.jsonを読み込む
- ユーザーごとの投稿メッセージからwordcloudを生成
  - ※stop_wordsはまだ調整中です
- wordcloud_img/ユーザーID.png として画像保存


### Directory structure:

```
├── LICENSE
├── README.md          <- The top-level README for developers using this project.
├── conf
│   ├── base           <- Space for shared configurations like parameters
│   └── local          <- Space for local configurations, usually credentials
│
├── data
│   ├── 01_raw         <- Imutable input data
│   ├── 02_intermediate<- Cleaned version of raw
│   ├── 03_processed   <- The data used for modelling
│   ├── 04_models      <- trained models
│   ├── 05_model_output<- model output
│   └── 06_reporting   <- Reports and input to frontend
│
├── docs               <- Space for Sphinx documentation
│
├── notebooks          <- Jupyter notebooks. Naming convention is date YYYYMMDD (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `20190601-jqp-initial-data-exploration`.
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── results            <- Intermediate analysis as HTML, PDF, LaTeX, etc.
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── .gitignore         <- Avoids uploading data, credentials, outputs, system files etc
│
└── src                <- Source code for use in this project.
    ├── __init__.py    <- Makes src a Python module
    │
    ├── d00_utils      <- Functions used across the project
    │   └── remove_accents.py
    │
    ├── d01_data       <- Scripts to reading and writing data etc
    │   └── load_data.py
    │
    ├── d02_intermediate<- Scripts to transform data from raw to intermediate
    │   └── create_int_payment_data.py
    │
    ├── d03_processing <- Scripts to turn intermediate data into modelling input
    │   └── create_master_table.py
    │
    ├── d04_modelling  <- Scripts to train models and then use trained models to make
    │   │                 predictions
    │   └── train_model.py
    │
    ├── d05_model_evaluation<- Scripts that analyse model performance and model selection
    │   └── calculate_performance_metrics.py
    │    
    ├── d06_reporting  <- Scripts to produce reporting tables
    │   └── create_rpt_payment_summary.py
    │
    └── d06_visualisation<- Scripts to create frequently used plots
        └── visualise_patient_journey.py
```
