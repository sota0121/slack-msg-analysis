# slackapiを使って所望の情報を取得するクラス
import sys
import json
sys.path.append('../../src/d000_utils')
import slack_app as sa


def main():
    # -------------------------------------
    # load api token
    # -------------------------------------
    credentials_root = '../../conf/local/'
    credential_fpath = credentials_root + 'credentials.json'
    print('load credential.json ...')
    with open(credential_fpath, 'r') as f:
        credentials = json.load(f)
    # -------------------------------------
    # start slack app
    # -------------------------------------    
    print('start slack app ...')
    app = sa.SlackApp(
        credentials['channel_api_key'],
        credentials['user_api_key']
        )
    outdir = '../../data/010_raw'
    # -------------------------------------
    # get channels info
    # -------------------------------------
    app.load_save_channel_info(outdir)
    # -------------------------------------
    # get user info
    # -------------------------------------
    app.load_save_user_info(outdir)
    # -------------------------------------
    # get msg info
    # -------------------------------------
    app.load_save_messages_info(outdir)


if __name__ == "__main__":
    main()
