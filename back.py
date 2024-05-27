from flask import Flask, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import re
import json
import logging
from collections import Counter


app = Flask(__name__)
# 允许跨域传输数据
CORS(app)


def read_json(f_name):
    f = open(f_name, "r")
    content = f.read()
    f.close()
    return json.loads(content)


@app.route("/back")
def hello():
    return "Hello, World!"


@app.route("/basicInfo", methods=["GET", "POST"])
def basicInfo():
    # 后续需要根据班级获取不同班的数据
    id = request.json.get("data")  # post
    # id = request.args.get('data')  # 用于get
    # print('--------------------------------------', id)
    file_temp = "./data/classes/basic_info/basic_info_"
    file = file_temp + str(id) + ".csv"
    # file = file_temp + "1.csv"

    data = pd.read_csv(file).sort_values(by="all_knowledge", ascending=False)
    result_each = []  # 每个学生分别的信息
    result_all = []  # 总的信息，比如每个专业的人数
    if id != "all":
        for index, row in data.iterrows():
            result_each.append(
                [
                    row["student_ID"],
                    row["major"],
                    row["age"],
                    row["sex"],
                    row["all_knowledge"],
                    "class1",
                ]
            )
    else:
        store_file = "./data/classes/basic_info/basic_info_all.csv"
        s = pd.read_csv(store_file)["all_knowledge"]
        # 获取30%和70%分位数对应的具体数值,实际上对应我需要的70%和30%
        percentiles = s.quantile([0.3, 0.7])
        # print(percentiles[0.3])
        # 分班级
        master_file = "./data/classes/basic_info/basic_info_"
        for i in range(1, 16):
            master_file_class = pd.read_csv(master_file + str(i) + ".csv")
            # print(master_file_class['all_knowledge'].mean(numeric_only=True))
            high = 0
            mid = 0
            low = 0
            for index, value in master_file_class["all_knowledge"].items():
                if value > percentiles[0.7]:
                    high = high + 1
                elif value <= percentiles[0.3]:
                    low = low + 1
                else:
                    mid = mid + 1
            result_each.append(
                [
                    "class" + str(i),
                    master_file_class["all_knowledge"].mean(
                        numeric_only=True).round(4),
                    [high, mid, low],
                ]
            )
        result_each = sorted(result_each, key=lambda x: x[1], reverse=True)
        result_each = [[x[0], str(x[1]), x[2]] for x in result_each]
        # print(result_each)

    # result_all.append([data['major'].value_counts().sort_index().index.tolist(),
    #                    data['major'].value_counts().sort_index().values.tolist()])
    # result_all.append([data['age'].value_counts().sort_index().index.tolist(),
    #                    data['age'].value_counts().sort_index().values.tolist()])
    # result_all.append([data['sex'].value_counts().sort_index().index.tolist(),
    #                    data['sex'].value_counts().sort_index().values.tolist()])

    for string in ["major", "age", "sex"]:
        temp = data[string].value_counts().sort_index()
        li = []
        for index, value in temp.items():
            li.append({"value": value, "name": index})
        result_all.append(li)

    result = [result_all, result_each]
    return result


# 题目掌握程度


@app.route("/titleMasterInfo", methods=["GET", "POST"])
def titleMasterInfo():
    id = request.json.get("data")  # post

    master_file = "./data/classes/title_master/student_master_title_" + \
        str(id) + ".csv"
    score_file = (
        "./data/classes/title_score_rate/student_master_title_" +
        str(id) + ".csv"
    )
    correct_file = "./data/classes/correct_rate/correct_rate_class_" + \
        str(id) + ".csv"

    master_info = pd.read_csv(master_file).mean(numeric_only=True).round(4)
    score_info = pd.read_csv(score_file).mean(numeric_only=True).round(4)
    correct_info = pd.read_csv(correct_file).mean(numeric_only=True).round(4)
    re = []
    re.append(
        {
            "name": "掌握程度",
            "data": list(master_info.values),
            "type": "line",
            "smooth": "true",
        }
    )
    re.append(
        {
            "name": "得分率",
            "data": list(score_info.values),
            "type": "line",
            "smooth": "true",
        }
    )
    re.append(
        {
            "name": "正确占比",
            "data": list(correct_info.values),
            "type": "line",
            "smooth": "true",
        }
    )
    # print(re)
    return re


# 题目用时和内存分布


@app.route("/titleTimeMemoryInfo", methods=["GET", "POST"])
def titleTimeMemoryInfo():
    id = request.json.get("data")  # post 这里应该获取到两个信息，班级和题目
    # print(data)  # prin
    data = request.json.get("name")  # post 这里应该获取到两个信息，班级和题目

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
    # id = 1
    # title = 'Question_3MwAFlmNO8EKrpY5zjUd'

    time_file = "./data/classes/time_count/class_" + str(id) + ".json"
    memory_file = "./data/classes/memory_count/class_" + str(id) + ".json"

    memory_data = read_json(memory_file)
    time_data = read_json(time_file)

    re = {}
    time_dic = dict(
        sorted(time_data[title].items(),
               key=lambda d: float(d[0]), reverse=False)
    )
    memory_dic = dict(
        sorted(memory_data[title].items(),
               key=lambda d: float(d[0]), reverse=False)
    )
    re["time"] = {"keys": list(time_dic.keys()),
                  "value": list(time_dic.values())}
    re["memory"] = {"keys": list(memory_dic.keys()),
                    "value": list(memory_dic.values())}

    return re


# 知识点


@app.route("/knowledgeMasterInfo", methods=["GET", "POST"])
def knowledgeMasterInfo():
    id = request.json.get("data")  # post
    title_value = request.json.get("title")

    # file = "./data/knowledge/Data_TitleInfo.csv"
    # title = pd.read_csv(file)
    # re = []
    # knowledge_group = title.groupby("knowledge")
    # for knowledge in knowledge_group:
    #     print(knowledge[0])
    #     re.append({"name": knowledge[0], "children": []})
    #     sub_knowledge_group = knowledge[1].groupby("sub_knowledge")
    #     for sub_knowledge in sub_knowledge_group:
    #         # re[-1]表示该列表最后一个元素
    #         re[-1]["children"].append({"name": sub_knowledge[0], "children": []})
    #         for index, row in sub_knowledge[1].iterrows():
    #             # print(row)
    #             re[-1]["children"][-1]["children"].append(
    #                 {"name": row["title_ID"], "value": row["score"]}
    #             )

    df_knowledge = pd.DataFrame()
    df_sub_knowledge = pd.DataFrame()
    df_title = pd.DataFrame()

    store_file1 = "./data/knowledge/knowledge/student_master_knowledge_"
    store_file2 = "./data/knowledge/sub_knowledge/student_master_sub_knowledge_"
    store_file3 = "./data/knowledge/title_master/student_master_title_"

    store_title_score = "./data/classes/correct_rate/correct_rate_class_"

    if id == "all":
        for i in range(1, 15):
            knowledge = pd.read_csv(store_file1 + str(i + 1) + ".csv")
            df_knowledge = pd.concat(
                [df_knowledge, knowledge], ignore_index=True)

            sub_knowledge = pd.read_csv(store_file2 + str(i + 1) + ".csv")
            df_sub_knowledge = pd.concat(
                [df_sub_knowledge, sub_knowledge], ignore_index=True
            )

            # 题目得分率
            if title_value == "score":
                title = pd.read_csv(store_title_score + str(i + 1) + ".csv")
                df_title = pd.concat([df_title, title], ignore_index=True)
            # 题目掌握程度
            else:
                title = pd.read_csv(store_file3 + str(i + 1) + ".csv")
                df_title = pd.concat([df_title, title], ignore_index=True)
    else:
        knowledge = pd.read_csv(store_file1 + id + ".csv")
        df_knowledge = pd.concat([df_knowledge, knowledge], ignore_index=True)

        sub_knowledge = pd.read_csv(store_file2 + id + ".csv")
        df_sub_knowledge = pd.concat(
            [df_sub_knowledge, sub_knowledge], ignore_index=True
        )

        # 题目得分率
        if title_value == "score":
            title = pd.read_csv(store_title_score + id + ".csv")
            df_title = pd.concat([df_title, title], ignore_index=True)
        else:
            title = pd.read_csv(store_file3 + id + ".csv")
            df_title = pd.concat([df_title, title], ignore_index=True)

    knowledge_mean = df_knowledge.mean(numeric_only=True).round(4)

    sub_knowledge_mean = df_sub_knowledge.mean(numeric_only=True).round(4)

    title_mean = df_title.mean(numeric_only=True).round(4)
    icon = {
        "Question_q7OpB2zCMmW9wS8uNt3H": 0,
        "Question_QRm48lXxzdP7Tn1WgNOf": 1,
        "Question_pVKXjZn0BkSwYcsa7C31": 2,
        "Question_lU2wvHSZq7m43xiVroBc": 3,
        "Question_x2Fy7rZ3SwYl9jMQkpOD": 4,
        "Question_oCjnFLbIs4Uxwek9rBpu": 5,
    }

    file = "./data/knowledge/Data_TitleInfo.csv"
    title = pd.read_csv(file)
    re = []
    knowledge_group = title.groupby("knowledge")
    for knowledge in knowledge_group:
        # print(knowledge[0])
        re.append(
            {
                "name": knowledge[0],
                "score": knowledge_mean[knowledge[0]],
                "children": [],
            }
        )
        sub_knowledge_group = knowledge[1].groupby("sub_knowledge")
        for sub_knowledge in sub_knowledge_group:
            # re[-1]表示该列表最后一个元素
            re[-1]["children"].append(
                {
                    "name": sub_knowledge[0],
                    "score": sub_knowledge_mean[sub_knowledge[0]],
                    "children": [],
                }
            )
            for index, row in sub_knowledge[1].iterrows():
                # print(row)
                if row["title_ID"] in icon.keys():
                    re[-1]["children"][-1]["children"].append(
                        {
                            "name": row["title_ID"],
                            "score": title_mean[row["title_ID"]],
                            "value": row["score"],
                            "icon": icon[row["title_ID"]],
                        }
                    )
                else:
                    re[-1]["children"][-1]["children"].append(
                        {
                            "name": row["title_ID"],
                            "score": title_mean[row["title_ID"]],
                            "value": row["score"],
                        }
                    )
    # print(re)
    reInfo = {"name": "Q1", "children": re}
    return reInfo


# 学习日历图


@app.route("/learnCalendarInfo", methods=["GET", "POST"])
def learnCalendarInfo():
    ids = request.json.get("data")  # 学生id列表
    month = request.json.get("month")
    language = [
        "Method_Cj9Ya2R7fZd6xs1q5mNQ",
        "Method_gj1NLb4Jn7URf9K2kQPd",
        "Method_5Q4KoXthUuYz3bvrTDFm",
        "Method_m8vwGkEZc3TSW2xqYUoR",
        "Method_BXr9AIsPQhwNvyGdZL57",
    ]

    file = "./data/detail/aaa.csv"
    df = pd.read_csv(file)
    students = df[df["student_ID"].isin(ids)]
    students_m = students[students["month"] == month]

    re = {}
    # print(students_m)
    stu_group = students_m.groupby("student_ID")
    for g in stu_group:
        re[g[0]] = {}
        sort_g = g[1].sort_values("date")
        date_g = sort_g.groupby("date")
        for date in date_g:
            re[g[0]][str(date[0])] = []
            # 正确率
            result_status = date[1]["state"].value_counts(normalize=True)
            correct_rate = 0
            if "Absolutely_Correct" in result_status.index:
                correct_rate = correct_rate + \
                    result_status["Absolutely_Correct"]
            if "Partially_Correct" in result_status.index:
                correct_rate = correct_rate + \
                    result_status["Partially_Correct"]
            re[g[0]][str(date[0])].append(correct_rate)
            # 答题数
            title_num = len(date[1]["title_ID"].value_counts().index)
            re[g[0]][str(date[0])].append(title_num)
            # 语言
            all_counts = len(date[1])  # 总提交次数

            temp = []
            all_language = date[1].value_counts("method")
            for lan in language:
                # 判断语言是否存在
                if lan in all_language.index:
                    temp.append(all_language[lan] / all_counts)
                else:
                    temp.append(0)
            re[g[0]][str(date[0])].append(temp)

            # 提交次数
            re[g[0]][str(date[0])].append(all_counts)

        # print(sort_g)
    # print(re)
    return re


# 个人提交图


@app.route("/personalSubmitInfo", methods=["GET", "POST"])
def personalSubmitInfo():
    student_id = request.json.get("data")  # 学生id列表
    learning_date = request.json.get("date")
    # 用时分布
    title_timeconsume_count = read_json(
        "./data/detail/title_timeconsume_count.json")
    # 内存分布
    title_memory_count = read_json("./data/detail/title_memory_count.json")

    file = "./data/detail/aaa.csv"
    df = pd.read_csv(file)
    info = df[(df["student_ID"] == student_id) & (df["date"] == learning_date)]
    # print(info)
    title_g = info.groupby("title_ID")
    re = {}
    # 按题目分组
    for g in title_g:
        re["Q_" + g[0][9:12]] = []
        sort_g = g[1].sort_values("time")
        # print('------------', '\n', sort_g)
        # 对每次提交依次处理
        for index, row in sort_g.iterrows():
            re["Q_" + g[0][9:12]].append([])
            answer_state = row["state"]
            # 完全正确的用时内存分布
            if answer_state == "Absolutely_Correct":
                total_correct_count = sum(
                    title_timeconsume_count[g[0]].values())
                # 用时
                temp_sum = 0
                for key in title_timeconsume_count[g[0]].keys():
                    if int(float(key)) <= int(row["timeconsume"]):
                        temp_sum = temp_sum + \
                            title_timeconsume_count[g[0]][key]
                timeconsume_rank_temp = temp_sum / total_correct_count
                re["Q_" + g[0][9:12]][-1].append(timeconsume_rank_temp)

                temp_sum = 0
                # 内存
                for key in title_memory_count[g[0]].keys():
                    if int(key) <= int(row["memory"]):
                        temp_sum = temp_sum + title_memory_count[g[0]][key]
                memory_rank_temp = temp_sum / total_correct_count
                re["Q_" + g[0][9:12]][-1].append(memory_rank_temp)
            else:
                re["Q_" + g[0][9:12]][-1].append(1)
                re["Q_" + g[0][9:12]][-1].append(1)

            # 答题状态
            re["Q_" + g[0][9:12]][-1].append(answer_state)
            # 方法
            re["Q_" + g[0][9:12]][-1].append(row["method"][0:8])
            # 提交时间
            re["Q_" + g[0][9:12]][-1].append(row["time"])

    # print(re)
    return re


@app.route("/featureStatisticsInfo", methods=["GET", "POST"])
def featureStatisticsInfo():
    # 输入：month,10月修改顺序
    month = request.json.get("data")
    month_to = {9: 0, 10: 1, 11: 2, 12: 3, 1: 4}
    # 特征：提交次数、活跃天数、正确占比、题目数
    feature = read_json("./data/cluster/month_student_feature_new.json")[
        month_to[month]
    ]
    tags = read_json("data/cluster/cluster_label" + str(month) + ".json")

    result = {0: [], 1: [], 2: []}
    for i in range(len(tags)):
        result[tags[i]].append(feature[i])

    # 其他月的分类：针对、多样、尝试
    feature_name = ["提交次数", "活跃天数", "正确占比", "答题数"]
    # print(result)

    mid_re = {}
    for key in result.keys():
        mid_re[key] = {}
        for i in range(len(feature_name)):
            mid_re[key][feature_name[i]] = [row[i] for row in result[key]]
    # print(mid_re)

    final_re = {}
    for i in feature_name:
        final_re[i] = []
        # 十月的标签顺序需要修改
        if month == 10:
            for key in [2, 1, 0]:
                final_re[i].append(mid_re[key][i])
        # 不是十月
        else:
            for key in mid_re.keys():
                final_re[i].append(mid_re[key][i])
    # print(final_re)
    new_final_re = {}
    for key, value in final_re.items():
        new_final_re[key] = []
        for data in value:
            new_final_re[key].append([min(data), np.percentile(
                data, 25), np.median(data), np.percentile(data, 75), max(data)])
    return new_final_re


@app.route("/allPeriodInfo", methods=["GET", "POST"])
def allPeriodInfo():
    total_student = 1364
    features = read_json("./data/cluster/time_cluster_original_feature.json")

    label = []
    for month in [9, 10, 11, 12, 1]:
        # 工作日、休息日
        for weekday in [1, 0]:
            # 时间段
            for period in ["Dawn", "Morning", "Afternoon", "Evening"]:
                key = str(month) + "-" + str(weekday) + "-" + period
                label.append(key)

    result = {}

    # 时间段
    pattern1 = r"\d+-([A-Za-z]+)"
    # 月份
    pattern2 = r"(\d+)"
    for i in range(len(features)):
        period = re.search(pattern1, label[i]).group(0)
        month = re.search(pattern2, label[i]).group(0)
        if period not in result:
            result[period] = {}

        result[period][int(month)] = [
            features[i][0] * total_student,
            features[i][1] * total_student,
            features[i][-1],
        ]
    # print(result)

    final_re = {}
    to_1 = {"0": "休息日", "1": "工作日"}
    to_2 = {"Dawn": "凌晨", "Morning": "上午", "Afternoon": "下午", "Evening": "晚上"}
    for key, value in result.items():
        key_list = key.split("-")
        final_re[to_2[key_list[1]] + "-" + to_1[key_list[0]]] = value
    # print(final_re)
    return final_re


@app.route("/onePeriodInfo", methods=["GET", "POST"])
def onePeriodInfo():

    # 传入数据month,is_weekday,period
    month = request.json.get("month")
    is_weekday = request.json.get("is_weekday")
    period = request.json.get("period")

    df = pd.read_csv('./data/detail/aaa.csv')
    tags = read_json('./data/cluster/student_tag_dict'+str(month)+'.json')

    data = df[(df['month'] == month) & (df['time_period'] == period)
              & (df['is_weekday'] == is_weekday)].sort_values('date')

    date_group = data.groupby('date')
    # 根据日期进行分组，
    result = {}
    for g in date_group:
        # 类型依次是针对、多样、尝试，012
        # 十月标签顺序不一样要修改210
        stu_group = g[1].groupby('student_ID')
        sum_li = [0, 0, 0]
        for student in stu_group:
            if (month == 10):
                tag = abs(tags[student[0]]-2)
                sum_li[tag] = sum_li[tag]+1
            else:
                tag = tags[student[0]]
                sum_li[tag] = sum_li[tag]+1
        result[g[0]] = sum_li
    # print(result)
    return (result)

# 时间模式下，右下3图，对学生分类后的分析


@app.route("/timeStudentInfo", methods=["GET", "POST"])
def timeStudentInfo():
    feature = request.json.get("data")

    # feature = '活跃天数'
    feature_to = {'提交次数': 0, '活跃天数': 1, '题目数': 2}
    feature_label = feature_to[feature]
    data = read_json('./data/detail/time_cluster_student_analysis.json')
    result = {}
    for key, value in data.items():
        result[key] = []
        for stu in ['top', 'mid', 'low']:
            result[key].append(value[stu][feature_label])

    result2 = {'top': [
        result['高峰型'][0],
        result['平均型'][0],
        result['低峰型'][0]
    ],
        'mid': [
        result['高峰型'][1],
        result['平均型'][1],
        result['低峰型'][1]
    ],
        'low': [
        result['高峰型'][2],
        result['平均型'][2],
        result['低峰型'][2]
    ]}

    return ([result, result2])

# 协助获取聚类所需的坐标数据以及对应的标签数据


def group_cluster_data(file_path1, file_path2, num=0):
    with open(file_path1, "r") as f:
        cluster_features = json.load(f)
    with open(file_path2, "r") as f:
        cluster_label = json.load(f)
    grouped_data = [[], [], []]
    # 将坐标与标签对应起来
    for index, features in enumerate(cluster_features):
        if num != -1:
            if cluster_label[index] == 0:
                if num == 10:
                    features["label"] = "尝试型"
                else:
                    features["label"] = "针对型"
            elif cluster_label[index] == 1:
                features["label"] = "多样型"
            elif cluster_label[index] == 2:
                if num == 10:
                    features["label"] = "针对型"
                else:
                    features["label"] = "尝试型"
        grouped_data[cluster_label[index]].append(features)
    # 10是特殊情况
    if num == 10:
        # 交换第一个元素和第三个元素的位置
        grouped_data[0], grouped_data[2] = grouped_data[2], grouped_data[0]
    return grouped_data


# 聚类数据
@app.route("/clusterData")
def cluster_data():
    feature_path9 = "data/cluster/student_more_info9.json"
    label_path9 = "data/cluster/cluster_label9.json"
    feature_path10 = "data/cluster/student_more_info10.json"
    label_path10 = "data/cluster/cluster_label10.json"
    feature_path11 = "data/cluster/student_more_info11.json"
    label_path11 = "data/cluster/cluster_label11.json"
    feature_path12 = "data/cluster/student_more_info12.json"
    label_path12 = "data/cluster/cluster_label12.json"
    feature_path1 = "data/cluster/student_more_info1.json"
    label_path1 = "data/cluster/cluster_label1.json"
    time_feature_path = "data/cluster/time_cluster_features.json"
    time_label_path = "data/cluster/time_cluster_label.json"
    a = group_cluster_data(feature_path9, label_path9)
    b = group_cluster_data(feature_path10, label_path10, 10)
    c = group_cluster_data(feature_path11, label_path11)
    d = group_cluster_data(feature_path12, label_path12)
    e = group_cluster_data(feature_path1, label_path1)
    f = group_cluster_data(time_feature_path, time_label_path, -1)
    merged_data = [a, b, c, d, e, f]
    return merged_data


# 相关性系数列表
@app.route("/correlationData")
def correlation_data():
    data_list = [
        [
            [0, 0, 0.139],
            [0, 1, 0.345],
            [0, 2, 0.183],
            [1, 0, 0.05],
            [1, 1, -0.504],
            [1, 2, 0.088],
            [2, 0, 0.258],
            [2, 1, 0.352],
            [2, 2, 0.443],
            [3, 0, 0.755],
            [3, 1, 0.694],
            [3, 2, 0.597],
        ],
        [
            [0, 0, -0.189],
            [0, 1, 0.378],
            [0, 2, -0.178],
            [1, 0, 0.133],
            [1, 1, -0.480],
            [1, 2, 0.100],
            [2, 0, 0.321],
            [2, 1, 0.148],
            [2, 2, 0.416],
            [3, 0, 0.702],
            [3, 1, 0.742],
            [3, 2, 0.594],
        ],
        [
            [0, 0, -0.051],
            [0, 1, 0.388],
            [0, 2, -0.227],
            [1, 0, -0.157],
            [1, 1, -0.303],
            [1, 2, 0.047],
            [2, 0, 0.096],
            [2, 1, 0.107],
            [2, 2, 0.323],
            [3, 0, 0.616],
            [3, 1, 0.777],
            [3, 2, 0.569],
        ],
        [
            [0, 0, 0.031],
            [0, 1, 0.472],
            [0, 2, -0.248],
            [1, 0, -0.409],
            [1, 1, -0.319],
            [1, 2, -0.046],
            [2, 0, 0.022],
            [2, 1, 0.462],
            [2, 2, 0.457],
            [3, 0, 0.585],
            [3, 1, 0.623],
            [3, 2, 0.536],
        ],
        [
            [0, 0, 0.039],
            [0, 1, 0.885],
            [0, 2, -0.131],
            [1, 0, -0.142],
            [1, 1, -0.854],
            [1, 2, -0.664],
            [2, 0, 0.040],
            [2, 1, 0.798],
            [2, 2, 0.160],
            [3, 0, 0.825],
            [3, 1, 0.936],
            [3, 2, 0.340],
        ],
    ]
    return data_list


@app.route("/transferData", methods=["GET", "POST"])
# 计算模式转移的数量
def get_mode_shift_data():
    # 拿到前端传递的参数
    month1 = request.args.get("pre_month")
    month2 = request.args.get("bk_month")
    # 根据月份读取数据
    with open(f"data/cluster/student_tag_dict{month1}.json", "r") as f:
        left_dict = json.load(f)
    with open(f"data/cluster/student_tag_dict{month2}.json", "r") as f:
        right_dict = json.load(f)
    # 计算每个每个模式的学生数量
    # left_value_counter = Counter(left_dict.values())
    right_value_counter = Counter(right_dict.values())
    # 将 Counter 对象的值转换为列表
    # left_values_list = list(left_value_counter.values())
    right_values_list = list(right_value_counter.values())
    transfer_matrix = [[0 for _ in range(4)] for _ in range(4)]
    for student_id, tag in left_dict.items():
        if tag != right_dict[student_id]:
            transfer_matrix[tag][right_dict[student_id]] += 1
    return [right_values_list, transfer_matrix]


if __name__ == "__main__":
    app.run(debug=True)
    app.logger.setLevel(logging.DEBUG)
