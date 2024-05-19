# 分析语言的选择是否对用时和内存有较大的影响

import pandas as pd  # 假设 data 是包含 method、title 和用时的 DataFrame
# data = pd.DataFrame({'method': ['GET', 'GET', 'POST', 'POST', 'GET', 'POST'], 'title': [
#                     'A', 'A', 'A', 'B', 'B', 'B'], 'time': [10, 20, 15, 25, 12, 18]})

# 选择要保留的字段
desired_columns = ['student_ID', 'title_ID',
                   'time', 'state', 'method', 'memory']

# file = "F:/vscode/vis24/data/challenge1/Data_SubmitRecord/SubmitRecord-Class1.csv"
file = "F:/vscode/vis24/data/combined_data.csv"

# 读取数据
data = pd.read_csv(file, low_memory=False)
# print(data['timeconsume'].dtype)
# data['timeconsume'] = data['timeconsume'].astype(float)
data['memory'] = pd.to_numeric(data['memory'], errors='coerce')
# 按照 method 和 title 分组，计算平均用时
grouped_data = data.groupby(['method', 'title_ID']).agg(
    {'memory': 'median'}).reset_index()  # 使用 pivot_table 将结果转换为二维数组
pivot_table = pd.pivot_table(grouped_data, values='memory', index='method',
                             columns='title_ID').fillna(0)  # 输出结果
print(pivot_table)
file_path = 'output1.csv'
pivot_table.to_csv(file_path, index=False)
