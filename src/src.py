import pandas as pd
import requests
import datetime
from dateutil.parser import isoparse

def convert_timestamp_to_jst_formatted(timestamp_str):
    """
    UTC タイムスタンプ文字列を JST の YYYY-MM-DD HH:MM 形式に変換します。

    Args:
        timestamp_str (str): UTC タイムスタンプの文字列 (例: '2025-04-23T12:51:44+0000').

    Returns:
T 形式のタイムスタンプ文字列 (例: '2025-04-23 21:51').
             変換に失敗した場合は None を返します。
    """
    jst_offset = datetime.timedelta(hours=9)
    try:
        # dateutil.parser.isoparse を使用して解析
        utc_dt = isoparse(timestamp_str)
        # タイムゾーン情報がない場合に UTC を指定（もしあればそのまま）
        if utc_dt.tzinfo is None or utc_dt.tzinfo.utcoffset(utc_dt) is None:
            utc_dt = utc_dt.replace(tzinfo=datetime.timezone.utc)
        # UTC に JST のオフセットを加算
        jst_dt = utc_dt + jst_offset
        # 指定の形式にフォーマット
        return jst_dt.strftime('%Y-%m-%d %H:%M')
    except ValueError:
        print(f"Warning: Could not parse timestamp string: {timestamp_str}")
        return None

def get_all_my_posts(
    user_id: str,
    access_token: str,
    api_version: str,
    num_iterations: int = 100
) -> pd.DataFrame :

    # --------
    # エンドポイントURLの作成
    # --------
    graph_domain = 'https://graph.facebook.com/'
    endpoint_base = f"{graph_domain}{api_version}/"
    url = f"{endpoint_base}{user_id}/media"

    # --------
    # リクエストパラメータの設定
    # --------
    params = {
        'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username,comments_count,like_count',
        'access_token': access_token
    }

    # --------
    # 一度に25個だけ取得できるため、while文で取得する
    # --------
    results = []
    cnt = 0
    jst_offset = datetime.timedelta(hours=9)

    response = requests.get(url, params=params)
    response.raise_for_status()  # HTTPエラーが発生した場合例外をスロー
    media_response = response.json()

    # --------    
    # for文で取得
    # --------    
    next_url = media_response["paging"]["next"]
    while True:
        response = requests.get(next_url, params=params)
        media_response = response.json()

        # for分で一つずつ辞書型にする
        for i, post in enumerate(media_response['data'], start=1):
            post_data = {}
            post_data["id"] = post["id"]
            post_data["link"] = post['permalink']
            post_data["caption"] = post.get('caption', 'なし')
            post_data["comments_count"] = post["comments_count"]
            post_data["like_count"] = post["like_count"]

            # timestampは、JSTのYYYY-MM-DD HH:MMに変換する
            timestamp_str = post["timestamp"]
            post_data["timestamp_jst"] = convert_timestamp_to_jst_formatted(timestamp_str)

            results.append(post_data)

        try:
            next_url = media_response["paging"]["next"]
        except:
            break

        # num_iterations回を超えたらやめる
        cnt += 1
        if cnt > num_iterations:
            break

    # データフレームに変換する
    results_df = pd.DataFrame(results)

    return results_df