import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

# 设置中文显示和高分辨率
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['savefig.dpi'] = 600
plt.rcParams['figure.figsize'] = (12, 8)

# 输出路径
desktop_path = Path.home() / 'Desktop'
output_dir = desktop_path / '富豪人口统计学分析'
os.makedirs(output_dir, exist_ok=True)

# 加载数据
df = pd.read_csv('hurun_rich_list_2024.csv')

# 数据预处理（仅处理出生地相关）
def preprocess_birth_place(df):
    # 过滤掉“未知”并确保所有值是字符串
    if 'birth_place_cn' in df.columns:
        df = df[df['birth_place_cn'].notna() & (df['birth_place_cn'] != '未知')]
        df['birth_place_cn'] = df['birth_place_cn'].astype(str)
        
        # 省份映射（扩展映射表以覆盖更多地区）
        province_map = {
            '北京': '北京', '上海': '上海', '天津': '天津', '重庆': '重庆',
            '河北': '河北', '山西': '山西', '辽宁': '辽宁', '吉林': '吉林', 
            '黑龙江': '黑龙江', '江苏': '江苏', '浙江': '浙江', '安徽': '安徽',
            '福建': '福建', '江西': '江西', '山东': '山东', '河南': '河南',
            '湖北': '湖北', '湖南': '湖南', '广东': '广东', '海南': '海南',
            '四川': '四川', '贵州': '贵州', '云南': '云南', '陕西': '陕西',
            '甘肃': '甘肃', '青海': '青海', '台湾': '台湾', '内蒙古': '内蒙古',
            '广西': '广西', '西藏': '西藏', '宁夏': '宁夏', '新疆': '新疆',
            '香港': '香港', '澳门': '澳门'
        }
        
        # 提取省份信息
        df['province'] = df['birth_place_cn'].apply(
            lambda x: next((k for k, v in province_map.items() if k in x), '其他')
        )
        print("省份分布统计：\n", df['province'].value_counts())
        return df
    else:
        print("数据中缺少 birth_place_cn 列！")
        return df

# 预处理数据
df = preprocess_birth_place(df)

# 生成出生地TOP10水平柱状图
province_counts = df['province'].value_counts().head(10)
if len(province_counts) < 10:
    print(f"警告：仅找到 {len(province_counts)} 个省份的数据，可能存在数据不足。")

plt.figure()
sns.barplot(x=province_counts.values, y=province_counts.index, 
            palette='Blues_r', edgecolor='black', orient='h')
plt.title('富豪出生地TOP10省份', fontsize=16, pad=15)
plt.xlabel('人数', fontsize=12)
plt.ylabel('省份', fontsize=12)

# 添加数据标签
for i, v in enumerate(province_counts.values):
    plt.text(v + 2, i, str(v), va='center', fontsize=10)

plt.grid(axis='x', linestyle='--', alpha=0.3)
plt.tight_layout()
plt.savefig(output_dir / '富豪出生地TOP10水平.png', bbox_inches='tight', dpi=600)
plt.close()

print(f"分析完成！图表已保存至: {output_dir}")    