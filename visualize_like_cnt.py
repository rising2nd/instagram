import os
import requests
import json
from tqdm import tqdm
import pandas as pd
import datetime
from dateutil.parser import isoparse
import matplotlib.pyplot as plt
import japanize_matplotlib
from config import ACCESS_TOKEN, USER_ID, API_VERSION
from src import convert_timestamp_to_jst_formatted


def fetch_instagram_media(api_version: str, user_id: str, access_token: str):
    """InstagramのメディアデータをAPIから取得します。"""
    graph_domain = 'https://graph.facebook.com/'
    endpoint_base = f"{graph_domain}{api_version}/"
    url = f"{endpoint_base}{user_id}/media"
    params = {
        'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username,comments_count,like_count',
        'access_token': access_token
    }
    results = []
    next_url = url
    cnt = 0

    while next_url:
        try:
            response = requests.get(next_url, params=params)
            response.raise_for_status()
            media_response = response.json()

            for post in media_response.get('data', []):
                post_data = {
                    "id": post["id"],
                    "link": post['permalink'],
                    "caption": post.get('caption', 'なし'),
                    "comments_count": post["comments_count"],
                    "like_count": post["like_count"],
                    "timestamp_jst": convert_timestamp_to_jst_formatted(post["timestamp"])
                }
                results.append(post_data)

            next_url = media_response['paging'].get('next')
            cnt += 1
            if cnt > 100 and next_url:  # 無限ループ対策
                print("Warning: Reached 100 pages, stopping data fetching.")
                break

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            break
        except KeyError:
            print("Error: 'paging' or 'data' key not found in response.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

    return pd.DataFrame(results)


def plot_like_count_over_time(df: pd.DataFrame, start_date_str: str, like_threshold: int, caption_length: int, timestamp_column: str, like_column: str, caption_column: str):
    """いいね数の時系列推移を可視化し、指定いいね数以上の投稿にキャプションを表示します。"""
    df[timestamp_column] = pd.to_datetime(df[timestamp_column])
    start_date = pd.to_datetime(start_date_str)
    filtered_df = df[df[timestamp_column] >= start_date].copy()

    plt.rcParams['font.size'] = 14       # 全体のフォントサイズ
    plt.rcParams['axes.labelsize'] = 16   # 軸ラベル
    plt.rcParams['xtick.labelsize'] = 16  # X軸目盛り
    plt.rcParams['ytick.labelsize'] = 16  # Y軸目盛り
    plt.rcParams['legend.fontsize'] = 16  # 凡例
    plt.rcParams['figure.titlesize'] = 12  # 図のタイトル

    plt.figure(figsize=(12, 6))
    plt.plot(filtered_df[timestamp_column], filtered_df[like_column])
    plt.xlabel('投稿日 (JST)')
    plt.ylabel('いいね数')
    plt.title(f'いいね数の時系列推移')
    plt.grid(True)

    # 文字の位置が重ならないように制御する
    previous_x_offset = -10
    previous_y_offset = 0
    for index, row in filtered_df[filtered_df[like_column] >= like_threshold].iterrows():
        caption_text_raw = str(row.get(caption_column, 'なし'))
        caption_text = caption_text_raw.replace('\n', '')[:caption_length] + '...'

        current_x_offset = previous_x_offset + 5
        current_y_offset = previous_y_offset - 5        

        plt.annotate(caption_text,
                     (row[timestamp_column], row[like_column]),
                     textcoords="offset points",
                     xytext=(current_x_offset, current_y_offset),
                     ha='center',
                     fontsize=10)

        previous_x_offset = current_x_offset
        previous_y_offset = current_y_offset       

    plt.tight_layout()
    plt.show()


def visualize_like_cnt(api_version: str, user_id: str, access_token: str):
    """いいね数の時系列推移を可視化するメイン関数。"""
    results_df = fetch_instagram_media(api_version, user_id, access_token)

    if not results_df.empty:
        plot_like_count_over_time(
            df=results_df,
            start_date_str='2023-02-10',
            like_threshold=20,
            caption_length=20,
            timestamp_column='timestamp_jst',
            like_column='like_count',
            caption_column='caption'
        )
    else:
        print("No media data fetched.")


if __name__ == '__main__':
    visualize_like_cnt(API_VERSION, USER_ID, ACCESS_TOKEN)