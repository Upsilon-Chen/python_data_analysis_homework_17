import requests
import json
import pandas as pd
import os
from tqdm import tqdm
import time
import random
from fake_useragent import UserAgent
from retry import retry  # 用于实现重试机制

class HurunRichListScraper:
    def __init__(self):
        """初始化爬虫类，设置基本请求参数"""
        self.base_url = "https://www.hurun.net/zh-CN/Rank/HsRankDetailsList"
        self.ua = UserAgent()
        self.headers = {
            "User-Agent": self.ua.random,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Content-Type": "application/json",
            "Referer": "https://www.hurun.net/zh-CN/Rank/HsRankDetails?pagetype=rich",
            "X-Requested-With": "XMLHttpRequest",
        }
        self.all_data = []
        self.total_pages = 0
        self.per_page = 20  # 每页数据量
        self.max_retries = 3  # 最大重试次数
        self.retry_delay = 5  # 重试间隔（秒）
    
    @retry(requests.RequestException, tries=3, delay=5, backoff=2)
    def _safe_get(self, url, params=None):
        """带重试机制的安全GET请求"""
        response = requests.get(url, params=params, headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()
    
    def get_total_records(self):
        """获取总记录数，计算总页数"""
        try:
            params = {
                "num": "ODBYW2BI",
                "search": "",
                "offset": 0,
                "limit": self.per_page
            }
            data = self._safe_get(self.base_url, params)
            total_records = data.get("total", 0)
            self.total_pages = (total_records + self.per_page - 1) // self.per_page
            return total_records
        except Exception as e:
            print(f"获取总记录数失败: {e}")
            return 0
    
    def fetch_page_data(self, page):
        """获取指定页面的数据，包含重试机制"""
        offset = page * self.per_page
        params = {
            "num": "ODBYW2BI",
            "search": "",
            "offset": offset,
            "limit": self.per_page
        }
        
        try:
            # 添加随机延迟，避免请求过于频繁
            time.sleep(1 + 2 * random.random())
            data = self._safe_get(self.base_url, params)
            return data
        except Exception as e:
            print(f"第{page+1}页爬取失败: {e}，已用尽重试次数")
            return {"rows": [], "total": 0}
    
    def parse_data(self, data):
        """解析JSON数据，提取所需字段"""
        rows = data.get("rows", [])
        for row in rows:
            # 提取个人信息
            person_info = row.get("hs_Character", [{}])[0]
            # 提取财富和排名信息
            rank_info = row
            # 提取企业信息
            company_info = {
                "company_name_cn": rank_info.get("hs_Rank_Rich_ComName_Cn", ""),
                "company_name_en": rank_info.get("hs_Rank_Rich_ComName_En", ""),
                "company_headquarters_cn": rank_info.get("hs_Rank_Rich_ComHeadquarters_Cn", ""),
                "company_headquarters_en": rank_info.get("hs_Rank_Rich_ComHeadquarters_En", ""),
                "industry_cn": rank_info.get("hs_Rank_Rich_Industry_Cn", ""),
                "industry_en": rank_info.get("hs_Rank_Rich_Industry_En", "")
            }
            
            # 组合完整数据
            record = {
                # 个人基本信息
                "fullname_cn": person_info.get("hs_Character_Fullname_Cn", ""),
                "fullname_en": person_info.get("hs_Character_Fullname_En", ""),
                "gender": person_info.get("hs_Character_Gender", ""),
                "birthday": person_info.get("hs_Character_Birthday", ""),
                "age": person_info.get("hs_Character_Age", ""),
                "nationality": person_info.get("hs_Character_Nationality", ""),
                "birth_place_cn": person_info.get("hs_Character_BirthPlace_Cn", ""),
                "permanent_place_cn": person_info.get("hs_Character_Permanent_Cn", ""),
                "education_cn": person_info.get("hs_Character_Education_Cn", ""),
                "school_cn": person_info.get("hs_Character_School_Cn", ""),
                "photo_url": person_info.get("hs_Character_Photo", ""),  # 保留URL但不下载
                
                # 财富和排名信息
                "year": rank_info.get("hs_Rank_Rich_Year", ""),
                "ranking": rank_info.get("hs_Rank_Rich_Ranking", ""),
                "ranking_change": rank_info.get("hs_Rank_Rich_Ranking_Change", ""),
                "wealth_cny": rank_info.get("hs_Rank_Rich_Wealth", ""),
                "wealth_usd": rank_info.get("hs_Rank_Rich_Wealth_USD", ""),
                "wealth_change": rank_info.get("hs_Rank_Rich_Wealth_Change", ""),
                "relations": rank_info.get("hs_Rank_Rich_Relations", ""),
                
                # 企业信息
                "company_name_cn": company_info["company_name_cn"],
                "company_name_en": company_info["company_name_en"],
                "company_headquarters_cn": company_info["company_headquarters_cn"],
                "industry_cn": company_info["industry_cn"]
            }
            self.all_data.append(record)
    
    def save_to_csv(self, filename="hurun_rich_list_2024.csv"):
        """将数据保存为CSV文件"""
        if not self.all_data:
            print("没有数据可保存")
            return
        
        df = pd.DataFrame(self.all_data)
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"数据已保存至 {filename}")
    
    def save_to_json(self, filename="hurun_rich_list_2024.json"):
        """将数据保存为JSON文件"""
        if not self.all_data:
            print("没有数据可保存")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存至 {filename}")
    
    def run(self):
        """运行爬虫主程序"""
        total_records = self.get_total_records()
        if total_records == 0:
            print("无法获取数据记录数，程序终止")
            return
        
        print(f"共发现 {total_records} 条记录，预计 {self.total_pages} 页")
        
        # 使用tqdm显示进度条
        for page in tqdm(range(self.total_pages), desc="爬取进度"):
            page_data = self.fetch_page_data(page)
            self.parse_data(page_data)
        
        print(f"爬取完成，共获取 {len(self.all_data)} 条记录")
        
        # 保存数据
        self.save_to_csv()
        self.save_to_json()

if __name__ == "__main__":
    # 安装依赖: pip install requests pandas tqdm fake-useragent retry
    scraper = HurunRichListScraper()
    scraper.run()