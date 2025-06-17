#%%
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib_fontja  # matplotlibで日本語を表示する
from config import ACCESS_TOKEN, USER_ID, API_VERSION
from src import convert_timestamp_to_jst_formatted, fetch_my_posts


def plot_target_column_over_time(
    df: pd.DataFrame,
    target_column: str,
    title: str,
    is_annotate: bool = True,
    timestamp_column: str = "timestamp_jst",
    caption_column: str = "caption",
    threshold: int = None,
    visualize_caption_length: int = 10,
    start_date_str: str = "2023-02-10"  # 毎日投稿を始めた日
):
    """
    特定のカラムの時系列推移を可視化し、しきい値以上の投稿にキャプションを表示します。
    """

    # start_date_str以降のみにする
    df[timestamp_column] = pd.to_datetime(df[timestamp_column])
    start_date = pd.to_datetime(start_date_str)
    filtered_df = df[df[timestamp_column] >= start_date].copy()

    # thesholdを求める
    if threshold is None:
        # 99パーセンタイルを取得
        percentile_99 = df[target_column].quantile(0.99)
        threshold = percentile_99

    # 閾値を超えた投稿を格納するDataFrame
    threshold_exceeded_df = pd.DataFrame(columns=[timestamp_column, caption_column])

    # グラフの設定
    plt.rcParams['font.size'] = 14       # 全体のフォントサイズ
    plt.rcParams['axes.labelsize'] = 16   # 軸ラベル
    plt.rcParams['xtick.labelsize'] = 16  # X軸目盛り
    plt.rcParams['ytick.labelsize'] = 16  # Y軸目盛り
    plt.rcParams['legend.fontsize'] = 16  # 凡例
    plt.rcParams['figure.titlesize'] = 12  # 図のタイトル

    fig, ax = plt.subplots(figsize=(12, 6)) # FigureとAxesオブジェクトを明示的に作成
    ax.plot(filtered_df[timestamp_column], filtered_df[target_column])
    ax.set_xlabel('投稿日')
    ax.set_ylabel(f'{title}')
    ax.set_title(f'{title}の時系列推移')
    ax.grid(True)


    # 文字の位置が重ならないように制御する
    previous_x_offset = -10
    previous_y_offset = 0

    # 閾値を超えたデータをフィルタリング
    threshold_posts = filtered_df[filtered_df[target_column] >= threshold]

    for index, row in threshold_posts.iterrows():
        # 閾値を超えたデータを新しいDataFrameに追加
        new_row = pd.DataFrame([{
            timestamp_column: row[timestamp_column].strftime('%Y-%m-%d %H:%M'), # 時刻も表示
            caption_column: str(row.get(caption_column, 'なし')),
            target_column: row[target_column]
        }])
        threshold_exceeded_df = pd.concat([threshold_exceeded_df, new_row], ignore_index=True)

        if is_annotate:
            caption_text_raw = str(row.get(caption_column, 'なし'))
            # キャプションの改行コードを削除し、指定された長さにカット
            caption_text = caption_text_raw.replace('\n', ' ')[:visualize_caption_length] + '...'

            current_x_offset = previous_x_offset + 5
            current_y_offset = previous_y_offset - 5        

            plt.annotate(caption_text,
                            (row[timestamp_column], row[target_column]),
                            textcoords="offset points",
                            xytext=(current_x_offset, current_y_offset),
                            ha='center',
                            fontsize=10,
                            arrowprops=dict(facecolor='black', shrink=0.05, width=0.5, headwidth=5, alpha=0.5))

            previous_x_offset = current_x_offset
            previous_y_offset = current_y_offset       

    fig.tight_layout() # figを使ってtight_layout

    # 閾値を超えた投稿のDataFrameを表で表示
    if not threshold_exceeded_df.empty:
        # target_columnの降順に並べる
        threshold_exceeded_df = threshold_exceeded_df.sort_values(by=target_column, ascending=False).reset_index(drop=True)

    return fig, threshold_exceeded_df


def main(
    api_version: str,
    user_id: str,
    access_token: str,
    num_iterations=100
):
    results_df = fetch_my_posts(
        api_version=api_version,
        user_id=user_id,
        access_token=access_token,
        num_iterations=num_iterations
    )

    results_df['caption_length'] = results_df["caption"].apply(len)

    if not results_df.empty:
        fig, threshold_exceeded_df = plot_target_column_over_time(
            df=results_df,
            target_column='caption_length',
            title='文字数',
            # visualize_caption_length = 5
            is_annotate = False
        )

        fig.show()

        threshold_exceeded_df = threshold_exceeded_df.rename(columns={
            "timestamp_jst": "投稿時間",
            "caption": "キャプション",
            "caption_length": "文字数"
            })

        display(threshold_exceeded_df)

    else:
        print("No media data fetched.")



if __name__ == '__main__':
    main(API_VERSION, USER_ID, ACCESS_TOKEN)