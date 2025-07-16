from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

def main():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    base_url = "https://www.tianqihoubao.com/lishi/dalian/"
    
    data_links = []
    for year in range(2022, 2025):  # 包括2022,2023,2024
        for month in range(1, 13):
            ym = f"{year}{month:02d}"  # 格式化为YYYYMM
            url = f"{base_url}month/{ym}.html"
            data_links.append((ym, url))

    # for month in range(1,7):
    #     ym = f"2025{month:02d}"
    #     url = f"{base_url}month/{ym}.html" 
    #     data_links.append((ym, url))
        

    print(f"共生成 {len(data_links)} 个月份的天气链接")

    all_data = []
    for ym, link in data_links:
        print(f"抓取 {ym} 月数据: {link}")
        try:
            driver.get(link)
            # 等待天气表格加载完成
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.weather-table"))
            )
            
            # 解析页面内容
            soup = BeautifulSoup(driver.page_source, "lxml")
            table = soup.find("table", class_="weather-table")
            
            if not table:
                print(f"警告：{link} 页面未找到天气表格")
                continue
                
            # 处理表格数据
            rows = []
            for tr in table.find_all("tr")[1:]:  # 跳过表头行
                tds = tr.find_all("td")
                if len(tds) < 4:  # 确保有足够的数据列
                    continue
                
                # 提取日期、天气状况、气温、风力风向
                date = tds[0].get_text().strip()
                weather = tds[1].get_text().strip().replace("\n", "").replace(" ", "")
                temp = tds[2].get_text().strip().replace("\n", "").replace(" ", "")
                wind = tds[3].get_text().strip().replace("\n", "").replace(" ", "")
                
                rows.append([date, weather, temp, wind])
            
            # 转换为DataFrame
            df = pd.DataFrame(rows, columns=["日期", "天气状况", "气温", "风力风向"])
            df["月份"] = ym
            all_data.append(df)
            
            print(f"成功抓取 {len(rows)} 条数据")
            time.sleep(1)  # 避免请求过快
            
        except Exception as e:
            print(f"抓取 {link} 失败: {str(e)}")

    driver.quit()

    # 合并并保存数据
    if all_data:
        result = pd.concat(all_data, ignore_index=True)
        result.to_csv("dalian_weather_2022_2024.csv", index=False, encoding="utf-8")
        # result.to_csv("dalian_weather_2025_1_6.csv", index=False, encoding="utf-8")
        print(f"数据已保存，合计 {len(result)} 条记录")
    else:
        print("未抓取到任何数据")

if __name__ == "__main__":
    main()