#%%
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib_fontja  # matplotlibで日本語を表示する
import os
from datetime import datetime

def plot_target_column_over_time(
    df: pd.DataFrame,
    target_column: str,
    title: str,
    is_annotate: bool = True,
    timestamp_column: str = "timestamp_jst",
    caption_column: str = "caption",
    threshold: int = None,
    visualize_caption_length: int = 10,
    start_date_str: str = "2023-02-10"
):
    """
    特定のカラムの時系列推移を可視化し、figオブジェクトを返します。
    """
    filtered_df = df.copy()
    filtered_df[timestamp_column] = pd.to_datetime(filtered_df[timestamp_column])
    start_date = pd.to_datetime(start_date_str)
    filtered_df = filtered_df[filtered_df[timestamp_column] >= start_date]

    if threshold is None:
        percentile_99 = filtered_df[target_column].quantile(0.99)
        threshold = percentile_99

    threshold_exceeded_df = pd.DataFrame(columns=[timestamp_column, caption_column])

    # グラフの設定
    plt.rcParams['font.size'] = 14
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(filtered_df[timestamp_column], filtered_df[target_column], color='orange', marker='o', markersize=4)
    ax.set_xlabel('投稿日')
    ax.set_ylabel(f'{title}')
    ax.set_title(f'{title}の時系列推移')
    ax.grid(True)

    # 閾値を超えたデータの抽出
    threshold_posts = filtered_df[filtered_df[target_column] >= threshold]
    for index, row in threshold_posts.iterrows():
        new_row = pd.DataFrame([{
            timestamp_column: row[timestamp_column].strftime('%Y-%m-%d %H:%M'),
            caption_column: str(row.get(caption_column, 'なし')),
            target_column: row[target_column]
        }])
        threshold_exceeded_df = pd.concat([threshold_exceeded_df, new_row], ignore_index=True)

    fig.tight_layout()
    
    if not threshold_exceeded_df.empty:
        threshold_exceeded_df = threshold_exceeded_df.sort_values(by=target_column, ascending=False).reset_index(drop=True)

    return fig, threshold_exceeded_df


def main(file_path: str):
    # 1. CSV読み込み
    try:
        results_df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: {file_path} が見つかりませんでした。")
        return

    # 2. 前処理
    if 'caption' in results_df.columns:
        results_df['caption_length'] = results_df["caption"].fillna("").apply(len)
    
    if results_df.empty:
        print("No data in CSV.")
        return

    # 3. 可視化実行
    fig, threshold_exceeded_df = plot_target_column_over_time(
        df=results_df,
        target_column='caption_length',
        title='文字数',
        is_annotate=False
    )

    # --- 4. 実行日の日付を入れてグラフ画像を保存する処理 ---
    output_dir = os.path.dirname(file_path)
    
    # 今日の日付を取得 (例: 20260111)
    today_str = datetime.now().strftime('%Y%m%d')
    
    # 保存先のフルパスを組み立てる
    save_dir = os.path.join(output_dir, today_str) # フォルダまでのパス
    save_path = os.path.join(save_dir, "visualize_caption_length.png") # ファイルまでのパス
    
    # 【重要】フォルダが存在しない場合は作成する
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"ディレクトリを作成しました: {save_dir}")
    
    # 画像として保存
    fig.savefig(save_path, dpi=300)
    print(f"グラフを保存しました: {save_path}")
    # -----------------------------------------------

    plt.show()

    # テーブルデータの表示
    threshold_exceeded_df = threshold_exceeded_df.rename(columns={
        "timestamp_jst": "投稿時間",
        "caption": "キャプション",
        "caption_length": "文字数"
    })
    # display(threshold_exceeded_df)

if __name__ == '__main__':
    CSV_PATH = '/Users/st/workspace/instagram/data/output/results_master.csv'
    main(CSV_PATH)
# %%
