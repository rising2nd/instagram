#%%
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib_fontja  # matplotlibで日本語を表示する
import os
import sys
from datetime import datetime

# --- パス設定 (notebooksフォルダ内からの実行に対応) ---
try:
    # スクリプト(.py)として実行する場合
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Jupyter NotebookやInteractive Windowで実行する場合
    current_dir = os.getcwd()

# プロジェクトルート (INSTAGRAMフォルダ) を取得
project_root = os.path.dirname(current_dir)

# ルートディレクトリをパスに追加
if project_root not in sys.path:
    sys.path.append(project_root)

# srcからのインポート（必要に応じて）
try:
    from src.config import DESTINATION_FOLDER_PATH
except ImportError:
    DESTINATION_FOLDER_PATH = None

def plot_like_count_over_time(df: pd.DataFrame, start_date_str: str, like_threshold: int, caption_length: int, timestamp_column: str, like_column: str, caption_column: str):
    """いいね数の時系列推移を可視化し、指定いいね数以上の投稿にキャプションを表示します。"""
    df[timestamp_column] = pd.to_datetime(df[timestamp_column])
    start_date = pd.to_datetime(start_date_str)
    filtered_df = df[df[timestamp_column] >= start_date].copy()

    # グラフの設定
    plt.rcParams['font.size'] = 14
    plt.rcParams['axes.labelsize'] = 16
    plt.rcParams['xtick.labelsize'] = 16
    plt.rcParams['ytick.labelsize'] = 16

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(filtered_df[timestamp_column], filtered_df[like_column], marker='o', markersize=4)
    ax.set_xlabel('投稿日')
    ax.set_ylabel('いいね数')
    ax.set_title('いいね数の時系列推移')
    ax.grid(True)

    # 文字の位置が重ならないように制御
    previous_x_offset = -10
    previous_y_offset = 0
    
    threshold_posts = filtered_df[filtered_df[like_column] >= like_threshold]
    
    for index, row in threshold_posts.iterrows():
        caption_text_raw = str(row.get(caption_column, 'なし'))
        caption_text = caption_text_raw.replace('\n', '')[:caption_length] + '...'

        current_x_offset = previous_x_offset + 5
        current_y_offset = previous_y_offset - 5        

        ax.annotate(caption_text,
                     (row[timestamp_column], row[like_column]),
                     textcoords="offset points",
                     xytext=(current_x_offset, current_y_offset),
                     ha='center',
                     fontsize=10,
                     arrowprops=dict(facecolor='black', shrink=0.05, width=0.5, headwidth=5, alpha=0.3))

        previous_x_offset = current_x_offset
        previous_y_offset = current_y_offset       

    fig.tight_layout()
    return fig

def main():
    # プロジェクトルートからの相対パスでCSVを指定
    file_path = os.path.join(project_root, 'data/output/results_master.csv')

    # 1. CSV読み込み
    try:
        results_df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: {file_path} が見つかりませんでした。")
        return

    # 2. 重複削除
    if 'id' in results_df.columns:
        initial_len = len(results_df)
        results_df = results_df.drop_duplicates(subset=['id'])
        if initial_len != len(results_df):
            print(f"重複を削除しました: {initial_len} -> {len(results_df)}")

    # 3. データチェック
    if results_df.empty:
        print("No data in CSV.")
        return

    # 4. 可視化の実行
    fig = plot_like_count_over_time(
        df=results_df,
        start_date_str='2023-02-10',
        like_threshold=21,
        caption_length=10,
        timestamp_column='timestamp_jst',
        like_column='like_count',
        caption_column='caption'
    )

    # 5. 画像をoutputフォルダに保存
    output_dir = os.path.dirname(file_path)
    today_str = datetime.now().strftime('%Y%m%d')
    save_dir = os.path.join(output_dir, today_str) # フォルダまでのパス
    save_path = os.path.join(save_dir, "visualize_like_cnt.png") # ファイルまでのパス
    
    # 【重要】フォルダが存在しない場合は作成する
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"ディレクトリを作成しました: {save_dir}")
    
    # 画像として保存
    fig.savefig(save_path, dpi=300)
    print(f"グラフを保存しました: {save_path}")

    plt.show()

if __name__ == '__main__':
    main()
# %%
