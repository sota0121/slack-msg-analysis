# Feature Extraction : ImportantWordExtraction
# - ある文書群（ここではSlackの投稿メッセージ群）における
# - 各単語の重要度を数値化するモジュール
# - ただし、ノイズ除去や正規化はすでに完了しているものとする

import pandas as pd
import json
from pathlib import Path
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer


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


def extract_important_word_by_user(feature_names: list, bow_df: pd.DataFrame, uids: list) -> dict:
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
        # 上位50単語を抽出(ただし、最低スコア0.1)
        important_words = words_score_tbl.head(50)
        important_words = important_words.query('scores > 0.01')
        # 当該ユーザの辞書作成 'uid0': {'w0': 0.9, 'w1': 0.87}
        d = {}
        for i, row in important_words.iterrows():
            d[row.words] = row.scores
        dict_important_words_by_user[uid] = d
    return dict_important_words_by_user

def main():
    input_root = '../../data/030_processed'
    output_root = '../../data/031_features'
    # ---------------------------------------------
    # 1. load messages (processed)
    # ---------------------------------------------
    msg_fpath = input_root + '/' + 'messages_wkt_norm_swremoved.csv'
    df_msgs = pd.read_csv(msg_fpath)
    # ---------------------------------------------
    # 2. group messages by user
    # ---------------------------------------------
    msgs_grouped_by_user = groupe_msgs_by_user(df_msgs)
    msg_grouped_fpath = input_root + '/' + 'messages_grouped_by_user.json'
    with open(msg_grouped_fpath, 'w', encoding='utf-8') as f:
        json.dump(msgs_grouped_by_user, f, ensure_ascii=False, indent=4)
    # ---------------------------------------------
    # 4. 全文書を対象にtf-idf計算
    # ---------------------------------------------
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
    d_word_score_by_uid = extract_important_word_by_user(tfidf_vectorizer.get_feature_names(), bow_df, msgs_grouped_by_user.keys())
    # # test output
    # with open(output_root + '/' + 'important_words_tfidf.json', 'w', encoding='utf-8') as f:
    #     json.dump(d_word_score_by_uid, f, ensure_ascii=False, indent=4)
    # return
    # ---------------------------------------------
    # 6. uid => uname 変換
    # ---------------------------------------------
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
    # ---------------------------------------------
    # 7. userごとに抽出した単語群を出力する
    # ---------------------------------------------
    with open(output_root + '/' + 'important_words_tfidf.json', 'w', encoding='utf-8') as f:
        json.dump(d_word_score_by_uname, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
