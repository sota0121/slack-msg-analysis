# Text Processing : Cleaning text noise
# 現段階のクリーニング対象
# - Return and Space : regex >> "\s"
# - url link (<https://...>): regex >> "(<)http.+(>)"
# - reaction (:grin:) : regex >> "(:).+\w(:)"
# - html kw (&lt;, 	&gt;, &amp;, &nbsp;, &ensp;, &emsp;, &ndash;, &mdash;) : regex >> "(&).+?\w(;)"
# - mention (<@XXXXXX>) : regex >> "(<)@.+\w(>)"
# - inline code block : regex >> "(`).+(`)"
# - multi lines code block : regex >> "(```).+(```)"
import re
import pandas as pd
import argparse
from pathlib import Path


def clean_msg(msg: str) -> str:
    # sub 'Return and Space'
    result = re.sub(r'\s', '', msg)
    # sub 'url link'
    result = re.sub(r'(<)http.+(>)', '', result)
    # sub 'mention'
    result = re.sub(r'(<)@.+\w(>)', '', result)
    # sub 'reaction'
    result = re.sub(r'(:).+\w(:)', '', result)
    # sub 'html key words'
    result = re.sub(r'(&).+?\w(;)', '', result)
    # sub 'multi lines code block'
    result = re.sub(r'(```).+(```)', '', result)
    # sub 'inline code block'
    result = re.sub(r'(`).+(`)', '', result)
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


def get_ch_id_from_table(ch_name_parts: list, input_fpath: str) -> list:
    df_ch = pd.read_csv(input_fpath)
    ch_id = []
    for ch_name_part in ch_name_parts:
        for i, row in df_ch.iterrows():
            if ch_name_part in row.ch_name:
                ch_id.append(row.ch_id)
                break
    return ch_id


def main(input_fname: str):
    input_root = '../../data/020_intermediate'
    output_root = input_root
    # 1. load messages.csv (including noise)
    msgs_fpath = input_root + '/' + input_fname
    df_msgs = pd.read_csv(msgs_fpath)
    print('load :{0}'.format(msgs_fpath))
    # 2. Drop Not Target Records
    print('drop records (drop non-target channel\'s messages)')
    non_target_ch_name = ['general', '運営からのアナウンス']
    non_target_ch_ids = get_ch_id_from_table(non_target_ch_name, input_root + '/' + 'channels.csv')
    print('=== non target channels bellow ====')
    print(non_target_ch_ids)
    for non_target_ch_id in non_target_ch_ids:
        df_msgs = df_msgs.query('ch_id != @non_target_ch_id')
    # 3. clean message string list
    ser_msg = df_msgs.msg
    df_msgs.msg = clean_msg_ser(ser_msg)
    # 4. save it
    pin = Path(msgs_fpath)
    msgs_cleaned_fpath = output_root + '/' + pin.stem + '_cleaned.csv'
    df_msgs.to_csv(msgs_cleaned_fpath, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_fname", help="set input file name", type=str)
    args = parser.parse_args()
    input_fname = args.input_fname
    main(input_fname)
