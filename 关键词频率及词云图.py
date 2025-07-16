import pandas as pd
import nltk
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import string

# 下载英文停用词
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

#分词模型
nltk.download('punkt')

# 加载数据
df = pd.read_csv('dblp_conference_papers.csv')

# 设置停用词和标点
stop_words = set(stopwords.words('english'))
punctuation = set(string.punctuation)

# 清洗 & 分词函数
def clean_and_tokenize(title):
    words = word_tokenize(title.lower())
    words = [w for w in words if w not in stop_words and w not in punctuation and w.isalpha()]
    return words

# 为每年统计关键词
df['tokens'] = df['title'].apply(clean_and_tokenize)

# 统计所有年份的总关键词频率
all_tokens = [token for tokens in df['tokens'] for token in tokens]
token_counts = Counter(all_tokens)

# 显示前20个高频关键词
print("Top 20 keywords:")
print(token_counts.most_common(20))


 # 生成词云图
wc = WordCloud(width=1000, height=600, background_color='white',
               max_words=100, colormap='viridis').generate_from_frequencies(token_counts)

# 显示词云图
plt.figure(figsize=(12, 6))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.title("Word cloud of frequently studied keywords from 2020 to present", fontsize=16)
plt.show()

# 按年份聚合关键
year_keyword_freq = {}
for year in sorted(df['year'].unique()):
    year_tokens = [token for tokens in df[df['year'] == year]['tokens'] for token in tokens]
    year_counter = Counter(year_tokens)
    year_keyword_freq[year] = year_counter
# 选出Top关键词（如在全部年份出现频率前20）
top_keywords = [kw for kw, _ in token_counts.most_common(20)]
# 构建DataFrame
keyword_trend_df = pd.DataFrame(index=top_keywords)
for year, counter in year_keyword_freq.items():
    year_data = {kw: counter.get(kw, 0) for kw in top_keywords}
    keyword_trend_df[year] = pd.Series(year_data)
keyword_trend_df = keyword_trend_df.fillna(0)
# 计算关键词总出现频次（所有年份总和）
total_freq = keyword_trend_df.sum(axis=1)
# 取出排名前10的关键词
top10_keywords = total_freq.sort_values(ascending=False).head(10).index
# 绘图
plt.figure(figsize=(14, 8))
for kw in top10_keywords:
    plt.plot(
        keyword_trend_df.columns,          # 年份
        keyword_trend_df.loc[kw],          # 该关键词各年频次
        marker='o',
        linewidth=2,
        label=kw
    )
plt.title("Top 10 High-Frequency Keyword Trends (2020 to Present)", fontsize=17, fontweight='bold')
plt.xlabel("Year", fontsize=14)
plt.ylabel("Frequency of Occurrence", fontsize=14)
plt.xticks(keyword_trend_df.columns, fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
# 美化图例
plt.legend(title="Keyword", fontsize=11, title_fontsize=12, ncol=2, loc='upper left', bbox_to_anchor=(1.02, 1))
plt.tight_layout()
plt.show()


