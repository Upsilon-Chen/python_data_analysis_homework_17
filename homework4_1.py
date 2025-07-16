import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('dlt_data.csv')
df['开奖日期'] = pd.to_datetime(df['开奖日期'])
df = df.sort_values(by='开奖日期')

plt.rcParams['figure.dpi'] = 100
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

plt.figure(figsize=(12, 6))
plt.plot(df['开奖日期'], df['总销售额(元)'].values)
plt.xlabel('开奖日期')
plt.ylabel('总销售额(元)')
plt.title('大乐透总销售额随开奖日期的变化趋势')
plt.grid(True)
plt.show()

# 定义指数移动平均函数
def exponential_moving_average(data, alpha):
    ema = [data[0]]
    for i in range(1, len(data)):
        ema.append(alpha * data[i] + (1 - alpha) * ema[-1])
    return np.array(ema)

# 对原始销售额数据进行指数移动平均处理，alpha 设置为 0.2
alpha = 0.2
original_sales = df['总销售额(元)'].values
base_trend = exponential_moving_average(original_sales, alpha)

# 准备 Prophet 模型数据
prophet_data = pd.DataFrame({
    'ds': df['开奖日期'],
    'y': base_trend
})

# 创建并拟合 Prophet 模型
model = Prophet()
model.fit(prophet_data)

# 预测未来一期
future = model.make_future_dataframe(periods=1, freq='D', include_history=True)
forecast = model.predict(future)

# 绘制原始数据指数移动平均趋势与预测趋势图
plt.figure(figsize=(12, 6))
plt.plot(df['开奖日期'], base_trend, label='原始数据指数移动平均趋势')
plt.plot(forecast['ds'], forecast['yhat'], label='原始数据指数移动平均趋势预测', linestyle='--')
plt.title('大乐透总销售额原始数据指数移动平均趋势及预测')
plt.xlabel('开奖日期')
plt.xticks(rotation=45)
plt.ylabel('总销售额(元)')
plt.legend()
plt.show()

# 计算一阶差分数据
first_difference = original_sales - base_trend

# 对一阶差分数据进行指数移动平均处理
first_diff_base_trend = exponential_moving_average(first_difference, alpha)

# 绘制一阶差分数据与一阶差分指数移动平均趋势图
plt.figure(figsize=(12, 6))
plt.plot(df['开奖日期'], first_difference, label='一阶差分数据')
plt.plot(df['开奖日期'], first_diff_base_trend, label='一阶差分指数移动平均趋势', linestyle='--')
plt.title('大乐透总销售额一阶差分数据及趋势')
plt.xlabel('开奖日期')
plt.xticks(rotation=45)
plt.ylabel('一阶差分')
plt.legend()
plt.show()

# 计算二阶差分数据
second_difference = first_difference - first_diff_base_trend

# 对二阶差分数据进行指数移动平均处理
second_diff_base_trend = exponential_moving_average(second_difference, alpha)

# 绘制二阶差分数据与二阶差分指数移动平均趋势图
plt.figure(figsize=(12, 6))
plt.plot(df['开奖日期'], second_difference, label='二阶差分数据')
plt.plot(df['开奖日期'], second_diff_base_trend, label='二阶差分指数移动平均趋势', linestyle='--')
plt.title('大乐透总销售额二阶差分数据及趋势')
plt.xlabel('开奖日期')
plt.xticks(rotation=45)
plt.ylabel('二阶差分')
plt.legend()
plt.show()

# 准备二阶差分 Prophet 模型数据
second_diff_prophet_data = pd.DataFrame({
    'ds': df['开奖日期'],
    'y': second_diff_base_trend
})

# 创建并拟合二阶差分 Prophet 模型
second_diff_model = Prophet()
second_diff_model.fit(second_diff_prophet_data)

# 预测二阶差分未来一期
second_diff_future = second_diff_model.make_future_dataframe(periods=1, freq='D', include_history=True)
second_diff_forecast = second_diff_model.predict(second_diff_future)

# 获取二阶差分预测值
next_second_diff_prediction = second_diff_forecast['yhat'].iloc[-1]

# 获取一阶差分指数移动平均趋势的最后一个值
last_first_diff_trend_value = first_diff_base_trend[-1]

# 计算一阶差分预测值
next_first_diff_prediction = last_first_diff_trend_value + next_second_diff_prediction

# 获取原始数据指数移动平均趋势的最后一个值
last_base_trend_value = base_trend[-1]

# 计算最终的销售额预测值
next_sales_prediction = last_base_trend_value + next_first_diff_prediction

# 绘制原数据预测图（包含历史数据和预测点）
plt.figure(figsize=(12, 6))
plt.plot(df['开奖日期'], original_sales, label='历史总销售额')
plt.scatter(df['开奖日期'].iloc[-1] + pd.DateOffset(days=1), next_sales_prediction,
            label='2025 年 7 月 1 日之后最近一期预测销售额', color='red')
plt.title('大乐透总销售额预测')
plt.xlabel('开奖日期')
plt.xticks(rotation=45)
plt.ylabel('总销售额(元)')
plt.legend()
plt.show()

print('2025 年 7 月 1 日之后最近一期的销售额预测值：', next_sales_prediction)
