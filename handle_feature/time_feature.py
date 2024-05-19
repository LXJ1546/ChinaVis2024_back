import pandas as pd
import os
import re
import json
import calendar
import numpy as np
from collections import defaultdict
from datetime import datetime


# 将字典保存为JSON文件
def save_to_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


# 每个月中工作日和休息日的天数
def caculate_day():
    year = 2024
    month = 1
    # 获取指定月份的天数
    num_days = calendar.monthrange(year, month)[1]
    # 初始化工作日和休息日的计数器
    working_days = 0
    non_working_days = 0
    # 遍历每一天，计算工作日和休息日的数量
    for day in range(1, num_days + 1):
        # 创建日期对象
        date_obj = datetime(year, month, day)
        # 判断是否是工作日（周一到周五为工作日）
        if date_obj.weekday() < 5:
            working_days += 1
        else:
            non_working_days += 1
    print(
        f"{year}年{month}月有 {working_days} 天工作日和 {non_working_days} 天休息日。"
    )


# 计算每个时段的所有提交次数总和
def time_total_submit():
    folder_path = "data/temporary/s-t-g"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    day_count = [[20, 10], [17, 14], [22, 8], [21, 10], [18, 7]]
    # 用于存储每个时间段的次数
    all_counts = [[0] * 8 for _ in range(5)]
    all_students = []
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取数据
        with open(file_path, "r") as f:
            student_title_group = json.load(f)
        # print(len(student_title_group))
        num = 0
        # 遍历每个学生的答题记录
        for _, answers in student_title_group.items():
            all_active = [[set() for _ in range(8)] for _ in range(5)]
            # 遍历每道题目的答题记录
            for _, answer_list in answers.items():
                # 遍历每个答题记录
                for _, answer in enumerate(answer_list):
                    num += 1
                    # 将 Unix 时间戳转换为 datetime 对象
                    dt = datetime.fromtimestamp(answer[0])
                    month_index = 0
                    inner_index = 0
                    if dt.month == 8:
                        continue
                    if dt.month == 9:
                        month_index = 0
                    elif dt.month == 10:
                        month_index = 1
                    elif dt.month == 11:
                        month_index = 2
                    elif dt.month == 12:
                        month_index = 3
                    else:
                        month_index = 4
                    if dt.weekday() < 5:
                        if 0 <= dt.hour < 6:
                            inner_index = 0
                        elif 6 <= dt.hour < 12:
                            inner_index = 1
                        elif 12 <= dt.hour < 18:
                            inner_index = 2
                        elif 18 <= dt.hour < 24:
                            inner_index = 3
                    else:
                        if 0 <= dt.hour < 6:
                            inner_index = 4
                        elif 6 <= dt.hour < 12:
                            inner_index = 5
                        elif 12 <= dt.hour < 18:
                            inner_index = 6
                        elif 18 <= dt.hour < 24:
                            inner_index = 7
                    if (
                        (dt.month == 9 and dt.day == 29)
                        or (dt.month == 10 and dt.day in [2, 3, 4, 5, 6])
                        or (dt.month == 1 and dt.day == 1)
                    ):
                        if 0 <= dt.hour < 6:
                            inner_index = 4
                        elif 6 <= dt.hour < 12:
                            inner_index = 5
                        elif 12 <= dt.hour < 18:
                            inner_index = 6
                        elif 18 <= dt.hour < 24:
                            inner_index = 7
                    all_counts[month_index][inner_index] += 1
                    all_active[month_index][inner_index].add(dt.day)
            day_counts = [[0] * 8 for _ in range(5)]
            for index1, month_count in enumerate(all_active):
                for index2, count in enumerate(month_count):
                    day_counts[index1][index2] = len(count)
            all_students.append(day_counts)
        print(file_name, num)
    # print(sum(sum(row) for row in all_counts))
    new_counts = [[0] * 8 for _ in range(5)]
    # 计算平均值
    for index1, month_count in enumerate(all_counts):
        for index2, count in enumerate(month_count):
            if index2 <= 3:
                average = count / day_count[index1][0]
            else:
                average = count / day_count[index1][1]
            new_counts[index1][index2] = average
    # 保存为JSON文件
    save_to_json(
        all_counts,
        f"data/temporary/time/time_average_submit.json",
    )
    save_to_json(
        all_students,
        f"data/temporary/time/all_students_active.json",
    )


def caculate_active():
    with open("data/temporary/time/all_students_active.json", "r") as f:
        all_students_active = json.load(f)
    day_count = [[20, 10], [17, 14], [22, 8], [21, 10], [18, 7]]
    # 初始化结果列表
    result = [[0] * 8 for _ in range(5)]
    # 确定大列表和中列表的大小
    num_middle_lists = len(all_students_active)
    # 遍历每个小列表的索引
    for i in range(5):
        for j in range(8):
            # 对每个大列表中的中列表进行累加
            result[i][j] = sum(
                all_students_active[k][i][j] for k in range(num_middle_lists)
            )
            result[i][j] = result[i][j] / 1364
            if j <= 3:
                result[i][j] = result[i][j] / day_count[i][0]
            else:
                result[i][j] = result[i][j] / day_count[i][1]

    save_to_json(
        result,
        f"data/temporary/time/all_students_active_result.json",
    )


# caculate_day()
time_total_submit()
# caculate_active()
