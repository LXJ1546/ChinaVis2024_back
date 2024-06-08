# 特征箱线图
# data={特征名:[[类型1数据]，[]，[]]}

import pandas as pd
import os
import json
import re
from datetime import datetime

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
weekday_to = {1: '工作日', 0: '休息日'}
month_day = {9: {'start': '2023-09-01', 'end': '2023-09-30'}, 10: {'start': '2023-10-01', 'end': '2023-10-31'}, 11: {'start': '2023-11-01',
                                                                                                                     'end': '2023-11-30'}, 12: {'start': '2023-12-01', 'end': '2023-12-31'}, 1: {'start': '2024-01-01', 'end': '2024-01-25'}}
# 创建工作日/休息日标识列
holidays = ['2023-09-29', '2023-10-01', '2023-10-02', '2023-10-03',
            '2023-10-04', '2023-10-05', '2023-10-06', '2024-01-01']
tags = read_json('data/cluster/time_cluster_label.json')
info = pd.read_csv('data/detail/aaa.csv')
time_feature = read_json('data/cluster/time_cluster_original_feature.json')

# for month in month_to.keys():
#     date_range = pd.date_range(
#         start=month_day[month]['start'], end=month_day[month]['end'], freq='D')
#     for date in date_range:
#         weekday = date.weekday()
#         print(str(date.date()) in holidays)
#     break


def is_weekday(date):
    if (date.weekday() < 5 and str(date.date()) not in holidays):
        return 1
    else:
        return 0


re_info = {}
g_period = info.groupby('time_period')
for period in g_period:
    g_weekday = period[1].groupby('is_weekday')
    for week in g_weekday:
        key = period_to[period[0]]+'-'+weekday_to[week[0]]
        re_info[key] = {}
        g_month = week[1].groupby('month')
        for month in g_month:
            re_info[key][month[0]] = []
            date_range = pd.date_range(
                start=month_day[month[0]]['start'], end=month_day[month[0]]['end'], freq='D')
            month_info = month[1]
            # print(date_range)
            # 遍历这个月的每一天，
            for date in date_range:
                # 判断是否工作日
                weekday = is_weekday(date)
                # 与当前循环项是否工作日匹配
                if (weekday == week[0]):
                    # print(str(date.date()))
                    parts = str(date.date()).split("-")
                    learning_date = "/".join([part.lstrip("0")
                                             for part in parts])
                    date_info = month_info[month_info['date'] == learning_date]
                    unique_values_count = date_info['student_ID'].nunique()
                    re_info[key][month[0]].append(unique_values_count)
                    # print(unique_values_count)
print(re_info)


# # 计算平均值
# result = {}
# i = 0
# for month in ['9', '10', '11', '12', '1']:
#     # 工作日、休息日
#     for weekday in [1, 0]:
#         # 时间段
#         for period in ['Dawn', 'Morning', 'Afternoon', 'Evening']:
#             key = month+'-'+period
#             if key not in result:
#                 result[key] = []
#             result[key].append(time_feature[i][3])
#             i = i+1
# # 使用字典推导式计算平均值并重新赋值给键
# averages = {key: sum(values) / len(values) for key, values in result.items()}
# # print(averages)


# # 依次9到12月
# i = 0
# result = {'weekday': [], 'weekoff': []}
# for month in month_to.keys():
#     # 工作日、休息日
#     for weekday in weekday_to.keys():
#         # 时间段
#         for period in period_to.keys():
#             nums = []
#             for rank in ['top', 'mid', 'low']:
#                 students = info[(info['month'] == month)
#                                 & (info['is_weekday'] == weekday) & (info['rank'] == rank)]
#                 nums.append(len(students.groupby('student_ID')))

#             result[weekday_to[weekday]].append(
#                 [str(month)+'-'+period_to[period], type_to[tags[i]], nums, round(time_feature[i][3], 4), round(averages[str(month)+'-'+period], 4)])
#             # print(result)

#             i = i+1
# print(result)
