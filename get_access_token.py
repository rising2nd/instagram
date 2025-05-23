import requests
import json

def print_access_token(
    access_tokenA: str,
    app_id: str,
    app_secret: str
):

    # アクセストークンbを取得
    r = requests.get(f"https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={access_tokenA}")
    r = json.loads(r.text)
    access_tokenB = r['access_token']
    # print("access tokenB;",access_tokenB)

    # facebook_idを取得
    r = requests.get(f"https://graph.facebook.com/v21.0/me?access_token={access_tokenB}")
    r = json.loads(r.text)
    facebook_id = r["id"]

    # access_tokenCを取得
    r = requests.get(f"https://graph.facebook.com/v21.0/{facebook_id}/accounts?access_token={access_tokenB}")
    r = json.loads(r.text)
    access_tokenC = r["data"][0]['access_token']
    print(f"自分の無期限アクセストークン↓\n{access_tokenC}\n")

    response = requests.get("https://graph.facebook.com/" + "v22.0" + "/me?fields=instagram_business_account&access_token=" + access_tokenC)
    data = response.json()
    print("インスタグラムアカウントの内部ID：",data['instagram_business_account']["id"])

if __name__ == "__main__":

    access_tokenA = "xxx"
    app_id = "yyy"
    app_secret = "zzz"

    print_access_token(
        access_tokenA=access_tokenA,
        app_id=app_id,
        app_secret=app_secret
    )