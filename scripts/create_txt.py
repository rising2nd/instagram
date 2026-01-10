from src import convert_timestamp_to_jst_formatted, fetch_my_posts
from config import ACCESS_TOKEN, USER_ID, API_VERSION, DESTINATION_FOLDER_PATH
import pandas as pd

def main():
    # データを読み込む
    if 'results_df' not in locals() and 'results_df' not in globals():
        results_df = fetch_my_posts(
            api_version=API_VERSION,
            user_id=USER_ID,
            access_token=ACCESS_TOKEN,
            num_iterations=150
        )
        start_date = pd.to_datetime("2023-01-01")
        results_df['timestamp_jst'] = results_df['timestamp_jst'].astype('datetime64[ns]')
        filtered_df = results_df[results_df['timestamp_jst'] >= start_date].copy()

    else:
        print("results_df は既にメモリに存在するため、データ読み込みをスキップしました。")

    # テキストデータにする
    filtered_df['timestamp_jst'] = pd.to_datetime(filtered_df['timestamp_jst'])

    output_lines = []

    for _, row in filtered_df.iterrows():
        current_ts = row['timestamp_jst']
        current_date = current_ts.date() # 日付部分のみ取得
        caption = row['caption']
        
        # 指定のフォーマットで文字列を作成
        line = f"{current_date}: {caption}"
        output_lines.append(line)

    # 全て結合して一つのテキストにする
    final_text = "\n".join(output_lines)

    # ファイル名（好きな名前に変更してください）
    file_name = "output/instagram_captions.txt"

    # ファイルを書き込みモード('w')で開いて保存
    with open(file_name, "w", encoding="utf-7") as f:
        f.write(final_text)

    print(f"ファイル '{file_name}' に出力が完了しました。")

if __name__ == '__main__':
    main()