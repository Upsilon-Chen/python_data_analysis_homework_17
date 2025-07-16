import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import matplotlib.ticker as ticker

plt.rcParams['figure.dpi'] = 100
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

def load_data():
    df = pd.read_csv('dlt_data.csv')
    df['开奖日期'] = pd.to_datetime(df['开奖日期'])
    df['星期'] = df['开奖日期'].dt.day_name()
    week_map = {'Monday': '星期一', 'Wednesday': '星期三', 'Saturday': '星期六'}
    df['星期'] = df['星期'].map(week_map)
    df = df.dropna(subset=['星期'])
    df['星期'] = pd.Categorical(df['星期'], categories=['星期一', '星期三', '星期六'], ordered=True)
    df['前区号码列表'] = df['前区号码'].apply(lambda x: list(map(int, x.split())))
    df['后区号码列表'] = df['后区号码'].apply(lambda x: list(map(int, x.split())))
    return df

def analyze_sales(df):
    plt.figure(figsize=(12, 6))
    sales_group = df.groupby('星期', observed=True)['总销售额(元)']
    sales_stats = sales_group.agg(['sum', 'mean', 'std', 'count']).reset_index()
    sales_stats.columns = ['星期', '总销售额', '平均销售额', '标准差', '期数']

    # 单位转换（亿元）
    for col in ['总销售额', '平均销售额', '标准差']:
        sales_stats[col] = sales_stats[col] / 1e8

    # 绘制销售额箱线图
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='星期', y='总销售额(元)', data=df)
    plt.title('不同开奖日的销售额分布', fontsize=14)
    plt.ylabel('销售额(元)', fontsize=12)
    plt.xlabel('开奖日', fontsize=12)
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x / 1e6:.1f}万'))
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

    # 绘制平均销售额条形图
    plt.figure(figsize=(12, 6))
    sns.barplot(x='星期', y='平均销售额', data=sales_stats, hue='星期', palette='Set2', legend=False)
    plt.title('不同开奖日的平均销售额（单位：亿元）', fontsize=14)
    plt.ylabel('平均销售额', fontsize=12)
    plt.xlabel('开奖日', fontsize=12)
    # 添加数据标签（直观展示统计量）
    for i, v in enumerate(sales_stats['平均销售额']):
        plt.text(i, v + 0.05, f'{v:.2f}亿', ha='center')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()

    # 销售额差异检验
    groups = [df[df['星期'] == day]['总销售额(元)'] for day in ['星期一', '星期三', '星期六']]
    stat, p = stats.kruskal(*groups)  # 非正态数据使用Kruskal-Wallis检验
    print(f"销售额差异检验（Kruskal-Wallis）：统计量={stat:.4f}, p值={p:.4f}")
    print("结论：" + ("存在显著差异" if p < 0.05 else "不存在显著差异"))

    return sales_stats

def analyze_numbers(df):
    front_freq = pd.DataFrame(0, index=range(1, 36), columns=['星期一', '星期三', '星期六'])
    back_freq = pd.DataFrame(0, index=range(1, 13), columns=['星期一', '星期三', '星期六'])

    for _, row in df.iterrows():
        week = row['星期']
        for num in row['前区号码列表']:
            front_freq.loc[num, week] += 1
        for num in row['后区号码列表']:
            back_freq.loc[num, week] += 1

    # 前区号码频数热力图（可视化频数分布）
    plt.figure(figsize=(12, 6))
    sns.heatmap(front_freq, annot=True, fmt='d', cmap='YlOrRd', cbar_kws={'label': '出现次数'})
    plt.title('前区号码在不同开奖日的出现次数', fontsize=14)
    plt.xlabel('开奖日', fontsize=12)
    plt.ylabel('号码', fontsize=12)
    plt.tight_layout()
    plt.show()

    # 后区号码频数热力图
    plt.figure(figsize=(12, 6))
    sns.heatmap(back_freq, annot=True, fmt='d', cmap='YlGnBu', cbar_kws={'label': '出现次数'})
    plt.title('后区号码在不同开奖日的出现次数', fontsize=14)
    plt.xlabel('开奖日', fontsize=12)
    plt.ylabel('号码', fontsize=12)
    plt.tight_layout()
    plt.show()

    # 前区高频号码分布（Top10）
    front_top10 = front_freq.sum(axis=1).sort_values(ascending=False).head(10).index
    plt.figure(figsize=(12, 6))
    front_freq.loc[front_top10].plot(kind='bar')
    plt.title('前10高频前区号码在不同开奖日的分布', fontsize=14)
    plt.xlabel('号码', fontsize=12)
    plt.ylabel('出现次数', fontsize=12)
    plt.legend(title='开奖日')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()

    # 号码分布独立性检验
    def chi2_test(observed, name):
        chi2, p, dof, expected = stats.chi2_contingency(observed)
        print(f"\n{name}号码独立性检验（卡方检验）：")
        print(f"卡方统计量={chi2:.4f}, p值={p:.4f}, 自由度={dof}")
        print("结论：" + ("与开奖日相关（存在显著差异）" if p < 0.05 else "与开奖日独立（无显著差异）"))

    chi2_test(front_freq.values, "前区")
    chi2_test(back_freq.values, "后区")

    return front_freq, back_freq

df = load_data()
print("数据基本信息：")
print(f"总样本量（有效开奖期数）：{len(df)}")
print(f"日期范围：{df['开奖日期'].min()} 至 {df['开奖日期'].max()}")
print(f"各开奖日样本量：{df['星期'].value_counts().to_dict()}\n")

sales_stats = analyze_sales(df)
front_freq, back_freq = analyze_numbers(df)

# 综合结论
print("\n===== 综合分析结论 =====")
print(
    f"1. 销售额特征：{['无显著差异' if stats.kruskal(*[df[df['星期'] == d]['总销售额(元)'] for d in ['星期一', '星期三', '星期六']])[1] >= 0.05 else '存在显著差异'][0]}，"
    f"平均销售额最高为{sales_stats.loc[sales_stats['平均销售额'].idxmax()]['星期']}")
print(
    f"2. 前区号码分布：{['与日期独立' if stats.chi2_contingency(front_freq.values)[1] >= 0.05 else '与日期相关'][0]}")
print(
    f"3. 后区号码分布：{['与日期独立' if stats.chi2_contingency(back_freq.values)[1] >= 0.05 else '与日期相关'][0]}")

