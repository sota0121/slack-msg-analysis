# Text Processing : Normalize texts
# 1. 文字種の統一
#  1.1. アルファベットを小文字に統一
#  1.2. 半角文字を全角文字に統一
# 2. 数字の置き換え
#  2.1. 数字を全て0にする
# ** nltkを用いたlemmatizeも今後検討
import re
import pandas as pd
from tqdm import tqdm
import argparse
from pathlib import Path
import sys


def normarize_text(text: str):
    normalized_text = normalize_number(text)
    normalized_text = lower_text(normalized_text)
    return normalized_text


def normalize_number(text: str) -> str:
    """
    pattern = r'\d+'
    replacer = re.compile(pattern)
    result = replacer.sub('0', text)
    """
    # 連続した数字を0で置換
    replaced_text = re.sub(r'\d+', '0', text)
    return replaced_text


def lower_text(text: str) -> str:
    return text.lower()


def normalize_msgs(wktmsg_ser: pd.Series) -> pd.Series:
    normalized_msg_list = []
    for wktstr in tqdm(wktmsg_ser, desc='normalize words...'):
        normalized = normarize_text(str(wktstr))
        normalized_msg_list.append(normalized)
    normalized_msg_ser = pd.Series(normalized_msg_list)
    return normalized_msg_ser


def main(input_fname: str):
    input_root = '../../data/030_processed'
    output_root = input_root
    # 1. load wakati messages
    msgs_fpath = input_root + '/' + input_fname
    df_msgs = pd.read_csv(msgs_fpath)
    # 2. normalize wakati_msg (update)
    ser_msg = df_msgs.wakati_msg
    df_msgs.wakati_msg = normalize_msgs(ser_msg)
    # 3. save it
    pin = Path(msgs_fpath)
    msgs_ofpath = output_root + '/' + pin.stem + '_norm.csv'
    df_msgs.to_csv(msgs_ofpath, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_fname", help="set input file name", type=str)
    args = parser.parse_args()
    input_fname = args.input_fname
    # input file must been cleaned
    if 'wakati' not in input_fname:
        print('input file name is invalid.: {0}'.format(input_fname))
        print('input file name must include \'wakati\'')
        sys.exit(1)
    main(input_fname)
