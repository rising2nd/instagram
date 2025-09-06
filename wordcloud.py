#%%
# インスタのキャプションからワードクラウドを作成する
# 参考: https://qiita.com/Mikeinu/items/dd5e9af26fd3a5f3c8e0

from src import convert_timestamp_to_jst_formatted, fetch_my_posts
from config import ACCESS_TOKEN, USER_ID, API_VERSION, DESTINATION_FOLDER_PATH

from janome.tokenizer import Tokenizer
import unicodedata
import MeCab
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re


def filter_df(
    df: pd.DataFrame,
    start_date_str: str,
    end_date_str: str,
) -> pd.DataFrame:
    # 日付でフィルタリング
    start_date = pd.to_datetime(start_date_str)
    end_date = pd.to_datetime(end_date_str)

    filtered_df_tmp = df[df['timestamp_jst'] >= start_date].copy()
    filtered_df = filtered_df_tmp[filtered_df_tmp['timestamp_jst'] <= end_date].copy()
    filtered_df.reset_index(drop=True, inplace=True)
    return filtered_df


def clean_text(text: str) -> str:
    # re.subで正規表現を使った文字列の削除
    text = re.sub('\u3000', '', text)
    text = re.sub('・', '', text)
    text = re.sub('「', '', text)
    text = re.sub('」', '', text)
    text = re.sub('（', '', text)
    text = re.sub('）', '', text)
    
    # re.subで正規表現を使った文字列の半角空白への置換
    text = re.sub('\n', ' ', text)
    text = re.sub('\\n', '', text)
    text = re.sub('\\n', ' ', text)
    return text


def tokenized_text(text: str) -> list:

    # ユニコード正規化
    normalized_text = unicodedata.normalize('NFKC', text)
    t = Tokenizer()
    tokenized_text = t.tokenize(normalized_text)

    words_list=[]
    #tokenizeされたテキストをfor文を使ってhinshiとhinshi2に格納する。
    for token in tokenized_text:
        tokenized_word = token.surface
        hinshi = token.part_of_speech.split(',')[0]
        hinshi2 = token.part_of_speech.split(',')[1]
        #抜き出す品詞を指定する
        if hinshi == "名詞":
            if (hinshi2 != "数") and (hinshi2 != "代名詞") and (hinshi2 != "非自立"):
                words_list.append(tokenized_word)

    words_wakachi = " ".join(words_list)

    return words_wakachi


def generate_wordcloud(words_wakachi: str, stop_words):
    # 日本語フォントのパスを指定
    font_path = 'NotoSansJP-VariableFont_wght.ttf'  # 適宜変更してください

    # WordCloudを表示
    word_cloud = WordCloud(font_path = font_path,
                           width=1500,
                           height=900,
                           stopwords=set(stop_words),
                           min_font_size=5,
                           collocations=False,
                           background_color='white',
                           max_words=400).generate(words_wakachi)

    figure = plt.figure(figsize=(15,10))
    plt.imshow(word_cloud)
    plt.tick_params(labelbottom=False, labelleft=False)
    plt.xticks([])
    plt.yticks([])
    plt.show()

#%%
# データを読み込む
if 'results_df' not in locals() and 'results_df' not in globals():
    results_df = fetch_my_posts(
        api_version=API_VERSION,
        user_id=USER_ID,
        access_token=ACCESS_TOKEN,
        num_iterations=150
    )
else:
    print("results_df は既にメモリに存在するため、データ読み込みをスキップしました。")

# dfを日付でフィルタリング
start_date_str = "2024-01-01"
end_date_str = "2024-12-31"

filtered_df = filter_df(
    df=results_df,
    start_date_str=start_date_str,
    end_date_str=end_date_str,
)

# caption列を結合
whole_words = ''.join(filtered_df['caption'].astype(str))

# テキストの前処理と形態素解析
cleaned_text = clean_text(whole_words)
words_wakachi = tokenized_text(cleaned_text)

# 除外するワードを設定  適宜変更してください
stop_words = ['こと', 'よう', 'それ', 'もの', 'さん', 'ため', 'ところ', 'これ',
              '私', '今日', '明日', '昨日', '時', '日','年', '月', '週', '分',
              '様', '自分', '皆', '人', '目', 'あと', '笑', '泣', '話']
# ワードクラウドの生成と表示
generate_wordcloud(words_wakachi, stop_words)
# %%
