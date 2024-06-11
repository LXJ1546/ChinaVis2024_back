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


id = "1b0baf552d2cd47ee10b"
data = "Q_bum"
titleTo = {
    "Q_bum": "Question_bumGRTJ0c8p4v5D6eHZa",
    "Q_62X": "Question_62XbhBvJ8NUSnApgDL94",
    "Q_ZTb": "Question_ZTbD7mxr2OUp8Fz6iNjy",
    "Q_FNg": "Question_FNg8X9v5zcbB1tQrxHR3",
    "Q_hZ5": "Question_hZ5wXofebmTlzKB1jNcP",
    "Q_xql": "Question_xqlJkmRaP0otZcX4fK3W",
    "Q_YWX": "Question_YWXHr4G6Cl7bEm9iF2kQ",
    "Q_X3w": "Question_X3wF8QlTyi4mZkDp9Kae",
    "Q_5fg": "Question_5fgqjSBwTPG7KUV3it6O",
    "Q_oCj": "Question_oCjnFLbIs4Uxwek9rBpu",
    "Q_EhV": "Question_EhVPdmlB31M8WKGqL0wc",
    "Q_Az7": "Question_Az73sM0rHfWVKuc4X2kL",
    "Q_Ou3": "Question_Ou3f2Wt9BqExm5DpN7Zk",
    "Q_UXq": "Question_UXqN1F7G3Sbldz02vZne",
    "Q_x2F": "Question_x2Fy7rZ3SwYl9jMQkpOD",
    "Q_Mh4": "Question_Mh4CZIsrEfxkP1wXtOYV",
    "Q_lU2": "Question_lU2wvHSZq7m43xiVroBc",
    "Q_Ej5": "Question_Ej5mBw9rsOUKkFycGvz2",
    "Q_pVK": "Question_pVKXjZn0BkSwYcsa7C31",
    "Q_QRm": "Question_QRm48lXxzdP7Tn1WgNOf",
    "Q_Jr4": "Question_Jr4Wz5jLqmN01KUwHa7g",
    "Q_7NJ": "Question_7NJzCXUPcvQF4Mkfh9Wr",
    "Q_n2B": "Question_n2BTxIGw1Mc3Zo6RLdUe",
    "Q_Nix": "Question_NixCn84GdK2tySa5rB1V",
    "Q_TmK": "Question_TmKaGvfNoXYq4FZ2JrBu",
    "Q_s6V": "Question_s6VmP1G4UbEQWRYHK9Fd",
    "Q_tgO": "Question_tgOjrpZLw4RdVzQx85h6",
    "Q_4nH": "Question_4nHcauCQ0Y6Pm8DgKlLo",
    "Q_6RQ": "Question_6RQj2gF3OeK5AmDvThUV",
    "Q_h7p": "Question_h7pXNg80nJbw1C4kAPRm",
    "Q_x2L": "Question_x2L7AqbMuTjCwPFy6vNr",
    "Q_3Mw": "Question_3MwAFlmNO8EKrpY5zjUd",
    "Q_3oP": "Question_3oPyUzDmQtcMfLpGZ0jW",
    "Q_rvB": "Question_rvB9mVE6Kbd8jAY4NwPx",
    "Q_BW0": "Question_BW0ItEaymH3TkD6S15JF",
    "Q_fZr": "Question_fZrP3FJ4ebUogW9V7taS",
    "Q_q7O": "Question_q7OpB2zCMmW9wS8uNt3H",
    "Q_VgK": "Question_VgKw8PjY1FR6cm2QI9XW",
}

title = titleTo[data]
re1 = {"time": 0, "memory": 0}
info = pd.read_csv('data/detail/aaa.csv')
stu_info = info[(info["student_ID"] == id) & (info["title_ID"] == title)]
# print(stu_info)
# 判断是否存在列 'a' 取值为 'x' 的行
exists_a_x = 'state' in stu_info.columns and (
    stu_info['state'] == 'Absolutely_Correct').any()
if exists_a_x:
    # 获取所有 'a' 列取值为 'x' 的行
    filtered_df = stu_info[stu_info['state'] == 'Absolutely_Correct']
    re1["time"] = filtered_df['timeconsume'].min()
    re1["memory"] = filtered_df['memory'].min()
print(re1)

# # 类型映射
# type_to = {0: '高峰型', 1: '低峰型', 2: '平均型'}
# month_to = {9: '9月', 10: '10月', 11: '11月', 12: '12月', 1: '1月'}
# period_to = {'Dawn': '凌晨', 'Morning': '上午', 'Afternoon': '下午', 'Evening': '晚上'}
# weekday_to = {1: '工作日', 0: '休息日'}
# month_day = {9: {'start': '2023-09-01', 'end': '2023-09-30'}, 10: {'start': '2023-10-01', 'end': '2023-10-31'}, 11: {'start': '2023-11-01',
#                                                                                                                      'end': '2023-11-30'}, 12: {'start': '2023-12-01', 'end': '2023-12-31'}, 1: {'start': '2024-01-01', 'end': '2024-01-25'}}
# # 创建工作日/休息日标识列
# holidays = ['2023-09-29', '2023-10-01', '2023-10-02', '2023-10-03',
#             '2023-10-04', '2023-10-05', '2023-10-06', '2024-01-01']
# tags = read_json('data/cluster/time_cluster_label.json')
# info = pd.read_csv('data/detail/aaa.csv')
# time_feature = read_json('data/cluster/time_cluster_original_feature.json')

# # for month in month_to.keys():
# #     date_range = pd.date_range(
# #         start=month_day[month]['start'], end=month_day[month]['end'], freq='D')
# #     for date in date_range:
# #         weekday = date.weekday()
# #         print(str(date.date()) in holidays)
# #     break


# def is_weekday(date):
#     if (date.weekday() < 5 and str(date.date()) not in holidays):
#         return 1
#     else:
#         return 0


# re_info = {}
# g_period = info.groupby('time_period')
# for period in g_period:
#     g_weekday = period[1].groupby('is_weekday')
#     for week in g_weekday:
#         key = period_to[period[0]]+'-'+weekday_to[week[0]]
#         re_info[key] = {}
#         g_month = week[1].groupby('month')
#         for month in g_month:
#             re_info[key][month[0]] = []
#             date_range = pd.date_range(
#                 start=month_day[month[0]]['start'], end=month_day[month[0]]['end'], freq='D')
#             month_info = month[1]
#             # print(date_range)
#             # 遍历这个月的每一天，
#             for date in date_range:
#                 # 判断是否工作日
#                 weekday = is_weekday(date)
#                 # 与当前循环项是否工作日匹配
#                 if (weekday == week[0]):
#                     # print(str(date.date()))
#                     parts = str(date.date()).split("-")
#                     learning_date = "/".join([part.lstrip("0")
#                                              for part in parts])
#                     date_info = month_info[month_info['date'] == learning_date]
#                     unique_values_count = date_info['student_ID'].nunique()
#                     re_info[key][month[0]].append(unique_values_count)
#                     # print(unique_values_count)
# print(re_info)


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
