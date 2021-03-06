# Feature Extraction : ImportantWordExtraction
# - ある文書群（ここではSlackの投稿メッセージ群）における
# - 各単語の重要度を数値化するモジュール
# - ただし、ノイズ除去や正規化はすでに完了しているものとする

import pandas as pd
import json
from datetime import datetime, date, timedelta, timezone
from pathlib import Path
import argparse
import sys
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
JST = timezone(timedelta(hours=+9), 'JST')


def group_msgs_by_user(df_msgs: pd.DataFrame) -> dict:
    ser_uid = df_msgs.uid
    ser_wktmsg = df_msgs.wakati_msg
    # 重複なしのuid一覧を取得
    ser_uid_unique = df_msgs.drop_duplicates(subset='uid').uid
    # 重複なしuidごとにグルーピング
    dict_msgs_by_user = {}
    for uid in ser_uid_unique:
        # 当該uidに該当する全wktmsgを取得
        extracted = df_msgs.query('uid == @uid')
        # key, value を出力用の辞書に追加
        dict_msgs_by_user[uid] = ' '.join(extracted.wakati_msg.dropna().values.tolist())        
    return dict_msgs_by_user


def group_msgs_by_term(df_msgs: pd.DataFrame, term: str) -> dict:
    # set term
    term_days = 8
    if term == 'lm':
        term_days = 31
    print('group messages every {0} days'.format(term_days))
    # analyze timestamp
    now_in_sec = (datetime.now(JST) - datetime.fromtimestamp(0, JST)).total_seconds()
    interval_days = timedelta(days=term_days)
    interval_seconds = interval_days.total_seconds()
    oldest_timestamp = df_msgs.min().timestamp
    oldest_ts_in_sec = (datetime.fromtimestamp(oldest_timestamp, JST) - datetime.fromtimestamp(0, JST)).total_seconds()
    loop_num = (abs(now_in_sec - oldest_ts_in_sec) / interval_seconds) + 1
    # extract by term
    dict_msgs_by_term = {}
    df_tmp = df_msgs
    now_tmp = now_in_sec
    for i in range(int(loop_num)):
        # make current term string
        cur_term_s = 'term_ago_{0}'.format(str(i).zfill(3))
        print(cur_term_s)
        # current messages
        df_msgs_cur = df_tmp.query('@now_tmp - timestamp < @interval_seconds')
        df_msgs_other = df_tmp.query('@now_tmp - timestamp >= @interval_seconds')
        # messages does not exist. break.
        if df_msgs_cur.shape[0] == 0:
            break
        # add current messages to dict
        dict_msgs_by_term[cur_term_s] = ' '.join(df_msgs_cur.wakati_msg.dropna().values.tolist())
        # update temp value for next loop
        now_tmp = now_tmp - interval_seconds
        df_tmp = df_msgs_other
    return dict_msgs_by_term
    

def extract_important_word_by_key(feature_names: list, bow_df: pd.DataFrame, uids: list) -> dict:
    # > 行ごと、つまりユーザーごとにみていき、重要単語を抽出する(tfidf上位X個の単語)
    dict_important_words_by_user = {}
    for uid, (i, scores) in zip(uids, bow_df.iterrows()):
        # 当該ユーザーの単語・tfidfスコアのテーブルを作る
        words_score_tbl = pd.DataFrame()
        words_score_tbl['scores'] = scores
        words_score_tbl['words'] = feature_names
        # tfidfスコアで降順ソートする
        words_score_tbl = words_score_tbl.sort_values('scores', ascending=False)
        words_score_tbl = words_score_tbl.reset_index()
        # extract : tf-idf score > 0.001
        important_words = words_score_tbl.query('scores > 0.001')
        # 当該ユーザの辞書作成 'uid0': {'w0': 0.9, 'w1': 0.87}
        d = {}
        for i, row in important_words.iterrows():
            d[row.words] = row.scores
        # 当該ユーザの辞書にワードが少なくとも一つ以上ある場合のみテーブルに追加
        if len(d.keys()) > 0:
            dict_important_words_by_user[uid] = d
    return dict_important_words_by_user

def extraction_by_user(input_root: str, output_root: str) -> dict:
    # ---------------------------------------------
    # 1. load messages (processed)
    # ---------------------------------------------
    msg_fpath = input_root + '/' + 'messages_cleaned_wakati_norm_rmsw.csv'
    print('load: {0}'.format(msg_fpath))
    df_msgs = pd.read_csv(msg_fpath)
    # ---------------------------------------------
    # 2. group messages by user
    # ---------------------------------------------
    print('group messages by user and save it.')
    msgs_grouped_by_user = group_msgs_by_user(df_msgs)
    msg_grouped_fpath = input_root + '/' + 'messages_grouped_by_user.json'
    with open(msg_grouped_fpath, 'w', encoding='utf-8') as f:
        json.dump(msgs_grouped_by_user, f, ensure_ascii=False, indent=4)
    # ---------------------------------------------
    # 4. 全文書を対象にtf-idf計算
    # ---------------------------------------------
    print('tfidf vectorizing ...')
    # > 全文書にある単語がカラムで、文書数（=user）が行となる行列が作られる。各要素にはtf-idf値がある
    tfidf_vectorizer = TfidfVectorizer(token_pattern=u'(?u)\\b\\w+\\b')

    bow_vec = tfidf_vectorizer.fit_transform(msgs_grouped_by_user.values())
    bow_array = bow_vec.toarray()
    bow_df = pd.DataFrame(bow_array,
                        index=msgs_grouped_by_user.keys(),
                        columns=tfidf_vectorizer.get_feature_names())
    # ---------------------------------------------
    # 5. tf-idfに基づいて重要単語を抽出する
    # ---------------------------------------------
    print('extract important words ...')
    d_word_score_by_uid = extract_important_word_by_key(tfidf_vectorizer.get_feature_names(), bow_df, msgs_grouped_by_user.keys())
    # # test output
    # with open(output_root + '/' + 'important_words_tfidf.json', 'w', encoding='utf-8') as f:
    #     json.dump(d_word_score_by_uid, f, ensure_ascii=False, indent=4)
    # return
    # ---------------------------------------------
    # 6. uid => uname 変換
    # ---------------------------------------------
    print('ユーザーごとの重要単語群のキーをuidからunameに変換 ...')
    user_tbl = pd.read_csv('../../data/020_intermediate/users.csv')
    d_word_score_by_uname = {}
    for uid, val in d_word_score_by_uid.items():
        # 発言者のuidでunameを検索（アクティブユーザーでない場合存在しない可能性あり）
        target = user_tbl.query('uid == @uid')
        if target.shape[0] != 0:
            uname = target.iloc[0]['uname']
        else:
            continue
        print('uname: ', uname, 'type of uname: ', type(uname))
        d_word_score_by_uname[uname] = val
    return d_word_score_by_uname


def extraction_by_term(input_root: str, output_root: str, term: str) -> dict:
    # ---------------------------------------------
    # 1. load messages (processed)
    # ---------------------------------------------
    print('load msgs (all of history and last term) ...')
    msg_fpath = input_root + '/' + 'messages_cleaned_wakati_norm_rmsw.csv'
    df_msgs_all = pd.read_csv(msg_fpath)
    # ---------------------------------------------
    # 2. group messages by term
    # ---------------------------------------------
    print('group messages by term and save it.')
    msgs_grouped_by_term = group_msgs_by_term(df_msgs_all, term)
    msg_grouped_fpath = input_root + '/' + 'messages_grouped_by_term.json'
    with open(msg_grouped_fpath, 'w', encoding='utf-8') as f:
        json.dump(msgs_grouped_by_term, f, ensure_ascii=False, indent=4)
    # ---------------------------------------------
    # 3. 全文書を対象にtf-idf計算
    # ---------------------------------------------
    print('tfidf vectorizing ...')
    # > 全文書にある単語がカラムで、文書数（=user）が行となる行列が作られる。各要素にはtf-idf値がある
    tfidf_vectorizer = TfidfVectorizer(token_pattern=u'(?u)\\b\\w+\\b')

    bow_vec = tfidf_vectorizer.fit_transform(msgs_grouped_by_term.values())
    bow_array = bow_vec.toarray()
    bow_df = pd.DataFrame(bow_array,
                        index=msgs_grouped_by_term.keys(),
                        columns=tfidf_vectorizer.get_feature_names())
    # ---------------------------------------------
    # 5. tf-idfに基づいて重要単語を抽出する
    # ---------------------------------------------
    print('extract important words ...')
    dict_word_score_by_term = extract_important_word_by_key(
        tfidf_vectorizer.get_feature_names(),
        bow_df, msgs_grouped_by_term.keys())
    return dict_word_score_by_term


def main(mode: int, term: str):
    input_root = '../../data/030_processed'
    output_root = '../../data/031_features'
    # =======================
    # MAIN PROCESS
    # =======================
    dic_words_and_score = {}
    if mode == 0:
        print('extract important words with tfidf by user.')
        dic_words_and_score = extraction_by_user(input_root, output_root)
    else:
        print('extract important words with tfidf of last term vs all history.')
        dic_words_and_score = extraction_by_term(input_root, output_root, term)

    # =======================
    # OUTPUT
    # =======================
    suffix = 'by_user' if mode == 0 else 'by_term'
    with open(output_root + '/' + 'important_words_tfidf_{0}.json'.format(suffix), 'w', encoding='utf-8') as f:
        json.dump(dic_words_and_score, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="0: tfidf by user, 1: tfidf of last term vs all history", type=int)
    parser.add_argument("--term", help="lw: tfidf of last week, lm: tfidf of last month", type=str)
    args = parser.parse_args()
    # get arguments
    mode = args.mode
    if (mode != 0) and (mode != 1):
        print('invalid args mode. please exe with -h option')
        sys.exit(1)
    term = args.term
    if mode == 1:
        if (term != 'lw') and (term != 'lm'):
            print('invalid args --term. please exe with -h option')
            sys.exit(1)
    main(mode, term)
