import matplotlib.pyplot as plt

# 使用之前 industry_stats 的汇总数据
industry_bubble = industry_stats.copy()
industry_bubble['avg_wealth'] = industry_bubble['total_wealth'] / industry_bubble['count']

# 只取人数较多的行业（可设置阈值）
industry_bubble_filtered = industry_bubble[industry_bubble['count'] >= 5]

plt.figure(figsize=(12, 8))
scatter = plt.scatter(
    industry_bubble_filtered['count'],
    industry_bubble_filtered['total_wealth'],
    s=industry_bubble_filtered['avg_wealth']*0.5,  # 调整气泡大小系数
    alpha=0.7,
    c=industry_bubble_filtered['avg_wealth'],
    cmap='viridis',
    edgecolors='k'
)

for i, row in industry_bubble_filtered.iterrows():
    plt.text(row['count'] + 0.5, row['total_wealth'], row['industry_cn'], fontsize=9)

plt.title('各行业富豪人数与总财富分布（气泡图）', fontsize=16)
plt.xlabel('富豪人数', fontsize=12)
plt.ylabel('总财富（亿元）', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
cbar = plt.colorbar(scatter)
cbar.set_label('人均财富（亿元）')

plt.tight_layout()
plt.savefig(output_dir / '6_行业人数_vs_财富气泡图.png', bbox_inches='tight')
plt.close()
print("图表已生成：6_行业人数_vs_财富气泡图.png")
