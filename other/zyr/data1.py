# 检查无效班级：class1表中标记为其他班级的
# 是否要删除无效班级

import os
import csv


def count_column_values(csv_file, column_index):
    counts = {}
    with open(csv_file, 'r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header if present
        for row in reader:
            value = row[column_index]
            counts[value] = counts.get(value, 0) + 1
    return counts


test = 'F:/vscode/vis24/data/challenge1/Data_SubmitRecord/SubmitRecord-Class'
# Replace 1 with the index of the column you want to count (0-indexed)
column_index = 1
combined_data = []
is_first_file = True  # 标记是否是第一个文件
for i in range(1, 16):
    f = test+str(i)+'.csv'
    '''
    检查无效班级
    result = count_column_values(f, column_index)
    print(result)
    '''
    # 读取并处理CSV文件
    with open(f, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # 读取标题行

        # 如果是第一个文件，则将表头添加到合并的数据中一次
        if is_first_file:
            combined_data.append(header)
            is_first_file = False
        data = []

        # 逐行处理数据并删除满足条件的行
        for row in reader:
            if row[column_index] == 'Class'+str(i):
                data.append(row)

        combined_data.extend(data)

# 将处理后的数据写入新的CSV文件
output_file = 'combined_data.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(combined_data)

print("Combined data written to:", output_file)

# 只有表1，6，10有无效班级
result = count_column_values(
    'F:/vscode/vis24/data/combined_data.csv', column_index)
print(result)
