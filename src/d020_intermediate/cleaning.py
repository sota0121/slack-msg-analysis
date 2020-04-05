# Text Processing : Cleaning text noise
# 現段階のクリーニング対象
# - url link (<https://...>): regex >> "(<)http.+(>)"
# - reaction (:grin:) : regex >> "(:).+\w(:)"
# - html kw (&lt;, 	&gt;, &amp;, &nbsp;, &ensp;, &emsp;, &ndash;, &mdash;) : regex >> "(&).+?\w(;)"
# - mention (<@XXXXXX>) : regex >> "(<)@.+\w(>)"
import re
import pandas as pd
import argparse
from pathlib import Path


def clean_msg(msg: str) -> str:
    # sub 'url link'
    result = re.sub(r'(<)http.+(>)', '', msg)
    # sub 'mention'
    result = re.sub(r'(<)@.+\w(>)', '', result)
    # sub 'reaction'
    result = re.sub(r'(:).+\w(:)', '', result)
    # sub 'html key words'
    result = re.sub(r'(&).+?\w(;)', '', result)
    return result


def clean_msg_ser(msg_ser: pd.Series) -> pd.Series:
    cleaned_msg_list = []
    for i, msg in enumerate(msg_ser):
        cleaned_msg = clean_msg(str(msg))
        if 'チャンネルに参加しました' in cleaned_msg:
            continue
        cleaned_msg_list.append(cleaned_msg)
    cleaned_msg_ser = pd.Series(cleaned_msg_list)
    return cleaned_msg_ser


def main(input_fname: str):
    input_root = '../../data/020_intermediate'
    output_root = input_root
    # 1. load messages.csv (including noise)
    msgs_fpath = input_root + '/' + input_fname
    df_msgs = pd.read_csv(msgs_fpath)
    # 2. clean message string list
    ser_msg = df_msgs.msg
    df_msgs.msg = clean_msg_ser(ser_msg)
    # 3. save it
    pin = Path(msgs_fpath)
    msgs_cleaned_fpath = output_root + '/' + pin.stem + '_cleaned.csv'
    df_msgs.to_csv(msgs_cleaned_fpath, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_fname", help="set input file name", type=str)
    args = parser.parse_args()
    input_fname = args.input_fname
    main(input_fname)
