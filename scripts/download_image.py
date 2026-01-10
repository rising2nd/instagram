import pandas as pd
import matplotlib.pyplot as plt
import matplotlib_fontja  # matplotlibで日本語を表示する
from config import ACCESS_TOKEN, USER_ID, API_VERSION, DESTINATION_FOLDER_PATH
from src import convert_timestamp_to_jst_formatted, fetch_my_posts
import requests

def filter_df(
    search_term: str,
    df: pd.DataFrame
) -> pd.DataFrame:

    filtered_df = df[df['caption'].str.contains(search_term, na=False)]

    if len(filtered_df) != 1:
        print("該当の投稿が1件ではありません")
        return
    else:
        result_dict = filtered_df.to_dict(orient='records')[0]
        return result_dict

# イメージ取得用URLを作成
def make_img_url(
    permalink: str
) -> str:
    img_link = f"{permalink}media/?size=l"
    headers = {"User-Agent": ""}
    img_url = requests.get(img_link, headers=headers).url

    return img_url

# 画像をダウンロードする
def get_img(
    img_url: str,
    result_dict: dict,
    destination_folder_path: str = "/Users/st/workspace/instagram/imgs/"
) -> None:

    timestamp_jst = result_dict["timestamp_jst"]
    id = result_dict["id"]

    file_name = f"{destination_folder_path}/{timestamp_jst}_{id}.jpg"
    response = requests.get(img_url)
    image = response.content
    with open(file_name, "wb") as f:
        f.write(image)

def download_img(
    api_version: str,
    user_id: str,
    access_token: str,
    num_iterations: str,
    serch_term: str,
    destination_folder_path: str
) -> None:

    # データを読み込む
    results_df = fetch_my_posts(
        api_version=api_version,
        user_id=user_id,
        access_token=access_token,
        num_iterations=num_iterations
    )

    # serch_termのデータを抽出する
    result_dict = filter_df(
        search_term=serch_term,
        df = results_df
    )

    # 画像のURLを取得する
    img_url = make_img_url(result_dict["link"])

    # 画像を指定したフォルダにダウンロードする
    get_img(
        img_url=img_url,
        result_dict=result_dict,
        destination_folder_path=destination_folder_path
    )

if __name__ == '__main__':

    serch_term = "ネイティブキャンプ"

    download_img(
        api_version = API_VERSION,
        user_id = USER_ID,
        access_token = ACCESS_TOKEN,
        num_iterations = 100,
        serch_term = serch_term,
        destination_folder_path = DESTINATION_FOLDER_PATH
    )