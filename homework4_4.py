import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression

plt.rcParams['figure.dpi'] = 100
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 1. 数据读取与预处理
data = pd.read_csv('zj_data.csv')

# 2. 数据清洗
core_cols = ['彩龄', '文章数量', '粉丝数', '双色球一等奖', '双色球二等奖', '双色球三等奖',
             '大乐透一等奖', '大乐透二等奖', '大乐透三等奖']
data = data[core_cols].dropna()

# 3. 计算衍生指标
data['双色球总中奖'] = data['双色球一等奖'] + data['双色球二等奖'] + data['双色球三等奖']
data['大乐透总中奖'] = data['大乐透一等奖'] + data['大乐透二等奖'] + data['大乐透三等奖']
data['总中奖次数'] = data['双色球总中奖'] + data['大乐透总中奖']

# 4. 基本属性分布分析
plt.figure(figsize=(18, 5))
plt.subplot(131)
sns.histplot(data['彩龄'], bins=8, kde=True, color='#FF6B6B')
plt.title('专家彩龄分布')
plt.xlabel('彩龄（年）')
plt.ylabel('频数')

plt.subplot(132)
sns.histplot(data['文章数量'], bins=8, kde=True, color='#4ECDC4')
plt.title('专家文章数量分布')
plt.xlabel('文章数量')
plt.ylabel('频数')

plt.subplot(133)
sns.histplot(data['粉丝数'], bins=8, kde=True, color='#45B7D1')
plt.title('专家粉丝数分布')
plt.xlabel('粉丝数')
plt.ylabel('频数')
plt.tight_layout()
plt.show()

# 5. 中奖情况分布
plt.figure(figsize=(18, 5))
plt.subplot(131)
sns.histplot(data['双色球总中奖'], bins=8, kde=True, color='#FFA07A')
plt.title('双色球总中奖次数分布')
plt.xlabel('中奖次数')
plt.ylabel('频数')

plt.subplot(132)
sns.histplot(data['大乐透总中奖'], bins=8, kde=True, color='#98D8C8')
plt.title('大乐透总中奖次数分布')
plt.xlabel('中奖次数')
plt.ylabel('频数')

plt.subplot(133)
sns.histplot(data['总中奖次数'], bins=8, kde=True, color='#F7DC6F')
plt.title('总中奖次数分布')
plt.xlabel('中奖次数')
plt.ylabel('频数')
plt.tight_layout()
plt.show()

# 6. 相关性分析
plt.figure(figsize=(10, 8))
corr_data = data[['彩龄', '文章数量', '粉丝数', '双色球总中奖', '大乐透总中奖', '总中奖次数']]
corr_matrix = corr_data.corr()
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm',
            square=True, linewidths=.5, fmt='.2f')
plt.title('属性与中奖情况相关性热力图')
plt.tight_layout()
plt.show()

# 7. 相关性显著性检验
print("\n=== 相关性显著性检验 ===")
for col in ['彩龄', '文章数量', '粉丝数']:
    corr, p_value = stats.pearsonr(data[col], data['总中奖次数'])
    significance = "显著相关" if p_value < 0.05 else "不显著相关"
    print(f"{col}与总中奖次数: 相关系数={corr:.3f}, p值={p_value:.4f}, 结论={significance}")

# 8. 回归模型显著性检验
print("\n=== 回归模型显著性检验 ===")
X = data[['彩龄', '文章数量', '粉丝数']]
y = data['总中奖次数']
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)

ss_total = np.sum((y - np.mean(y)) **2)
ss_reg = np.sum((y_pred - np.mean(y))** 2)
ss_res = np.sum((y - y_pred) **2)
m, n = X.shape[1], len(y)

# F检验（模型整体显著性）
f_stat = (ss_reg/m) / (ss_res/(n-m-1))
f_pvalue = 1 - stats.f.cdf(f_stat, m, n-m-1)
f_significance = "模型整体显著" if f_pvalue < 0.05 else "不显著"
print(f"F统计量={f_stat:.3f}, p值={f_pvalue:.4f}, 结论={f_significance}")

# 回归系数t检验
print("\n各变量回归系数显著性:")
for i, col in enumerate(['彩龄', '文章数量', '粉丝数']):
    se = np.sqrt(ss_res/(n-m-1)) / np.sqrt(np.sum((X[col]-np.mean(X[col]))** 2))
    t_stat = abs(model.coef_[i])/se
    t_pvalue = 2*(1 - stats.t.cdf(t_stat, n-m-1))
    t_significance = "显著" if t_pvalue < 0.05 else "不显著"
    print(f"{col}: 系数={model.coef_[i]:.3f}, t值={t_stat:.3f}, p值={t_pvalue:.4f}")

# 9. 方差分析
print("\n=== 方差分析 ===")
data['彩龄分组'] = pd.cut(data['彩龄'], bins=[0,5,15,np.inf], labels=['低','中','高'])
f_val, p_val = stats.f_oneway(
    data[data['彩龄分组']=='低']['总中奖次数'],
    data[data['彩龄分组']=='中']['总中奖次数'],
    data[data['彩龄分组']=='高']['总中奖次数']
)
anova_significance = "组间差异显著" if p_val < 0.05 else "不显著"
print(f"彩龄分组方差分析: F={f_val:.3f}, p值={p_val:.4f}, 结论={anova_significance}")

# 10. 层次分析法权重计算
print("\n=== 层次分析法权重 ===")
# 提取相关系数
corr_array = np.array([corr_matrix.loc[col, '总中奖次数'] for col in ['彩龄', '文章数量', '粉丝数']])
weights = np.abs(corr_array)  # 基于相关系数绝对值的权重
weights = weights / np.sum(weights)  # 归一化

for i, col in enumerate(['彩龄', '文章数量', '粉丝数']):
    print(f"{col}权重: {weights[i]:.3f}")

# 权重排序（修正索引访问）
sorted_indices = np.argsort(weights)[::-1]  # 降序排序
sorted_cols = [['彩龄', '文章数量', '粉丝数'][i] for i in sorted_indices]
print(f"权重排序: {sorted_cols[0]} > {sorted_cols[1]} > {sorted_cols[2]}")

# 11. 插值趋势分析
plt.figure(figsize=(10, 6))
x_interp = np.linspace(data['彩龄'].min(), data['彩龄'].max(), 100)
y_interp = np.interp(x_interp, sorted(data['彩龄']), sorted(data['总中奖次数']))
plt.scatter(data['彩龄'], data['总中奖次数'], label='原始数据', alpha=0.7)
plt.plot(x_interp, y_interp, 'r--', label='线性插值趋势')
plt.title('彩龄与总中奖次数插值趋势')
plt.xlabel('彩龄（年）')
plt.ylabel('总中奖次数')
plt.legend()
plt.tight_layout()
plt.show()

# 12. 关键属性与中奖次数关系
plt.figure(figsize=(18, 5))
plt.subplot(131)
sns.scatterplot(x='彩龄', y='总中奖次数', data=data, alpha=0.7)
sns.regplot(x='彩龄', y='总中奖次数', data=data, scatter=False, color='red')
plt.title('彩龄与总中奖次数的关系')

plt.subplot(132)
sns.scatterplot(x='文章数量', y='总中奖次数', data=data, alpha=0.7)
sns.regplot(x='文章数量', y='总中奖次数', data=data, scatter=False, color='red')
plt.title('文章数量与总中奖次数的关系')

plt.subplot(133)
sns.scatterplot(x='粉丝数', y='总中奖次数', data=data, alpha=0.7)
sns.regplot(x='粉丝数', y='总中奖次数', data=data, scatter=False, color='red')
plt.title('粉丝数与总中奖次数的关系')
plt.tight_layout()
plt.show()

# 13. 统计描述输出
print("\n=== 基本属性统计描述 ===")
print(data[['彩龄', '文章数量', '粉丝数']].describe())
print("\n=== 中奖情况统计描述 ===")
print(data[['双色球总中奖', '大乐透总中奖', '总中奖次数']].describe())