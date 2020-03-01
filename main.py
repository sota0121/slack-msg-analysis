# DLG Slack ws の任意チャンネルのメッセージ群を取得する
import sys
import pandas as pd
import json
import slackapp as sa
import vectorizer

# api token 読み込み
print('load credential.json ...')
with open('credential.json', 'r') as f:
    credentials = json.load(f)

# slackapp開始
print('start slackapp ...')
app = sa.slackapp(credentials['channel_api_key'], credentials['user_api_key'])

# channels情報を取得する
print('get channel info ...')
if app.request_chinfo() is False:
    print('failed to get channel info')
    sys.exit(1)

# メッセージ群を取得したいチャンネル名
print('load chlist_to_get.csv ...')
df_getting_chs = pd.read_csv(
    'chlist_to_get.csv',
    names=['index', 'channel_name']
    )
target_chname = df_getting_chs.channel_name.values.tolist()

# 各channelsのメッセージ群を取得する
print('get massages each channel ...')
for tc in target_chname:
    print('from : {0}'.format(tc))
    chid = app.get_channel_id(tc)
    if chid:
        r = app.request_msgs_in_channel(chid, tc)
        if r is False:
            print('failed to request messages in ch = ' + tc)
            sys.exit(1)

# users情報を取得する
print('get user info ...')
if app.request_usrinfo() is False:
    print('failed to get user info')
    sys.exit(1)

# 各チャンネルの情報をまとめたデータフレーム列作成
# カラム：user_name, text, timestamp
mic_val_dfs = []
for mic_key in app.messages_in_chs.keys():
    mic_val_df = app.messages_in_chs[mic_key]
    mic_val_dfs.append(mic_val_df)

# userごとに投稿内容をグルーピングする
print('group messages by user ...')
msgs_by_usr = {}
for df in mic_val_dfs:
    for index, row in df.iterrows():
        # ignore empty user name key
        if row[0] == '':
            continue
        # search user name
        uname = app.userInfo[row[0]]
        umsg = row[1]
        if uname not in msgs_by_usr.keys():
            msgs_by_usr[uname] = []
        umsg = umsg.replace('\n', '')
        msgs_by_usr[uname].append(umsg)

# userごとの投稿内容をJSON形式で保存
collect_msg_fpath = 'collect_msgs.json'
print('save file {0} ...'.format(collect_msg_fpath))
with open(collect_msg_fpath, 'w', encoding='utf-8') as f:
    json.dump(msgs_by_usr, f, indent=2, ensure_ascii=False)

# -----------------------------------------------------
# メッセージ文字列から不要な文字列を除外（データクレンジング）
# -----------------------------------------------------
# 未実装

# vectorizerオブジェクト生成
X_by_users = []
feature_by_users = []
analyzer = vectorizer.vectorizer()

# userごとの投稿内容をベクトル化
for uname, umsgs in msgs_by_usr.items():
    s = ''
    # 当該ユーザーの投稿を１Lineにまとめる
    for msg in umsgs:
        # チャンネル参加時の文字列を除去
        if 'さんがチャンネルに参加しました' in msg:
            continue
        s += msg
    if s == '':
        continue
    analyzer.vectorize_line(s)
    print('user : ' + str(uname) + '=============')
    print(analyzer.features)
    feature_by_users.append(analyzer.features)
    print(analyzer.X)
    X_by_users.append(analyzer.X)

# userごとの投稿内容テーブルを作成

    