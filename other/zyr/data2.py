# 检查是否存在前一题对了，后面错了
import pandas as pd
pd.set_option('display.width', 1000)
# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)

# 定义一个函数，对每个组进行排序


def sort_by_timestamp(group):
    return group.sort_values('time', ascending=True)


# 选择要保留的字段
desired_columns = ['student_ID', 'title_ID', 'time', 'state']

# 读取数据
data = pd.read_csv(
    "F:/vscode/vis24/data/challenge1/Data_SubmitRecord/SubmitRecord-Class1.csv")
# 按学生id和题目id分组，并统计每个组的答题状态变化情况
data = data[desired_columns]
grouped_data = data.groupby(
    ['student_ID', 'title_ID']).apply(sort_by_timestamp)[['state', 'time', 'student_ID']]
# grouped_data = data.groupby(['student_ID', 'title_ID']).apply(
#     sort_by_timestamp).reset_index(drop=True)

# for i in grouped_data:
#     print(i)

# 输出结果
print(grouped_data)
