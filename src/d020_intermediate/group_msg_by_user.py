import json
import pandas as pd


def make_user_table(usr_dict: dict) -> pd.DataFrame:
    uid_list = []
    uname_list = []
    for usr_ditem in usr_dict:
        if usr_ditem['deleted'] == True:
            continue
        uid_list.append(usr_ditem['id'])
        uname_list.append(usr_ditem['profile']['real_name_normalized'])
    user_table = pd.DataFrame({'uid': uid_list, 'uname': uname_list})
    return user_table


def make_msg_table(msg_dict: dict) -> pd.DataFrame:
    ch_id_list = []
    msg_list = []
    uid_list = []
    ts_list = []
    for msg_ditem in msg_dict:
        if 'channel_id' in msg_ditem.keys():
            ch_id = msg_ditem['channel_id']
        else:
            continue
        if 'messages' in msg_ditem.keys():
            msgs_in_ch = msg_ditem['messages']
        else:
            continue
        # get message in channel
        for i, msg in enumerate(msgs_in_ch):
            # if msg by bot, continue
            if 'user' not in msg:
                continue
            ch_id_list.append(ch_id)
            msg_list.append(msg['text'])
            uid_list.append(msg['user'])  # botの場合はこのキーがない
            ts_list.append(msg['ts'])
    df_msgs = pd.DataFrame({
        'ch_id': ch_id_list,
        'msg': msg_list,
        'uid': uid_list,
        'timestamp': ts_list
    })
    return df_msgs


def make_ch_table(ch_dict: dict) -> pd.DataFrame:
    chid_list = []
    chname_list = []
    chnormname_list = []
    chmembernum_list = []
    for ch_ditem in ch_dict:
        chid_list.append(ch_ditem['id'])
        chname_list.append(ch_ditem['name'])
        chnormname_list.append(ch_ditem['name_normalized'])
        chmembernum_list.append(ch_ditem['num_members'])
    ch_table = pd.DataFrame({
        'ch_id': chid_list,
        'ch_name': chname_list,
        'ch_namenorm': chnormname_list,
        'ch_membernum': chmembernum_list
    })
    return ch_table


def main():
    # 1. load user/message/channels
    input_root = '../../data/010_raw'
    user_info_fpath = input_root + '/' + 'user_info.json'
    with open(user_info_fpath, 'r', encoding='utf-8') as f:
        user_info_rawdict = json.load(f)
        print('load ... ', user_info_fpath)
    msg_info_fpath = input_root + '/' + 'messages_info.json'
    with open(msg_info_fpath, 'r', encoding='utf-8') as f:
        msgs_info_rawdict = json.load(f)
        print('load ... ', msg_info_fpath)
    ch_info_fpath = input_root + '/' + 'channel_info.json'
    with open(ch_info_fpath, 'r', encoding='utf-8') as f:
        ch_info_rawdict = json.load(f)
        print('load ... ', ch_info_fpath)
    # 2. make and save tables
    # user
    output_root = '../../data/020_intermediate'
    df_user_info = make_user_table(user_info_rawdict)
    user_tbl_fpath = output_root + '/' + 'users.csv'
    df_user_info.to_csv(user_tbl_fpath, index=False)
    print('save ... ', user_tbl_fpath)
    # msg
    df_msg_info = make_msg_table(msgs_info_rawdict)
    msg_tbl_fpath = output_root + '/' + 'messages.csv'
    df_msg_info.to_csv(msg_tbl_fpath, index=False)
    print('save ... ', msg_tbl_fpath)
    # channel
    df_ch_info = make_ch_table(ch_info_rawdict)
    ch_tbl_fpath = output_root + '/' + 'channels.csv'
    df_ch_info.to_csv(ch_tbl_fpath, index=False)
    print('save ... ', ch_tbl_fpath)


if __name__ == "__main__":
    main()