# DLG Slack ws の任意チャンネルのメッセージ群を取得する
import sys
import pandas as pd
import json
import re
import slackapp as sa
import vectorizer
from tqdm import tqdm


# userごとの投稿メッセージ列から不要な文字列を削除する
# * 除外対象のメッセージ *
#  - チャンネル参加時のメッセージ「XXXさんがチャンネルに参加しました」は列ごと消去
#  - URLが含まれる場合は、URLのみ消去
def cleansing_msgs(msgs_by_user):
    pattern_url = re.compile(r'\<.*?\>')
    ret_tbl = {}
    for uname, umsgs in msgs_by_user.items():
        ret_umsgs = []
        for umsg in umsgs:
            # ignore "join channel" msg
            if 'さんがチャンネルに参加しました' in umsg:
                continue
            # exclude url string
            umsg = pattern_url.sub('', umsg)
            ret_umsgs.append(umsg)
        ret_tbl[uname] = ret_umsgs
    return ret_tbl


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

# users情報を出力する
userinfo = app.get_usrinfo()
sr_user_id = pd.Series(list(userinfo.keys()))
sr_user_name = pd.Series(list(userinfo.values()))
df_userinfo = pd.concat(
    [sr_user_id, sr_user_name], axis=1)
df_userinfo = df_userinfo.rename(columns={0: 'usr_id', 1: 'usr_name'})
df_userinfo.to_csv('userinfo.csv', index=False)

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

# -----------------------------------------------------
# メッセージ文字列から不要な文字列を除外（データクレンジング）
# -----------------------------------------------------
print('cleansing data ...')
msgs_by_usr = cleansing_msgs(msgs_by_usr)

# userごとの投稿内容をJSON形式で保存
collect_msg_fpath = 'collect_msgs.json'
print('save file {0} ...'.format(collect_msg_fpath))
with open(collect_msg_fpath, 'w', encoding='utf-8') as f:
    json.dump(msgs_by_usr, f, indent=2, ensure_ascii=False)

# vectorizerオブジェクト生成
X_by_users = []
feature_by_users = []
analyzer = vectorizer.vectorizer()

# userごとの投稿内容をベクトル化して保存
print('save countvectorized data (this has not been implemented  yet) ...')
for uname, umsgs in msgs_by_usr.items():
    s = ''
    # 当該ユーザーの投稿を１Lineにまとめる
    s = ''.join(umsgs)
    analyzer.vectorize_line(s)
    print('user : ' + str(uname) + '=============')
    feature_by_users.append(analyzer.features)
    X_by_users.append(analyzer.X)
    # save func have not been implemented yet.

# userごとの投稿内容の頻度データを保存
print('save frequency of words by users(名詞を対象) ...')
freq_info_dict = {}
for uname, umsgs in tqdm(msgs_by_usr.items(), desc="[analyze freq]"):
    # 当該ユーザーの投稿を１Lineにまとめる
    s = ''.join(umsgs)
    freq = analyzer.frequency_info(s, part_of_speech='名詞')
    freq_info_dict[uname] = freq
with open('frequency_of_words.json', 'w', encoding='utf-8') as fw:
    json.dump(freq_info_dict, fw, indent=4, ensure_ascii=False)
