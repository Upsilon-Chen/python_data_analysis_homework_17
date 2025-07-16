import requests
import json
import csv
from datetime import datetime
import os


def crawl_zj_data():
    base_url = 'https://i.cmzj.net/expert/queryExpertById'
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,pt-BR;q=0.5,pt;q=0.4',
        'authorization_code': '',
        'connection': 'keep-alive',
        'host': 'i.cmzj.net',
        'origin': 'https://www.cmzj.net',
        'referer': 'https://www.cmzj.net/',
        'sec-ch-ua': '"Not)A;Brand";v = "8", "Chromium";v = "138", "Microsoft Edge";v = "138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0'
    }
    ids = [
        2088315, 1924319, 2500940, 2367322, 2118856, 2712177, 2235738, 1820937, 2604328, 2349046,
        2290189, 2037784, 2370927, 1689690, 1935616, 2295059, 2370219, 1921296, 1724513, 1961120
    ]
    zj_data = []
    for id in ids:
        params = {
            'expertId': f'{id}'
        }
        response = requests.get(base_url, headers=headers, params=params, timeout=10)
        json_temp = json.loads(response.text)
        content = json_temp['data']
        required_fields = [
            'expertId', 'name', 'age', 'articles', 'fans', 'skills',
            'ssqOne', 'ssqTwo', 'ssqThree', 'dltOne', 'dltTwo', 'dltThree'
        ]
        result = {field: content.get(field) for field in required_fields}
        zj_data.append(result)
    return zj_data


def save_to_csv(data, filename=None):
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"zj_data_{timestamp}.csv"
    fieldnames = [
        '专家ID', '姓名', '彩龄', '文章数量', '粉丝数', '彩种等级',
        '双色球一等奖', '双色球二等奖', '双色球三等奖',
        '大乐透一等奖', '大乐透二等奖', '大乐透三等奖'
    ]
    field_mapping = {
        'expertId': '专家ID',
        'name': '姓名',
        'age': '彩龄',
        'articles': '文章数量',
        'fans': '粉丝数',
        'skills': '彩种等级',
        'ssqOne': '双色球一等奖',
        'ssqTwo': '双色球二等奖',
        'ssqThree': '双色球三等奖',
        'dltOne': '大乐透一等奖',
        'dltTwo': '大乐透二等奖',
        'dltThree': '大乐透三等奖'
    }
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            total_count = len(data)
            valid_count = 0
            for expert in data:
                row = {}
                for orig_key, chn_key in field_mapping.items():
                    value = expert.get(orig_key)
                    row[chn_key] = value if value is not None else ''
                writer.writerow(row)
                valid_count += 1
        print(f"数据处理完成：共{total_count}条数据，成功写入{valid_count}条")
        print(f"文件已保存至: {os.path.abspath(filename)}")
    except Exception as e:
        print(f"保存文件时出错: {str(e)}")


zj_data = crawl_zj_data()
save_to_csv(zj_data, 'zj_data.csv')
