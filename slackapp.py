# slackapiを使って所望の情報を取得するクラス
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
    
    def get_channel_id(self, chname):
        if chname in self.channelInfo.keys():
            chid = self.channelInfo[chname]
            return chid
        else:
            print('invalid channel name is input : ' + chname)
            return ''
    
    def list_channel_names(self, sep=','):
        for i, chn in enumerate(self.channelInfo.keys()):
            print('{0}{2}{1}'.format(i, chn, sep))

    def request_usrinfo(self):
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

    def request_chinfo(self):
        # channels.listを取得してchannelInfoに格納
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
    
    def request_msgs_in_channel(self, chid, chname):
        # channels.historyを取得してmessages_in_channelsに格納
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
                self.messages_in_chs[chname] = messages_in_ch
                return True
        return False
