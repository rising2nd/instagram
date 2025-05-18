import os
import requests
import json


def print_my_posts(
    api_version: str,
    access_token: str,
    user_id: str
):

    # エンドポイントURLの作成
    graph_domain = 'https://graph.facebook.com/'
    endpoint_base = f"{graph_domain}{API_VERSION}/"
    url = f"{endpoint_base}{USER_ID}/media"

    # リクエストパラメータの設定
    params = {
        'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username',
        'access_token': ACCESS_TOKEN
    }

    # APIリクエストの送信
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # HTTPエラーが発生した場合例外をスロー
        media_response = response.json()
    except requests.exceptions.RequestException as e:
        print(f"HTTPリクエスト中にエラーが発生しました: {e}")
        media_response = None
    except json.JSONDecodeError as e:
        print(f"JSONのパース中にエラーが発生しました: {e}")
        media_response = None

    # 取得したデータの表示
    # URLは約8時間で無効になることに注意
    print(f"\n---------- {media_response['data'][0]['username']}の投稿内容 ----------\n")
    for i, post in enumerate(media_response['data'], start=1):
        print(f"\n---------- 投稿内容({i}) ----------\n")
        print(f"投稿日: {post['timestamp']}")
        print(f"投稿メディアID: {post['id']}")
        print(f"メディア種別: {post['media_type']}")
        print(f"投稿リンク: {post['permalink']}")
        print(f"\n投稿文: {post.get('caption', 'なし')}")

if __name__ == "__main__":
    # 環境変数から取得
    API_VERSION = "v22.0"
    ACCESS_TOKEN = "xxx"
    USER_ID = "yyy"

    print_my_posts(
        api_version=API_VERSION,
        access_token=ACCESS_TOKEN,
        user_id=USER_ID
    )