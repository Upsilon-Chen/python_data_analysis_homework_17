import pandas as pd
import matplotlib.pyplot as plt

# 读取上一步保存的 CSV 文件（或使用内存中的 all_papers 数据）
csv_file = 'dblp_conference_papers.csv'
df = pd.read_csv(csv_file)

# 统计每个会议每年的论文数量
paper_counts = df.groupby(['conference', 'year']).size().reset_index(name='paper_count')

# 打印汇总表格（可选）
print(paper_counts)

# 可视化：按会议分组绘制每年论文数量的变化曲线
plt.figure(figsize=(12, 6))
for conf in paper_counts['conference'].unique():
    conf_data = paper_counts[paper_counts['conference'] == conf]
    plt.plot(conf_data['year'], conf_data['paper_count'], marker='o', label=conf)

plt.title('The trend of the number of papers presented at each conference over the years (for 2020 and beyond)', fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Number', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(title='Conference name')
plt.tight_layout()
plt.xticks(paper_counts['year'].unique())  # 确保年份整齐显示
plt.show()
