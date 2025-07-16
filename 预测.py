import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ------------------ 读取并预处理数据 ------------------
df = pd.read_csv("dblp_conference_papers.csv")

# 确保列名统一小写
df.columns = [col.lower() for col in df.columns]

# 检查必要字段
required_cols = {'conference', 'year'}
if not required_cols.issubset(set(df.columns)):
    raise ValueError(f"CSV 文件必须包含列：{required_cols}")

# 按会议和年份统计论文数量
paper_counts = df.groupby(['conference', 'year']).size().reset_index(name='paper_count')

# ------------------ 灰色预测核心函数 ------------------
def gm11(x0, predict_len=1):
    x0 = np.array(x0)
    n = len(x0)
    x1 = np.cumsum(x0)
    B = np.zeros((n - 1, 2))
    Y = x0[1:]
    for i in range(n - 1):
        B[i][0] = -0.5 * (x1[i] + x1[i + 1])
        B[i][1] = 1.0
    [[a], [b]] = np.linalg.inv(B.T @ B) @ B.T @ Y.reshape(-1, 1)
    def model(k): return (x0[0] - b / a) * np.exp(-a * k) + b / a
    predict = [model(k) - model(k - 1) for k in range(n, n + predict_len)]
    return predict[0], a, b

# ------------------ 多会议预测 + 可视化 ------------------
def predict_next_year_grey_model(paper_counts_df):
    conferences = paper_counts_df['conference'].unique()
    results = []

    plt.figure(figsize=(12, 6))

    for conf in conferences:
        data = paper_counts_df[paper_counts_df['conference'] == conf].sort_values('year')
        years = data['year'].tolist()
        papers = data['paper_count'].tolist()

        if len(papers) < 4:
            print(f"⚠️ 会议 {conf} 数据点太少，建议至少4年数据")
            continue

        next_year = years[-1] + 1
        pred, _, _ = gm11(papers)

        results.append({
            'conference': conf,
            'last_year': years[-1],
            'predicted_year': next_year,
            'predicted_paper_count': int(pred)
        })

        # 可视化历史 + 预测
        full_years = years + [next_year]
        full_papers = papers + [pred]
        plt.plot(years, papers, marker='o', label=f"{conf} history")
        plt.plot([years[-1], next_year], [papers[-1], pred], linestyle='--', marker='x', label=f"{conf} prediction")

    plt.title("Prediction of the Number of Papers for the Next Conference (Grey Model GM(1,1))", fontsize=16)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Number", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(ncol=2)
    plt.tight_layout()
    plt.show()

    return pd.DataFrame(results)

# ------------------ 执行预测 ------------------
result_df = predict_next_year_grey_model(paper_counts)
print(result_df)

# 可选：保存结果
##result_df.to_csv("predicted_conference_papers_grey.csv", index=False)
