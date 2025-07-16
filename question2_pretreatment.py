import pandas as pd
import numpy as np
import re

# 读取数据
df = pd.read_csv('dalian_weather_2022_2024.csv', encoding='utf-8')
df_2025 = pd.read_csv('dalian_weather_2025_1_6.csv', encoding='utf-8')

# 去除空行
df = df.dropna(subset=['日期', '气温', '风力风向', '天气状况'])

# 提取日期
df['日期'] = df['日期'].str.replace('年', '-').str.replace('月', '-').str.replace('日', '')
df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d')

df_2025['日期'] = df_2025['日期'].str.replace('年', '-').str.replace('月', '-').str.replace('日', '')
df_2025['日期'] = pd.to_datetime(df_2025['日期'], format='%Y-%m-%d')

def extract_temps(temp_str):
    try:
        day, night = temp_str.replace('℃', '').split('/')
        return float(day), float(night)
    except:
        return np.nan, np.nan

df[['最高气温', '最低气温']] = df['气温'].apply(lambda x: pd.Series(extract_temps(x)))
df['平均气温'] = df[['最高气温', '最低气温']].mean(axis=1)

df_2025[['最高气温', '最低气温']] = df_2025['气温'].apply(lambda x: pd.Series(extract_temps(x)))
df_2025['平均气温'] = df_2025[['最高气温', '最低气温']].mean(axis=1)

# 计算每月平均气温、平均最高气温、平均最低气温
df['月份'] = df['日期'].dt.to_period('M')
monthly_avg = df.groupby('月份').agg({
    '平均气温': 'mean',
    '最高气温': 'mean',
    '最低气温': 'mean'
}).reset_index()
monthly_avg['平均气温'] = monthly_avg['平均气温'].round(2)
monthly_avg['平均最高气温'] = monthly_avg['最高气温'].round(2)
monthly_avg['平均最低气温'] = monthly_avg['最低气温'].round(2)
monthly_avg['月份'] = monthly_avg['月份'].astype(str)
monthly_avg = monthly_avg[['月份', '平均气温', '平均最高气温', '平均最低气温']]

df_2025['月份'] = df_2025['日期'].dt.to_period('M')
monthly_avg_2025 = df_2025.groupby('月份').agg({
    '平均气温': 'mean',
    '最高气温': 'mean',
    '最低气温': 'mean'
}).reset_index()
monthly_avg_2025['平均气温'] = monthly_avg_2025['平均气温'].round(2)
monthly_avg_2025['平均最高气温'] = monthly_avg_2025['最高气温'].round(2)
monthly_avg_2025['平均最低气温'] = monthly_avg_2025['最低气温'].round(2)
monthly_avg_2025['月份'] = monthly_avg_2025['月份'].astype(str)
monthly_avg_2025 = monthly_avg_2025[['月份', '平均气温', '平均最高气温', '平均最低气温']]

# ================== 风力等级统计 ==================
def extract_wind_level(wind_str):
    match = re.search(r'(\d+-\d+级|\d+级)', wind_str)
    return match.group(1) if match else None

df['风力等级'] = df['风力风向'].apply(extract_wind_level)
wind_count = df.groupby(['月份', '风力等级']).size().reset_index(name='天数')

# ================== 天气状况统计（白天/夜晚） ==================
def extract_weather_types(weather_str):
    if pd.isna(weather_str):
        return []
    types = str(weather_str).split('/')
    if len(types) == 2 and types[0] == types[1]:
        return [types[0]]
    return list(set(types))

df['天气类型列表'] = df['天气状况'].apply(extract_weather_types)

# 展开每一天的所有天气类型（如晴/多云算晴和多云各一天，相同只算一次）
weather_expanded = df[['月份', '天气类型列表']].explode('天气类型列表')
weather_expanded = weather_expanded.dropna(subset=['天气类型列表'])

# 按月份和天气类型统计天数
weather_count = weather_expanded.groupby(['月份', '天气类型列表']).size().reset_index(name='天数')
weather_count = weather_count.rename(columns={'天气类型列表': '天气类型'})

# 保存结果
df[['日期', '平均气温']].to_csv('daily_avg_temp.csv', index=False, encoding='utf-8-sig')
monthly_avg.to_csv('monthly_avg_temp.csv', index=False, encoding='utf-8-sig')
monthly_avg_2025.to_csv('2025_monthly_avg_temp.csv', index=False, encoding='utf-8-sig')
wind_count.to_csv('monthly_wind_level_days.csv', index=False, encoding='utf-8-sig')
weather_count.to_csv('monthly_weather_days.csv', index=False, encoding='utf-8-sig')

print("每天和每月平均气温、平均最高气温、平均最低气温、每月风力等级及每月天气状况（白天/夜晚）出现天数已计算并保存。")