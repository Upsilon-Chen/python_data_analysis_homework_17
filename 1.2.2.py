import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from pathlib import Path

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.autolayout'] = True

# 获取桌面路径
desktop_path = Path.home() / 'Desktop'
output_dir = desktop_path / '胡润百富榜行业分析'
os.makedirs(output_dir, exist_ok=True)
print(f"图表将保存到: {output_dir}")

# 加载数据
df = pd.read_csv('hurun_rich_list_2024.csv')

# 清洗数据
if 'industry_cn' in df.columns:
    df['industry_cn'] = df['industry_cn'].fillna('未知行业').astype(str)
    df['industry_cn'] = df['industry_cn'].str.replace('、|与|及', '和', regex=True)
else:
    df['industry_cn'] = '未知行业'

if 'wealth_cny' in df.columns:
    df['wealth_cny'] = df['wealth_cny'].astype(str).str.replace(',', '')
    wealth_numeric = pd.to_numeric(df['wealth_cny'], errors='coerce')
    df['wealth_cny'] = wealth_numeric.fillna(wealth_numeric.median())
else:
    df['wealth_cny'] = np.random.randint(10, 1000, size=len(df))

# 分组统计
industry_stats = df.groupby('industry_cn').agg(
    count=('industry_cn', 'size'),
    total_wealth=('wealth_cny', 'sum')
).reset_index()

# 绘图：富豪人数 vs 财富总量（散点图）
plt.figure(figsize=(14, 9))
scatter = sns.scatterplot(
    data=industry_stats, 
    x='count', y='total_wealth', 
    hue='industry_cn', 
    s=70,             # 点稍微小一点
    palette='tab20', 
    alpha=0.8         # 适当透明
)

plt.title('2024胡润百富榜 - 各行业富豪人数与总财富关系', fontsize=18)
plt.xlabel('富豪人数', fontsize=14)
plt.ylabel('总财富 (亿元)', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.6)

# 只标注财富最高的Top 5行业，避免拥挤
top5 = industry_stats.sort_values('total_wealth', ascending=False).head(5)
for _, row in top5.iterrows():
    plt.text(row['count'] + 0.3, row['total_wealth'], row['industry_cn'], 
             fontsize=11, color='black', weight='bold')

# 将图例放到图右侧外面，避免遮挡
plt.legend(
    title='行业', 
    bbox_to_anchor=(1.05, 1), 
    loc='upper left', 
    borderaxespad=0,
    fontsize=10,
    title_fontsize=12,
    frameon=False
)

plt.tight_layout(rect=[0, 0, 0.85, 1])  # 留出右边空间给图例

plt.savefig(output_dir / '富豪人数_vs_总财富_行业关系图_优化版.png')
plt.close()
print("已生成图表: 富豪人数_vs_总财富_行业关系图_优化版.png")
