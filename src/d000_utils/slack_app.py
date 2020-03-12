# slackapiを使って所望の情報を取得するクラス(加工はしない)
import requests
import pandas as pd


class slackapp:
    ch_list_url = 'https://slack.com/api/channels.list'
    ch_history_url = 'https://slack.com/api/channels.history'
    usr_list_url = 'https://slack.com/api/users.list'

    def __init__(self, ch_api_key, usr_api_key):
        self.channelInfo = {}  # k: ch_name, v: ch_id
        self.messages_in_chs = {}
        self.userInfo = {}
        self.ch_api_token = str(ch_api_key)
        self.usr_api_token = str(usr_api_key)

    def request_channel_info(self):
        # slackAPI 経由で channels.listを取得してchannelInfoに格納
        payload = {'token': self.ch_api_token}
        response = requests.get(slackapp.ch_list_url, params=payload)
        if response.status_code == 200:
            json_data = response.json()
            if 'channels' in json_data.keys():
                channels = json_data['channels']
                for ci in channels:
                    self.channelInfo[ci['name']] = ci['id']
                return True
        return False

    def request_msgs_in_channel(self, chid, ch_name):
        # slackAPI 経由で channels.historyを取得してchannel毎にmessages_in_channelsに格納
        payload = {'token': self.ch_api_token, 'channel': chid}
        response = requests.get(slackapp.ch_history_url, params=payload)
        if response.status_code == 200:
            json_data = response.json()
            if 'messages' in json_data.keys():
                res_msgs = json_data['messages']
                users = []
                texts = []
                timestamps = []
                for rm in res_msgs:
                    users.append(rm['user'] if 'user' in rm.keys() else '')
                    texts.append(rm['text'] if 'text' in rm.keys() else '')
                    timestamps.append(rm['ts'] if 'ts' in rm.keys() else '')

                messages_in_ch = pd.DataFrame({
                    'user': users,
                    'text': texts,
                    'timestamp': timestamps
                    })
                self.messages_in_chs[ch_name] = messages_in_ch
                return True
        return False

    def request_usr_info(self):
        # slackAPI 経由で user情報を取得してuserInfoに格納
        payload = {'token': self.usr_api_token}
        response = requests.get(slackapp.usr_list_url, params=payload)
        if response.status_code == 200:
            json_data = response.json()
            if 'members' in json_data.keys():
                members = json_data['members']
                for m in members:
                    self.userInfo[m['id']] = m['name']
                return True
        return False

    def get_channel_id(self, ch_name):
        # channel名を指定してchannelIDを取得
        # channelInfoが空の場合は、slackAPI経由で取得する
        if len(self.channelInfo.keys()) == 0:
            self.request_channel_info()
        if ch_name in self.channelInfo.keys():
            chid = self.channelInfo[ch_name]
            return chid
        else:
            print('invalid channel name is input : ' + ch_name)
            return ''

    def list_channel_names(self, sep=','):
        # channel名を標準出力する
        # channelInfoが空の場合は、slackAPI経由で取得する
        if len(self.channelInfo.keys()) == 0:
            self.request_channel_info()
        for i, chn in enumerate(self.channelInfo.keys()):
            print('{0}{2}{1}'.format(i, chn, sep))

    def get_usr_info(self):
        # userInfoが空の場合slackAPI経由で取得する
        if len(self.userInfo.keys()) == 0:
            self.request_usr_info()
        return self.userInfo
