# Text processing : StopWordRemoval
# 1. ストップワード除去
#   - messages_wkt_norm['wakati_msg']から
#   - ストップワードを除去
#   - 当該カラムの値を更新
#   - messages_wkt_norm_swrmv.csv を保存

import pandas as pd
import urllib.request
from pathlib import Path
from tqdm import tqdm


def maybe_download(path: str):
    stopword_def_page_url = 'http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt'
    p = Path(path)
    if p.exists():
        print('File already exists.')
    else:
        print('downloading stop words definition ...')
        # Download the file from `url` and save it locally under `file_name`:
        urllib.request.urlretrieve(stopword_def_page_url, path)
    # stop word 追加分
    sw_added_list = [
        '-',
        'ー',
        'w',
        'W',
        'm',
        '笑'
    ]
    sw_added_str = '\n'.join(sw_added_list)
    with open(path, 'a') as f:
        print(sw_added_str, file=f)


def load_sw_definition(path: str) -> list:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.read()
        line_list = lines.split('\n')
        line_list = [x for x in line_list if x != '']
    return line_list


def remove_sw_from_text(wktstr: str, stopwords: list) -> str:
    words_list = wktstr.split(' ')
    words_list_swrm = [x for x in words_list if x not in stopwords]
    swremoved_str = ' '.join(words_list_swrm)
    return swremoved_str


def remove_sw_from_msgs(wktmsg_ser: pd.Series, stopwords: list) -> pd.Series:
    swremved_msg_list = []
    for wktstr in tqdm(wktmsg_ser, desc='remove stopwords...'):
        removed_str = remove_sw_from_text(str(wktstr), stopwords)
        swremved_msg_list.append(removed_str)
    swremved_msg_ser = pd.Series(swremved_msg_list)
    return swremved_msg_ser


def main():
    input_root = '../../data/030_processed'
    output_root = input_root
    # 1. load stop words
    sw_def_fpath = 'stopwords.txt'
    maybe_download(sw_def_fpath)
    stopwords = load_sw_definition(sw_def_fpath)
    # 2. load messages
    msgs_fpath = input_root + '/' + 'messages_wkt_norm.csv'
    df_msgs = pd.read_csv(msgs_fpath)
    # 3. remove stop words
    ser_msg = df_msgs.wakati_msg
    df_msgs.wakati_msg = remove_sw_from_msgs(ser_msg, stopwords)
    # 4. save it
    msgs_ofpath = output_root + '/' + 'messages_wkt_norm_swremoved.csv'
    df_msgs.to_csv(msgs_ofpath, index=False)


if __name__ == "__main__":
    main()
