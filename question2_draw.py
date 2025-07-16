import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import os

# 设置全局样式
plt.style.use('seaborn-v0_8-darkgrid')  # 使用更美观的主题
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']  # 更好的中文字体支持
plt.rcParams['axes.unicode_minus'] = False

# 读取月平均气温数据
monthly_avg = pd.read_csv('monthly_avg_temp.csv', encoding='utf-8')

# ========== 近三年月平均气温变化图 ==========
plt.figure(figsize=(14, 7), facecolor='#f8f9fa')  # 添加浅色背景
ax = plt.gca()
ax.set_facecolor('#f0f2f6')  # 设置坐标区背景色

# 绘制折线图
plt.plot(monthly_avg['月份'], monthly_avg['平均气温'], 
         marker='o', markersize=8, markerfacecolor='white', markeredgewidth=2,
         color='#2c7bb6', linewidth=3, alpha=0.9, label='月平均气温')

# 美化标题和标签
plt.title('近三年月平均气温变化趋势', fontsize=22, pad=20, fontweight='bold')
plt.xlabel('月份', fontsize=16, labelpad=12)
plt.ylabel('平均气温 (℃)', fontsize=16, labelpad=12)

# 坐标轴美化
plt.xticks(rotation=45, fontsize=13)
plt.yticks(fontsize=13)
ax.xaxis.set_minor_locator(MultipleLocator(1))  # 添加次要刻度
ax.yaxis.set_minor_locator(MultipleLocator(1))
ax.tick_params(axis='both', which='both', length=6, width=1.5)

# 网格和边框处理
ax.grid(which='major', linestyle='-', linewidth=1.2, alpha=0.7)
ax.grid(which='minor', linestyle=':', linewidth=0.8, alpha=0.4)
for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_linewidth(1.8)
    spine.set_color('#333333')

# 添加数据标签
for i, temp in enumerate(monthly_avg['平均气温']):
    plt.annotate(f'{temp:.1f}℃', 
                 (monthly_avg['月份'][i], temp),
                 textcoords="offset points", 
                 xytext=(0,10), 
                 ha='center', 
                 fontsize=11,
                 color='#2c5a82')

# 图例和布局
plt.legend(fontsize=14, loc='best', frameon=True, shadow=True)
plt.tight_layout(pad=3.0)
plt.savefig('monthly_avg_temp_trend.png', dpi=300, bbox_inches='tight')

# ========== 一年中气温变化趋势图 ==========
monthly_avg['月'] = monthly_avg['月份'].str[5:7].astype(int)
avg_by_month = monthly_avg.groupby('月').agg({
    '平均最高气温': 'mean',
    '平均最低气温': 'mean'
}).reset_index()
avg_by_month = avg_by_month.sort_values('月')

plt.figure(figsize=(12, 6.5), facecolor='#f8f9fa')
ax = plt.gca()
ax.set_facecolor('#f0f2f6')

# 绘制高低气温区间填充
plt.fill_between(avg_by_month['月'], 
                 avg_by_month['平均最低气温'], 
                 avg_by_month['平均最高气温'], 
                 color='#d1e5f0', alpha=0.8, label='温度区间')

# 绘制高低气温线
plt.plot(avg_by_month['月'], avg_by_month['平均最高气温'], 
         marker='^', markersize=10, markerfacecolor='white', markeredgewidth=2,
         color='#d7191c', linewidth=3, alpha=0.9, label='平均最高气温')
plt.plot(avg_by_month['月'], avg_by_month['平均最低气温'], 
         marker='v', markersize=10, markerfacecolor='white', markeredgewidth=2,
         color='#2c7bb6', linewidth=3, alpha=0.9, label='平均最低气温')

# 美化标题和标签
plt.title('一年中气温变化趋势（近三年平均）', fontsize=22, pad=20, fontweight='bold')
plt.xlabel('月份', fontsize=16, labelpad=12)
plt.ylabel('气温 (℃)', fontsize=16, labelpad=12)

# 坐标轴美化
plt.xticks(avg_by_month['月'], [f"{m}月" for m in avg_by_month['月']], fontsize=13)
plt.yticks(fontsize=13)
ax.xaxis.set_minor_locator(MultipleLocator(0.5))
ax.yaxis.set_minor_locator(MultipleLocator(1))
ax.tick_params(axis='both', which='both', length=6, width=1.5)

# 网格和边框处理
ax.grid(which='major', linestyle='-', linewidth=1.2, alpha=0.7)
ax.grid(which='minor', linestyle=':', linewidth=0.8, alpha=0.4)
for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_linewidth(1.8)
    spine.set_color('#333333')

# 添加数据标签
for i, row in avg_by_month.iterrows():
    plt.annotate(f'{row["平均最高气温"]:.1f}℃', 
                 (row['月'], row['平均最高气温']), 
                 textcoords="offset points", 
                 xytext=(0,10), 
                 ha='center', 
                 fontsize=11,
                 color='#a50f15')
    plt.annotate(f'{row["平均最低气温"]:.1f}℃', 
                 (row['月'], row['平均最低气温']), 
                 textcoords="offset points", 
                 xytext=(0,-15), 
                 ha='center', 
                 fontsize=11,
                 color='#1a4f72')

# 图例和布局
plt.legend(fontsize=14, loc='best', frameon=True, shadow=True)
plt.tight_layout(pad=3.0)
plt.savefig('yearly_month_high_low_temp_trend.png', dpi=300, bbox_inches='tight')

# ========== 风力等级分布饼图 ==========
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']  # 更好的中文字体支持
plt.rcParams['axes.unicode_minus'] = False

# 读取风力等级统计数据
wind_count = pd.read_csv('monthly_wind_level_days.csv', encoding='utf-8')

# 提取月份数字
wind_count['月'] = wind_count['月份'].str[5:7].astype(int)

# 按风力等级和月份统计三年平均天数
avg_wind = (
    wind_count.groupby(['月', '风力等级'])['天数'].sum().reset_index()
)
avg_wind['天数'] = (avg_wind['天数'] / 3).round(2)
# 获取所有唯一的风力等级并排序
all_wind_levels = sorted(avg_wind['风力等级'].unique(), key=lambda x: int(x.split('-')[0]) if '-' in x else int(x))

# 创建风力等级到颜色的映射
# 使用从浅蓝到深红的渐变表示风力强度
colors = plt.cm.YlGnBu(np.linspace(0.2, 0.8, len(all_wind_levels)))
color_map = {level: colors[i] for i, level in enumerate(all_wind_levels)}

# 创建12个月份的图表
for m in range(1, 13):
    month_data = avg_wind[avg_wind['月'] == m].sort_values('天数', ascending=False)
    
    # 如果当月没有数据，跳过
    if month_data.empty:
        print(f"警告: {m}月没有数据，跳过")
        continue
        
    # 创建图表和子图
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='#f8f9fa')
    fig.subplots_adjust(top=0.85)
    
    # 设置背景
    ax.set_facecolor('#f0f2f6')
    
    # 计算爆炸效果 - 突出显示最大部分
    max_index = month_data['天数'].idxmax()
    explode = [0.05 if i == max_index else 0 for i in month_data.index]
    
    # 获取颜色
    colors = [color_map[lvl] for lvl in month_data['风力等级']]
    
    # 绘制饼图
    wedges, texts, autotexts = ax.pie(
        month_data['天数'],
        labels=month_data['风力等级'],
        autopct=lambda pct: f'{pct:.1f}%' if pct > 5 else '',  # 小百分比不显示标签
        startangle=90,
        counterclock=False,
        colors=colors,
        explode=explode,
        wedgeprops={
            'edgecolor': 'white',
            'linewidth': 2,
            'linestyle': '-',
            'alpha': 0.95
        },
        textprops={
            'fontsize': 12,
            'color': '#333333',
            'fontweight': 'bold'
        },
        pctdistance=0.85,
        labeldistance=1.05
    )
    
    # 美化百分比文本
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(11)
        autotext.set_fontweight('bold')
    
    # 添加中心圆，创建环形图效果
    centre_circle = plt.Circle((0,0), 0.70, fc='white', edgecolor='#e0e0e0', linewidth=1.5)
    ax.add_artist(centre_circle)
    
    # 添加标题和副标题
    plt.title(f'{m}月风力等级分布', fontsize=22, fontweight='bold', pad=20)
    plt.suptitle('近三年不同等级风力平均出现天数占比', fontsize=16, y=0.95, color='#555555')
    
    # 添加图例
    total_days = month_data['天数'].sum()
    legend_labels = [f"{lvl}风: {days:.1f}天 ({days/total_days*100:.1f}%)" 
                    for lvl, days in zip(month_data['风力等级'], month_data['天数'])]
    
    plt.legend(wedges, legend_labels,
              title="风力等级说明",
              loc="center left",
              bbox_to_anchor=(1, 0.5),
              fontsize=11,
              frameon=True,
              framealpha=0.9,
              edgecolor='#cccccc',
              shadow=True)
    
    # 添加脚注
    plt.figtext(0.5, 0.01, f"数据统计周期: {wind_count['月份'].min()} 至 {wind_count['月份'].max()}", 
               ha="center", fontsize=10, color='#777777')
    
    # 添加风力等级说明
    plt.figtext(0.5, 0.06, "注: 颜色从浅到深表示风力强度增强", 
               ha="center", fontsize=9, color='#555555', style='italic')
    
    # 保存和关闭
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])  # 为脚注留出空间
    plt.savefig(f'wind_level_pie_{m:02d}.png', dpi=600, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()

# ========== 天气状况分布柱状图 ==========
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']  # 更好的中文字体支持
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
weather_count = pd.read_csv('monthly_weather_days.csv', encoding='utf-8')

# 提取月份数字
weather_count['月'] = weather_count['月份'].str[5:7].astype(int)

# 按天气类型和月份统计三年平均天数
avg_weather = (
    weather_count.groupby(['月', '天气类型'])['天数'].sum()
    .reset_index()
)
avg_weather['天数'] = (avg_weather['天数'] / 3).round(2)


# 创建输出目录
output_dir = 'monthly_weather_charts'
os.makedirs(output_dir, exist_ok=True)

# 设置天气类型对应的专业配色
weather_colors = {
    # 晴天相关
    '晴': '#FFD700',        # 金色
    
    # 多云/阴天相关
    '多云': '#A9A9A9',      # 深灰色
    '阴': '#778899',        # 浅灰色
    
    # 雨天相关（从浅到深）
    '小雨': '#87CEEB',      # 浅蓝色
    '小到中雨': '#5F9EA0',  # 卡其蓝
    '中雨': '#1E90FF',      # 道奇蓝
    '中到大雨': '#4169E1',  # 皇家蓝
    '大雨': '#0000CD',      # 中蓝色
    '大到暴雨': '#00008B',   # 深蓝色
    '暴雨': '#191970',      # 午夜蓝
    '大暴雨': '#000033',    # 极深蓝
    
    # 阵雨相关
    '阵雨': '#6495ED',      # 矢车菊蓝
    '雷阵雨': '#483D8B',    # 深板岩蓝
    
    # 雪天相关（从浅到深）
    '小雪': '#F0F8FF',      # 爱丽丝蓝
    '小到中雪': '#B0E0E6',  # 粉蓝
    '中雪': '#ADD8E6',      # 浅蓝
    '中到大雪': '#87CEEB',  # 天蓝
    '大雪': '#4682B4',      # 钢蓝
    
    # 混合天气
    '雨夹雪': '#B0C4DE'     # 亮钢蓝
}

# 创建12个月份的图表
for month in range(1, 13):
    # 获取当月数据
    month_data = avg_weather[avg_weather['月'] == month]
    
    # 过滤掉天数为0的天气类型
    month_data = month_data[month_data['天数'] > 0]
    
    # 如果当月没有数据，跳过
    if month_data.empty:
        print(f"警告: {month}月没有天气数据，跳过")
        continue
    
    # 按天数降序排序
    month_data = month_data.sort_values('天数', ascending=False)
    
    # 创建图表 - 增加高度以适应垂直柱形图
    fig, ax = plt.subplots(figsize=(12, 10), facecolor='#f8f9fa')  # 增加高度到10
    fig.subplots_adjust(top=0.92, bottom=0.22, left=0.1, right=0.95)  # 调整底部边距
    
    # 设置背景
    ax.set_facecolor('#f0f2f6')
    
    # 获取天气类型和天数
    weather_types = month_data['天气类型'].tolist()
    days = month_data['天数'].tolist()
    
    # 获取对应的颜色
    colors = [weather_colors.get(wt, '#999999') for wt in weather_types]
    
    # 绘制垂直柱状图 (修改点1)
    bars = ax.bar(
        weather_types, 
        days, 
        width=0.7, 
        color=colors,
        edgecolor='white',
        linewidth=1.5,
        alpha=0.95,
        zorder=3
    )
    
    # 添加数据标签 (修改点2)
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.05,  # 在柱子顶部上方显示
            f'{height:.1f}天',
            ha='center',
            va='bottom',
            fontsize=12,
            fontweight='bold',
            color='#333333'
        )
    
    # 设置标题
    plt.title(f'{month}月不同天气状况出现的平均天数（近三年）', 
              fontsize=22, fontweight='bold', pad=20)
    
    # 设置坐标轴标签 (修改点3)
    plt.ylabel('平均天数', fontsize=16, labelpad=12)
    plt.xlabel('天气类型', fontsize=16, labelpad=12)
    
    # 设置y轴范围 (修改点4)
    max_days = max(days) * 1.2  # 留出空间给标签
    plt.ylim(0, max_days)
    plt.yticks(fontsize=13)
    
    # 设置x轴标签旋转 (修改点5)
    plt.xticks(rotation=30, ha='right', fontsize=14)
    
    # 添加网格 (修改点6)
    ax.grid(axis='y', linestyle='--', linewidth=1.0, alpha=0.6)
    ax.grid(axis='x', visible=False)
    
    # 美化边框
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.8)
        spine.set_color('#333333')
    
    # 添加数据来源和说明
    source_text = f"数据统计周期: {weather_count['月份'].min()} 至 {weather_count['月份'].max()}"
    note_text = f"注: 仅显示{month}月实际出现的天气类型"
    
    plt.figtext(0.5, 0.03, f"{source_text} | {note_text}", 
               ha="center", fontsize=12, color='#666666')
    
    # 保存图像
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    filename = os.path.join(output_dir, f'month_{month:02d}_weather_chart.png')
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()

print("所有图表生成完成！")