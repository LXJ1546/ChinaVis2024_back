# 特征箱线图
# data={特征名:[[类型1数据]，[]，[]]}

import pandas as pd
import os
import json
import re

pd.set_option('display.width', 1000)
# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)


def read_json(f_name):
    f = open(f_name, 'r')
    content = f.read()
    f.close()
    return (json.loads(content))


def write_dict_to_json(file_path, data):
    # 将字典写入 JSON 文件
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


# 类型映射
type_to = {0: '高峰型', 1: '低峰型', 2: '平均型'}
month_to = {9: '9月', 10: '10月', 11: '11月', 12: '12月', 1: '1月'}
period_to = {'Dawn': '凌晨', 'Morning': '上午', 'Afternoon': '下午', 'Evening': '晚上'}
weekday_to = {1: 'weekday', 0: 'weekoff'}

tags = read_json('data/cluster/time_cluster_label.json')
info = pd.read_csv('data/detail/aaa.csv')
time_feature = read_json('data/cluster/time_cluster_original_feature.json')

# 计算平均值
result = {}
i = 0
for month in ['9', '10', '11', '12', '1']:
    # 工作日、休息日
    for weekday in [1, 0]:
        # 时间段
        for period in ['Dawn', 'Morning', 'Afternoon', 'Evening']:
            key = month+'-'+period
            if key not in result:
                result[key] = []
            result[key].append(time_feature[i][3])
            i = i+1
# 使用字典推导式计算平均值并重新赋值给键
averages = {key: sum(values) / len(values) for key, values in result.items()}
# print(averages)


# 依次9到12月
i = 0
result = {'weekday': [], 'weekoff': []}
for month in month_to.keys():
    # 工作日、休息日
    for weekday in weekday_to.keys():
        # 时间段
        for period in period_to.keys():
            nums = []
            for rank in ['top', 'mid', 'low']:
                students = info[(info['month'] == month)
                                & (info['is_weekday'] == weekday) & (info['rank'] == rank)]
                nums.append(len(students.groupby('student_ID')))

            result[weekday_to[weekday]].append(
                [str(month)+'-'+period_to[period], type_to[tags[i]], nums, round(time_feature[i][3], 4), round(averages[str(month)+'-'+period], 4)])
            # print(result)

            i = i+1
print(result)
