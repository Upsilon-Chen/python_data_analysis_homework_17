import requests
import re
import json
import csv
from datetime import datetime


def crawl_dlt_data():
    base_url = 'https://jc.zhcw.com/port/client_json.php'
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,pt-BR;q=0.5,pt;q=0.4',
        'connection': 'keep-alive',
        'host': 'jc.zhcw.com',
        'referer': 'https://www.zhcw.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0'
    }
    params = {
        'callback': 'jQuery112209610648176395699_1752584130517',
        'transactionType': '10001001',
        'lotteryId': '281',
        'issueCount': '106',
        'startIssue': '',
        'endIssue': '',
        'startDate': '',
        'endDate': '',
        'type': '0',
        'pageNum': '1',
        'pageSize': '106',
        'tt': '0.8537108011972389',
        '_' : '1752586106058'
    }
    response = requests.get(base_url, headers=headers, params=params, timeout=10)
    obj = re.compile(r'jQuery112209610648176395699_1752584130517\((?P<json>.*?)\)')
    content = obj.search(response.text).group('json')
    json_temp = json.loads(content)
    data = json_temp['data']
    dlt_data = []
    for item in data:
        issue = item.get('issue', '')
        openTime = item.get('openTime', '')
        week = item.get('week', '')
        frontWinningNum = item.get('frontWinningNum', '')
        backWinningNum = item.get('backWinningNum', '')
        saleMoney = item.get('saleMoney', '')
        prizePoolMoney = item.get('prizePoolMoney', '')
        winnerDetails = []
        for detail in item.get('winnerDetails', []):
            award_etc_match = re.search(r'(\d+)', detail.get('awardEtc', ''))
            if award_etc_match:
                award_etc = int(award_etc_match.group(1))
                if award_etc <= 3:
                    base_winner = detail.get('baseBetWinner', {})
                    add_winner = detail.get('addToBetWinner', {})
                    clean_detail = {
                        'awardEtc': award_etc,
                        'baseBetWinner': {
                            'remark': base_winner.get('remark', ''),
                            'awardNum': base_winner.get('awardNum', ''),
                            'awardMoney': base_winner.get('awardMoney', '')
                        }
                    }
                    if add_winner:
                        clean_detail['addToBetWinner'] = {
                            'remark': add_winner.get('remark', ''),
                            'awardNum': add_winner.get('awardNum', ''),
                            'awardMoney': add_winner.get('awardMoney', '')
                        }
                    winnerDetails.append(clean_detail)
        dlt_data.append({
            'issue': issue,
            'openTime': openTime,
            'week': week,
            'frontWinningNum': frontWinningNum,
            'backWinningNum': backWinningNum,
            'saleMoney': saleMoney,
            'winnerDetails': winnerDetails,
            'prizePoolMoney': prizePoolMoney,
        })
    return dlt_data


def save_to_csv(data, filename=None):
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dlt_data_before_202507_{timestamp}.csv"

    fieldnames = [
        '期号', '开奖日期', '星期', '前区号码', '后区号码', '总销售额(元)',
        '一等奖注数', '一等奖单注奖金(元)', '一等奖追加注数', '一等奖追加单注奖金(元)',
        '二等奖注数', '二等奖单注奖金(元)', '二等奖追加注数', '二等奖追加单注奖金(元)',
        '三等奖注数', '三等奖单注奖金(元)', '奖池(元)'
    ]

    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        total_count = len(data)
        filtered_count = 0
        for item in data:
            open_date = datetime.strptime(item['openTime'], '%Y-%m-%d')
            if open_date.year < 2025 or (open_date.year == 2025 and open_date.month < 7):
                row = {
                    '期号': item['issue'],
                    '开奖日期': item['openTime'],
                    '星期': item['week'],
                    '前区号码': item['frontWinningNum'],
                    '后区号码': item['backWinningNum'],
                    '总销售额(元)': item['saleMoney'],
                    '奖池(元)': item['prizePoolMoney']
                }
                for detail in item['winnerDetails']:
                    if detail['awardEtc'] == 1:
                        base_bet = detail['baseBetWinner']
                        add_bet = detail.get('addToBetWinner', {})
                        row['一等奖注数'] = base_bet['awardNum']
                        row['一等奖单注奖金(元)'] = base_bet['awardMoney']
                        row['一等奖追加注数'] = add_bet.get('awardNum', '')
                        row['一等奖追加单注奖金(元)'] = add_bet.get('awardMoney', '')
                    elif detail['awardEtc'] == 2:
                        base_bet = detail['baseBetWinner']
                        add_bet = detail.get('addToBetWinner', {})
                        row['二等奖注数'] = base_bet['awardNum']
                        row['二等奖单注奖金(元)'] = base_bet['awardMoney']
                        row['二等奖追加注数'] = add_bet.get('awardNum', '')
                        row['二等奖追加单注奖金(元)'] = add_bet.get('awardMoney', '')
                    elif detail['awardEtc'] == 3:
                        base_bet = detail['baseBetWinner']
                        row['三等奖注数'] = base_bet['awardNum']
                        row['三等奖单注奖金(元)'] = base_bet['awardMoney']
                writer.writerow(row)
                filtered_count += 1
    print(f"数据已成功保存到 {filename}")


dlt_data = crawl_dlt_data()
save_to_csv(dlt_data, 'dlt_data.csv')
