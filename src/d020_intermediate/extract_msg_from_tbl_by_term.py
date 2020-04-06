# 期間を指定して、msg table (messages.csv) からメッセージを抽出する
from datetime import datetime, date, timedelta, timezone
import argparse
import sys
import pandas as pd
JST = timezone(timedelta(hours=+9), 'JST')


def main(term: str):
    input_root = '../../data/020_intermediate'
    output_root = input_root
    # 1. load messages.csv (including noise)
    msgs_fpath = input_root + '/' + 'messages.csv'
    df_msgs = pd.read_csv(msgs_fpath)
    print('load messages.csv ...')

    # 2. set term
    term_days = 8
    if term == 'lm':
        term_days = 31
    print('set term limit : {0} days'.format(term_days))
    
    # 3. extract
    now_in_sec = (datetime.now(JST) - datetime.fromtimestamp(0, JST)).total_seconds()
    recent_days = timedelta(days=term_days)
    recent_seconds = recent_days.total_seconds()
    print('extract messages last {0} days ...'.format(term_days))
    df_last = df_msgs.query('@now_in_sec - timestamp < @recent_seconds')
    
    # 3. save it
    suffix = 'lastweek' if term == 'lw' else 'lastmonth'
    msgs_last_fpath = output_root + '/' + 'messages_{0}.csv'.format(suffix)
    df_last.to_csv(msgs_last_fpath, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("term", help="lw: last week, lm: last month(30 days)", type=str)
    args = parser.parse_args()
    term_s = args.term
    if (term_s != 'lw') and (term_s != 'lm'):
        print('args0 is invalid. (lw or lm)')
        sys.exit(1)
    main(term_s)

