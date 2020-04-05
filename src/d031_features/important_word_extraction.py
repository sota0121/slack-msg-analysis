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


def groupe_msgs_by_user(df_msgs: pd.DataFrame) -> dict:
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

def split_lastterm_other_records(df_all: pd.DataFrame, term: str) -> pd.DataFrame:
    # set term
    term_days = 8
    if term == 'lm':
        term_days = 31
    print('set term limit : {0} days'.format(term_days))
    
    # 3. extract
    now_in_sec = (datetime.now(JST) - datetime.fromtimestamp(0, JST)).total_seconds()
    recent_days = timedelta(days=term_days)
    recent_seconds = recent_days.total_seconds()
    print('extract messages last {0} days ...'.format(term_days))
    df_last = df_all.query('@now_in_sec - timestamp < @recent_seconds')
    df_other = df_all.query('@now_in_sec - timestamp >= @recent_seconds')
    return df_last, df_other


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
    msgs_grouped_by_user = groupe_msgs_by_user(df_msgs)
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

def extraction_of_lastterm(input_root: str, output_root: str, term: str) -> dict:
    # ---------------------------------------------
    # 1. load messages (processed)
    # ---------------------------------------------
    print('load msgs (all of history and last term) ...')
    msg_fpath = input_root + '/' + 'messages_cleaned_wakati_norm_rmsw.csv'
    df_msgs_all = pd.read_csv(msg_fpath)
    # ---------------------------------------------
    # 2. split last term and other messages, and save it as dict
    # ---------------------------------------------
    df_msgs_last, df_msgs_other = split_lastterm_other_records(df_msgs_all, term)
    # save it
    term_s = 'lastweek' if 'lw' == term else 'lastmonth'
    dict_msgs_last_other = {}
    dict_msgs_last_other[term_s] = ' '.join(df_msgs_last.wakati_msg.dropna().values.tolist())
    dict_msgs_last_other['other'] = ' '.join(df_msgs_other.wakati_msg.dropna().values.tolist())
    msg_grouped_fpath = input_root + '/' + 'messages_lastterm_other.json'
    with open(msg_grouped_fpath, 'w', encoding='utf-8') as f:
        json.dump(dict_msgs_last_other, f, ensure_ascii=False, indent=4)
    # ---------------------------------------------
    # 3. 全文書を対象にtf-idf計算
    # ---------------------------------------------
    print('tfidf vectorizing ...')
    # > 全文書にある単語がカラムで、文書数（=user）が行となる行列が作られる。各要素にはtf-idf値がある
    tfidf_vectorizer = TfidfVectorizer(token_pattern=u'(?u)\\b\\w+\\b')

    bow_vec = tfidf_vectorizer.fit_transform(dict_msgs_last_other.values())
    bow_array = bow_vec.toarray()
    bow_df = pd.DataFrame(bow_array,
                        index=dict_msgs_last_other.keys(),
                        columns=tfidf_vectorizer.get_feature_names())
    # ---------------------------------------------
    # 5. tf-idfに基づいて重要単語を抽出する
    # ---------------------------------------------
    print('extract important words ...')
    dict_word_score_by_term = extract_important_word_by_key(tfidf_vectorizer.get_feature_names(), bow_df, [term_s, 'other'])
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
        dic_words_and_score = extraction_of_lastterm(input_root, output_root, term)

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
