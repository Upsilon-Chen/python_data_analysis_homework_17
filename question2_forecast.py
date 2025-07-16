import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.dates as mdates

# 设置全局样式
plt.style.use('seaborn-whitegrid')
mpl.rcParams['font.family'] = 'Microsoft YaHei'
mpl.rcParams['axes.unicode_minus'] = False

# 加载数据
hist_data = pd.read_csv('monthly_avg_temp.csv')
hist_data['日期'] = pd.to_datetime(hist_data['月份'], format='%Y-%m')
hist_data.set_index('日期', inplace=True)

new_data = pd.read_csv('2025_monthly_avg_temp.csv')
new_data['日期'] = pd.to_datetime(new_data['月份'], format='%Y-%m')
new_data.set_index('日期', inplace=True)

# 准备训练数据
train = hist_data['2022-01':'2024-12']['平均最高气温'].astype(float)

# 训练模型
model = SARIMAX(train, 
                order=(1, 1, 1), 
                seasonal_order=(1, 1, 1, 12),
                enforce_stationarity=False,
                enforce_invertibility=False)
results = model.fit(disp=False)

# 预测
forecast = results.get_forecast(steps=6)
pred_mean = forecast.predicted_mean
pred_ci = forecast.conf_int()
actual = new_data['2025-01':'2025-09']['平均最高气温']

# 构造完整的月份索引
all_months = pd.date_range('2023-01-01', '2025-07-01', freq='MS')

# 补齐历史数据
train_plot = train.copy()
train_plot.index = pd.to_datetime(train_plot.index)
train_plot = train_plot.reindex(all_months)

# 补齐预测数据
pred_mean_plot = pd.Series(np.nan, index=all_months)
pred_mean_plot.loc[pred_mean.index] = pred_mean.values

# 补齐真实数据
actual_plot = pd.Series(np.nan, index=all_months)
actual_plot.loc[actual.index] = actual.values

# 绘图
plt.figure(figsize=(12, 7), dpi=120)
plt.title('2025年月度平均最高气温预测 vs 实际值', fontsize=20, fontweight='bold', pad=18)

colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

train_plot.plot(
    label='历史数据 (2023-2024)', 
    color=colors[0], 
    linewidth=2.5,
    marker='o', 
    markersize=7
)

pred_mean_plot.plot(
    label='预测值 (2025)', 
    color=colors[1], 
    linewidth=2.5,
    linestyle='--',
    marker='s', 
    markersize=7
)

actual_plot.plot(
    label='真实值 (2025)', 
    color=colors[2], 
    linewidth=2.5,
    marker='D', 
    markersize=7
)

# 置信区间只在预测区间绘制
if not pred_ci.empty:
    plt.fill_between(
        pred_ci.index, 
        pred_ci.iloc[:, 0], 
        pred_ci.iloc[:, 1], 
        color=colors[1], 
        alpha=0.18,
        label='95%置信区间'
    )

plt.ylabel('温度 (℃)', fontsize=14)
plt.xlabel('月份', fontsize=14)
plt.legend(loc='upper left', fontsize=12, frameon=True, framealpha=0.9)
plt.xticks(all_months, [d.strftime('%Y-%m') for d in all_months], rotation=30, ha='right', fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout(rect=[0, 0, 1, 0.97])

plt.figtext(0.5, 0.01, 
            '数据来源：2022-2025年月度气温数据 | SARIMAX(1,1,1)(1,1,1,12) | 置信水平：95%', 
            ha='center', fontsize=11, color='#555555')

# 标出预测值和真实值的数据点
for i in range(len(all_months)):
    month = all_months[i]
    # 标注预测值
    if not np.isnan(pred_mean_plot[month]):
        plt.text(month, pred_mean_plot[month]+0.5, 
                 f'{pred_mean_plot[month]:.2f}', 
                 color=colors[1], fontsize=11, ha='center', va='bottom', fontweight='bold')
    # 标注真实值
    if not np.isnan(actual_plot[month]):
        plt.text(month, actual_plot[month]-0.5, 
                 f'{actual_plot[month]:.2f}', 
                 color=colors[2], fontsize=11, ha='center', va='top', fontweight='bold')

plt.savefig('temperature_forecast_chinese_main.png', dpi=300, bbox_inches='tight')
plt.show()

plt.figure(figsize=(10, 6), dpi=120)
plt.title('2025年月度平均最高气温预测', fontsize=18, fontweight='bold', pad=15)

forecast_start = pred_ci.index[0]
forecast_end = pred_ci.index[-1]

# 提取预测区间的数据
pred_interval = pred_mean_plot.loc[forecast_start:forecast_end]
actual_interval = actual_plot.loc[forecast_start:forecast_end]

pred_interval.plot(
    color='#ff7f0e', 
    linewidth=2.5,
    linestyle='-',
    marker='o', 
    markersize=8,
    label='预测值'
)

plt.fill_between(
    pred_ci.index, 
    pred_ci.iloc[:, 0], 
    pred_ci.iloc[:, 1], 
    color='#1f77b4', 
    alpha=0.18,
    label='95% 预测区间'
)

# 绘制实际值（如果存在）
if not actual_interval.isnull().all():
    actual_interval.plot(
        color='#2ca02c', 
        linewidth=2.5,
        marker='D', 
        markersize=8,
        label='实际值'
    )

# 标注数据点
for date in pred_ci.index:
    # 标注预测值
    if not np.isnan(pred_interval[date]):
        plt.text(
            date, 
            pred_interval[date] + 0.3, 
            f'{pred_interval[date]:.1f}℃', 
            color='#ff7f0e', 
            fontsize=11, 
            ha='center', 
            va='bottom', 
            fontweight='bold',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2')
        )
    
    # 标注实际值（如果存在）
    if not actual_interval.isnull().all() and not np.isnan(actual_interval[date]):
        plt.text(
            date, 
            actual_interval[date] - 0.3, 
            f'{actual_interval[date]:.1f}℃', 
            color='#2ca02c', 
            fontsize=11, 
            ha='center', 
            va='top', 
            fontweight='bold',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2')
        )

# 设置坐标轴和网格
plt.ylabel('温度 (℃)', fontsize=13)
plt.xlabel('月份', fontsize=13)
plt.xticks(pred_ci.index, [d.strftime('%Y-%m') for d in pred_ci.index], 
           rotation=30, ha='right', fontsize=11)
plt.yticks(fontsize=11)
plt.grid(True, linestyle='--', alpha=0.7)

# 添加图例
plt.legend(loc='upper left', fontsize=11, frameon=True, framealpha=0.9)

# 添加脚注
plt.figtext(0.5, 0.01, 
            '数据来源：2022-2025年月度气温数据 | SARIMAX(1,1,1)(1,1,1,12) | 置信水平：95%', 
            ha='center', fontsize=10, color='#555555')

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig('prediction_interval_zoomed.png', dpi=300, bbox_inches='tight')
plt.show()