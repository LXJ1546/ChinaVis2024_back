# 查看各个题目的用时和内存是否有差异
import pandas as pd  # 假设 data 是包含 method、title 和用时的 DataFrame

pd.set_option('display.width', 1000)
# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)

# 选择要保留的字段
desired_columns = ['student_ID', 'title_ID',
                   'time', 'state', 'method', 'memory']

# file = "F:/vscode/vis24/data/challenge1/Data_SubmitRecord/SubmitRecord-Class1.csv"
file = "F:/vscode/vis24/data/combined_data.csv"

# 读取数据
data = pd.read_csv(file, low_memory=False)
# print(data['timeconsume'].dtype)
# data['timeconsume'] = data['timeconsume'].astype(float)
data['timeconsume'] = pd.to_numeric(data['timeconsume'], errors='coerce')
# 按照title 分组，计算平均用时
grouped_data = data.groupby(['title_ID']).agg(
    {'timeconsume': 'median'}).reset_index()  # 使用 pivot_table 将结果转换为二维数组
print(grouped_data)
