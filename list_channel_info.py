# channel 名の一覧を取得する
# 設定ファイル生成のサポートとして使う
# 1. "python list_channel_info.py > ch_list.txt"
# 2. 解析対象にしたいチャンネルのみ残す
# 3. "main.py" を実行

import sys
import json
import slackapp as sa


# api token 読み込み
with open('credential.json', 'r') as f:
    credentials = json.load(f)

# slackapp開始
app = sa.slackapp(credentials['channel_api_key'], credentials['user_api_key'])

# channels情報を取得する
if app.request_chinfo() is False:
    print('failed to get channel info')
    sys.exit(1)

app.list_channel_names(sep=',')

