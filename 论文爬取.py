import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import csv

# 要爬取的会议缩写及其在 DBLP 的网址标识
conferences = {
    'AAAI': 'aaai',
    'IJCAI': 'ijcai',
    'CVPR': 'cvpr',
    'ICML': 'icml',
    'ICLR': 'iclr'
}

# 爬取起始年份
start_year = 2020

# 构建每年会议的网址并爬取论文数据
def fetch_papers(conference_acronym, conference_key):
    papers = []
    print(f"\n正在爬取会议 {conference_acronym} ...")

    for year in range(start_year, 2025):  # 可根据当前年份动态设置
        url = f'https://dblp.org/db/conf/{conference_key}/{conference_key}{year}.html'
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print(f"[跳过] {conference_acronym} {year} 页面不存在或访问失败。")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            entries = soup.find_all('cite', class_='data')

            for entry in tqdm(entries, desc=f"{conference_acronym} {year}"):
                title_tag = entry.find('span', class_='title')
                if not title_tag:
                    continue
                title = title_tag.text.strip()

                authors = [a.text.strip() for a in entry.find_all('span', itemprop='author')]

                # 原始链接（第一个外部链接）
                links = entry.find_all('a')
                url_link = ''
                for link in links:
                    href = link.get('href', '')
                    if href.startswith('http'):
                        url_link = href
                        break

                papers.append({
                    'conference': conference_acronym,
                    'year': year,
                    'title': title,
                    'authors': ', '.join(authors),
                    'link': url_link
                })

                time.sleep(0.01)  # 防止请求太频繁
        except Exception as e:
            print(f"发生错误：{e}")
            continue

    return papers

# 主程序
all_papers = []

for conf_acronym, conf_key in conferences.items():
    papers = fetch_papers(conf_acronym, conf_key)
    all_papers.extend(papers)

# 保存为 CSV
csv_file = 'dblp_conference_papers.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['conference', 'year', 'title', 'authors', 'link'])
    writer.writeheader()
    writer.writerows(all_papers)

print(f"\n 所有数据已保存到 {csv_file}")
