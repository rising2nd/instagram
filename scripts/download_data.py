#%%
import os
import sys
import pandas as pd

# --- パス設定 ---
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    current_dir = os.getcwd()

project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.src import convert_timestamp_to_jst_formatted, fetch_my_posts
from src.config import ACCESS_TOKEN, USER_ID, API_VERSION

def update_instagram_logs(csv_path, txt_path):
    """
    指定されたCSVとTXTファイルを最新データで書き換える関数
    """
    # 1. データの取得
    # ノートブック環境等での再実行を考慮し、グローバル変数をチェック
    if 'results_df' not in globals():
        print("APIからデータを取得中...")
        results_df = fetch_my_posts(
            api_version=API_VERSION,
            user_id=USER_ID,
            access_token=ACCESS_TOKEN,
            num_iterations=150
        )
    else:
        print("メモリ上の results_df を使用します。")
        results_df = globals()['results_df']

    # 2. データ加工（日付フィルタとソート）
    results_df['timestamp_jst'] = pd.to_datetime(results_df['timestamp_jst'])
    start_date = pd.to_datetime("2023-01-01")
    filtered_df = results_df[results_df['timestamp_jst'] >= start_date].copy()
    
    # 日付順に並び替え
    filtered_df = filtered_df.sort_values('timestamp_jst')

    # 3. CSVの書き換え（上書き）
    filtered_df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    # 4. TXTの書き換え（上書き）
    output_lines = []
    last_date = None

    for _, row in filtered_df.iterrows():
        current_date = row['timestamp_jst'].date()
        caption = str(row['caption']).replace('\n', ' ')
        
        # 日付が変わるタイミングで空行を挿入
        if last_date is not None and current_date != last_date:
            output_lines.append("")
        
        output_lines.append(f"{current_date}: {caption}")
        last_date = current_date

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"--- 更新完了 ---")
    print(f"CSV: {csv_path}")
    print(f"TXT: {txt_path}")
    print(f"合計: {len(filtered_df)} 件のデータを保存しました。")

if __name__ == '__main__':
    # 引数としてパスを指定
    target_csv = "/Users/st/workspace/instagram/data/output/results_master.csv"
    target_txt = "/Users/st/workspace/instagram/data/output/instagram_captions.txt"
    
    update_instagram_logs(target_csv, target_txt)
# %%
