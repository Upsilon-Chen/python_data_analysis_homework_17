import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import numpy as np
from scipy import stats

plt.rcParams['figure.dpi'] = 100
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv('dlt_data.csv')
df['前区号码拆分'] = df['前区号码'].str.split(' ')
df['后区号码拆分'] = df['后区号码'].str.split(' ')

# 提取前区号码每个位置的号码
for i in range(5):
    df[f'前区位置{i + 1}'] = df['前区号码拆分'].str[i]

# 提取后区号码每个位置的号码
for i in range(2):
    df[f'后区位置{i + 1}'] = df['后区号码拆分'].str[i]

# 1. 笼统分析 - 统计前区和后区中每个号码出现频率并绘制直方图
front_frequency = df['前区号码拆分'].explode().value_counts(normalize=True).sort_index()
back_frequency = df['后区号码拆分'].explode().value_counts(normalize=True).sort_index()

# 绘制前区号码频率分布直方图
plt.figure(figsize=(12, 6))
all_front_numbers = [str(i).zfill(2) for i in range(1, 36)]
front_frequency = front_frequency.reindex(all_front_numbers).fillna(0)
plt.bar(front_frequency.index.astype(int), front_frequency.values)
plt.title('前区号码频率分布直方图')
plt.xlabel('号码')
plt.ylabel('频率')
plt.xticks(range(1, 36))
plt.show()

# 绘制后区号码频率分布直方图
plt.figure(figsize=(12, 6))
all_back_numbers = [str(i).zfill(2) for i in range(1, 13)]
back_frequency = back_frequency.reindex(all_back_numbers).fillna(0)
plt.bar(back_frequency.index.astype(int), back_frequency.values)
plt.title('后区号码频率分布直方图')
plt.xlabel('号码')
plt.ylabel('频率')
plt.xticks(range(1, 13))
plt.show()

# 2. 分别统计前区和后区中每个位置上出现的号码的频率并绘制直方图
front_position_frequency = {}
for i in range(5):
    front_position_frequency[f'前区位置{i + 1}'] = df[f'前区位置{i + 1}'].value_counts(
        normalize=True).sort_index()

back_position_frequency = {}
for i in range(2):
    back_position_frequency[f'后区位置{i + 1}'] = df[f'后区位置{i + 1}'].value_counts(
        normalize=True).sort_index()

# 绘制前区每个位置号码的频率分布直方图
for i in range(5):
    plt.figure(figsize=(12, 6))
    all_front_numbers = [str(j).zfill(2) for j in range(1, 36)]
    front_position_frequency[f'前区位置{i + 1}'] = front_position_frequency[f'前区位置{i + 1}'].reindex(all_front_numbers).fillna(0)
    plt.bar(front_position_frequency[f'前区位置{i + 1}'].index.astype(int),
            front_position_frequency[f'前区位置{i + 1}'].values)
    plt.title(f'前区位置{i + 1}号码频率分布直方图')
    plt.xlabel('号码')
    plt.ylabel('频率')
    plt.xticks(range(1, 36))
    plt.show()

# 绘制后区每个位置号码的频率分布直方图
for i in range(2):
    plt.figure(figsize=(12, 6))
    all_back_numbers = [str(j).zfill(2) for j in range(1, 13)]
    back_position_frequency[f'后区位置{i + 1}'] = back_position_frequency[f'后区位置{i + 1}'].reindex(all_back_numbers).fillna(0)
    plt.bar(back_position_frequency[f'后区位置{i + 1}'].index.astype(int),
            back_position_frequency[f'后区位置{i + 1}'].values)
    plt.title(f'后区位置{i + 1}号码频率分布直方图')
    plt.xlabel('号码')
    plt.ylabel('频率')
    plt.xticks(range(1, 13))
    plt.show()

# 3. 对前区和后区每个号码分布进行累计出现次数得分计算并绘制指数移动平均趋势图
front_cumulative_counts = {str(i).zfill(2): [] for i in range(1, 36)}
back_cumulative_counts = {str(i).zfill(2): [] for i in range(1, 13)}

for index, row in df.iterrows():
    front_numbers = row['前区号码拆分']
    back_numbers = row['后区号码拆分']
    for num in front_cumulative_counts.keys():
        if len(front_cumulative_counts[num]) == 0:
            count = 1 if num in front_numbers else 0
        else:
            count = front_cumulative_counts[num][-1] + (1 if num in front_numbers else 0)
        front_cumulative_counts[num].append(count)
    for num in back_cumulative_counts.keys():
        if len(back_cumulative_counts[num]) == 0:
            count = 1 if num in back_numbers else 0
        else:
            count = back_cumulative_counts[num][-1] + (1 if num in back_numbers else 0)
        back_cumulative_counts[num].append(count)

# 将累计出现次数转换为 DataFrame
front_cumulative_counts_df = pd.DataFrame(front_cumulative_counts)
back_cumulative_counts_df = pd.DataFrame(back_cumulative_counts)

# 绘制前区指数移动平均趋势图
plt.figure(figsize=(12, 6))
for num in front_cumulative_counts_df.columns:
    fit = ExponentialSmoothing(front_cumulative_counts_df[num], trend='add').fit()
    plt.plot(range(1, len(front_cumulative_counts_df) + 1), fit.fittedvalues, label=num)

plt.title('前区号码累计出现次数指数移动平均趋势图')
plt.xlabel('开奖顺序（1 - 100）')
plt.ylabel('累计出现次数')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.show()

# 绘制后区指数移动平均趋势图
plt.figure(figsize=(12, 6))
for num in back_cumulative_counts_df.columns:
    fit = ExponentialSmoothing(back_cumulative_counts_df[num], trend='add').fit()
    plt.plot(range(1, len(back_cumulative_counts_df) + 1), fit.fittedvalues, label=num)

plt.title('后区号码累计出现次数指数移动平均趋势图')
plt.xlabel('开奖顺序（1 - 100）')
plt.ylabel('累计出现次数')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.show()

# 4. 计算条件概率
front_conditional_prob = {}
for pos1 in range(1, 5):
    for num1 in df[f'前区位置{pos1}'].unique():
        for pos2 in range(pos1 + 1, 6):
            for num2 in df[f'前区位置{pos2}'].unique():
                condition1 = df[f'前区位置{pos1}'] == num1
                condition2 = df[f'前区位置{pos2}'] == num2
                count = (condition1 & condition2).sum()
                prob = count / 100
                front_conditional_prob[(pos1, num1, pos2, num2)] = prob

back_conditional_prob = {}
for pos1 in range(1, 2):
    for num1 in df[f'后区位置{pos1}'].unique():
        for pos2 in range(pos1 + 1, 3):
            for num2 in df[f'后区位置{pos2}'].unique():
                condition1 = df[f'后区位置{pos1}'] == num1
                condition2 = df[f'后区位置{pos2}'] == num2
                count = (condition1 & condition2).sum()
                prob = count / 100
                back_conditional_prob[(pos1, num1, pos2, num2)] = prob

# 选取前区最显著的 5 个条件概率
top_5_front = sorted(front_conditional_prob.items(), key=lambda x: x[1], reverse=True)[:5]

# 选取后区最显著的 2 个条件概率
top_2_back = sorted(back_conditional_prob.items(), key=lambda x: x[1], reverse=True)[:2]

# 输出条件概率结果
print('前区最显著的 5 个条件概率：')
for item in top_5_front:
    print(f'{{位置1：{item[0][0]}，号码1：{item[0][1]}，位置2：{item[0][2]}，号码2：{item[0][3]}，P：{item[1]}}}')

print('后区最显著的 2 个条件概率：')
for item in top_2_back:
    print(f'{{位置1：{item[0][0]}，号码1：{item[0][1]}，位置2：{item[0][2]}，号码2：{item[0][3]}，P：{item[1]}}}')

# 预测号码仅基于频率和近25期线性拟合斜率
# 1. 计算前区号码综合得分：频率（a%）+ 近25期累计次数线性拟合斜率（b%）
a = 0.40
b = 0.60
def get_slope(cumulative_counts, last_n=25):
    """计算近n期累计次数的线性拟合斜率"""
    if len(cumulative_counts) < last_n:
        last_n = len(cumulative_counts)  # 若总期数不足25，取全部
    x = np.arange(len(cumulative_counts)-last_n, len(cumulative_counts))  # 近25期索引
    y = cumulative_counts[-last_n:]  # 近25期累计次数
    slope, _, _, _, _ = stats.linregress(x, y)  # 线性回归求斜率
    return slope

# 计算前区近25期斜率
front_slopes = {num: get_slope(front_cumulative_counts[num]) for num in all_front_numbers}
# 计算后区近25期斜率
back_slopes = {num: get_slope(back_cumulative_counts[num]) for num in all_back_numbers}

# 前区综合得分
front_scores = {}
for num in all_front_numbers:
    # 标准化频率和斜率到0-1区间（斜率可能为负，统一平移到非负区间）
    norm_freq = front_frequency[num] / front_frequency.max()
    min_slope = min(front_slopes.values())
    max_slope = max(front_slopes.values())
    norm_slope = (front_slopes[num] - min_slope) / (max_slope - min_slope + 1e-10)  # 加小值避免除零
    front_scores[num] = a * norm_freq + b * norm_slope

# 后区综合得分
back_scores = {}
for num in all_back_numbers:
    norm_freq = back_frequency[num] / back_frequency.max()
    min_slope = min(back_slopes.values())
    max_slope = max(back_slopes.values())
    norm_slope = (back_slopes[num] - min_slope) / (max_slope - min_slope + 1e-10)
    back_scores[num] = a * norm_freq + b * norm_slope

# 选取得分最高的号码作为推荐（前区5个，后区2个）
recommended_front_numbers = sorted(front_scores, key=front_scores.get, reverse=True)[:5]
recommended_back_numbers = sorted(back_scores, key=back_scores.get, reverse=True)[:2]

print('推荐的前区号码（仅供娱乐参考）：', recommended_front_numbers)
print('推荐的后区号码（仅供娱乐参考）：', recommended_back_numbers)