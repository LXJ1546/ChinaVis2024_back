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
app.config["GREETING"] = "Hello, World!"
# app.config['corr'] = []


def read_json(f_name):
    f = open(f_name, "r")
    content = f.read()
    f.close()
    return json.loads(content)


def write_dict_to_json(file_path, data):
    # 将字典写入 JSON 文件
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


@app.route("/back")
def hello():
    app.config["GREETING"] = "111"
    return app.config["GREETING"]


@app.route("/back1")
def hello1():
    return app.config["GREETING"]


# 学生对题目掌握程度
def get_student_master_title(case, f_name, f_store, w):
    """
    case:表示计算掌握程度还是公式
    f_name:进行处理的文件
    f_store:处理结果的保存路径
    注意：后续可能还需要将掌握程度的权重也作为参数进行传递
    """
    f = open(f_name, "r")
    content = f.read()
    a = json.loads(content)
    f.close()

    # 读取题目用时、内存分布情况
    f = open("data/detail/title_timeconsume_count.json", "r")
    content = f.read()
    title_timeconsume_count = json.loads(content)
    f.close()
    f = open("data/detail/title_memory_count.json", "r")
    content = f.read()
    title_memory_count = json.loads(content)
    f.close()

    re = {}
    # 计算得分率
    if case == "score":
        # 遍历学生
        for student in a.keys():
            # print(key)
            re[student] = {}
            for title in a[student].keys():
                # 读取a[student][title]是一个题目列表
                score_rate = []  # 储存得分率
                # 遍历题目列表
                for item in a[student][title]:
                    # item:[1704206906, 'Class1', 'Absolutely_Error', 0, 'Method_m8vwGkEZc3TSW2xqYUoR', 320, '2', 3, "['b3C9s,b3C9s_l4z6od7y']"]
                    # 计算得分率使用这个
                    score_rate.append(item[3] / item[7])
                score_rate_avg = sum(score_rate) / len(score_rate)
                # 计算得分率
                re[student][title] = score_rate_avg

    # 否则，就是计算掌握程度
    else:
        # 遍历学生
        for student in a.keys():
            # print(key)
            re[student] = {}
            for title in a[student].keys():
                # 读取a[student][title]是一个题目列表
                score_rate = []  # 储存得分率
                state_list = []  # 存储学生的答题状态，用以计算正确占比和错误占比
                memory_rank = 1  # 内存和用时没有完全正确的情况就设为1
                timeconsume_rank = 1
                memory_timeconsume_rank_candidata = (
                    []
                )  # 记录正确情况下，用时和内存使用的候选，因为可能有多次完全正确

                # 遍历题目列表
                for item in a[student][title]:
                    # item:[1704206906, 'Class1', 'Absolutely_Error', 0, 'Method_m8vwGkEZc3TSW2xqYUoR', 320, '2', 3, "['b3C9s,b3C9s_l4z6od7y']"]
                    # 计算掌握程度使用这个
                    if item[2] == "Absolutely_Correct" or "Partially_Correct":
                        score_rate.append(item[3] / item[7])

                    # 答题状态
                    state_list.append(item[2])
                    # 用时和内存如何衡量,只有在完全正确的情况下考虑

                    if item[2] == "Absolutely_Correct":
                        total_correct_count = sum(
                            title_timeconsume_count[title].values()
                        )
                        # memory
                        # 遍历title_timeconsume_count，计算占比前百分之多少
                        temp_sum = 0
                        for key in title_timeconsume_count[title].keys():
                            if int(float(key)) <= int(item[6]):
                                temp_sum = (
                                    temp_sum + title_timeconsume_count[title][key]
                                )
                        timeconsume_rank_temp = temp_sum / total_correct_count

                        # 遍历title_memory_count，计算占比前百分之多少
                        temp_sum = 0
                        for key in title_memory_count[title].keys():
                            if int(key) <= item[5]:
                                temp_sum = temp_sum + title_memory_count[title][key]
                        memory_rank_temp = temp_sum / total_correct_count
                        memory_timeconsume_rank_candidata.append(
                            [memory_rank_temp, timeconsume_rank_temp]
                        )

                # 从memory_timeconsume_rank_candidata中获取最优的那一次
                if len(memory_timeconsume_rank_candidata) > 0:
                    flag = float("inf")
                    flag_index = 0
                    for i in range(len(memory_timeconsume_rank_candidata)):
                        if sum(memory_timeconsume_rank_candidata[i]) < flag:
                            flag = sum(memory_timeconsume_rank_candidata[i])
                            flag_index = i
                    memory_rank = memory_timeconsume_rank_candidata[flag_index][0]
                    timeconsume_rank = memory_timeconsume_rank_candidata[flag_index][1]

                score_rate_avg = sum(score_rate) / len(score_rate)
                # 错误占比
                error_count = 0
                for n in state_list:
                    if "Error" in n:
                        error_count = error_count + 1
                error_rate = error_count / len(state_list)
                # 正确和部分正确占比
                correct_rate = 1 - error_rate

                # # 新版本
                re[student][title] = (
                    w["w1"] * score_rate_avg
                    + w["w2"] * correct_rate
                    + w["w3"] * (1 - memory_rank)
                    + w["w4"] * (1 - timeconsume_rank)
                )

    # 将字典转换为 DataFrame
    df = pd.DataFrame.from_dict(re, orient="index")

    # 缺失值填充为!!!!!!!!!!!!!!!!!!!!!!
    df = df.fillna("null")
    df.to_csv(f_store, index=True)
    return df


# 分班级计算所有学生对题目的掌握程度


def get_all_class_master_title(case, w):

    # 所有班级，直接合并分班的数据
    df = pd.DataFrame()

    # 分班级计算掌握程度和得分率
    file = "data/classes/origin_data/student_title_group"
    if case == "score":
        store = "F:/vscode/vis24/data/datap/DataPro_class/title_score_rate/student_master_title_"
    else:
        store = "data/classes/title_master/student_master_title_"
    for i in range(1, 16):
        # print(i)
        f = file + str(i) + ".json"
        store_f = store + str(i) + ".csv"
        result = get_student_master_title(case, f, store_f, w)
        df = pd.concat([df, result])
    df.to_csv("data/classes/title_master/student_master_title_all.csv")

    # 分月份计算每个人的掌握程度
    file = "data/classes/month_origin_data/student_title_group"
    if case == "score":
        pass
        # store = 'F:/vscode/vis24/data/datap/DataPro_class/title_score_rate/student_master_title_'
    else:
        store = "data/classes/month_data/student_master_title_"
    for i in [9, 10, 11, 12, 1]:
        print(i)
        f = file + str(i) + ".json"
        store_f = store + str(i) + ".csv"
        get_student_master_title(case, f, store_f, w)


# 计算对总的知识点的掌握程度


def get_student_master_all_knowledge_new(df):
    # 所有知识点总分
    knowledge_score = 115
    origin_df = df.copy(deep=True)

    # 将取值为字符串 'null' 的元素替换为数值 0
    df.replace("null", 0, inplace=True)
    # print(df)
    # b3C9s 10
    # g7R2j 15
    # k4W1c 3
    # m3D1v 36
    # r8S3g 5
    # s8Y2f 3
    # t5V9e 10
    # y9W5d 33

    origin_df["all_knowledge"] = (
        10 / knowledge_score * df["b3C9s"]
        + 15 / knowledge_score * df["g7R2j"]
        + 3 / knowledge_score * df["k4W1c"]
        + 36 / knowledge_score * df["m3D1v"]
        + 5 / knowledge_score * df["r8S3g"]
        + 3 / knowledge_score * df["s8Y2f"]
        + 10 / knowledge_score * df["t5V9e"]
        + 33 / knowledge_score * df["y9W5d"]
    )

    return origin_df


# 根据学生对题目的掌握程度计算每个学生对不同知识点的掌握程度


def get_student_master_knowledge(param):
    # 主要参数，学生掌握题表，知识点到题目映射表，保存路径

    file = param["student_master_title"]

    # knowledge_to_title_file = 'F:/vscode/vis24/data/datap/knowledge_to_title.json'
    knowledge_to_title_file = param["knowledge_to_title_file"]
    df = pd.read_csv(file, low_memory=False)
    f = open(knowledge_to_title_file, "r")
    content = f.read()
    knowledge_to_title = json.loads(content)
    f.close()

    dict_student_master_knowledge = {}
    # 依次遍历每一个学生
    for index, row in df.iterrows():
        dict_student_master_knowledge[row[0]] = {}
        # 依次遍历每一个知识点
        for knowledge in knowledge_to_title.keys():
            # 获取一个知识点对应的多个题目的题目列表
            title_list = knowledge_to_title[knowledge].keys()
            # 计算knowledge对应的题目总分
            total_score = sum(knowledge_to_title[knowledge].values())
            # print(total_score)
            master_rate = 0
            flag = True  # 用于标识学生当前知识点是否没有做,先默认为没做
            # 依次遍历一个知识点对应的题目
            for title in title_list:
                title = title.strip()
                # row[title]是该题目得分，只当掌握程度不为null时计算
                if not pd.isna(row[title]):
                    flag = False
                    master_rate = (
                        master_rate
                        + knowledge_to_title[knowledge][title]
                        / total_score
                        * row[title]
                    )
            if not flag:
                dict_student_master_knowledge[row[0]][knowledge] = master_rate
    # print(dict_student_master_knowledge)
    # 将字典转换为 DataFrame
    df = pd.DataFrame.from_dict(dict_student_master_knowledge, orient="index")
    # 缺失值填充为
    df = df.fillna("null")
    # file_path = './datap/temp_student_master_knowledge_all.csv'
    # 如果是主知识点，就再添加一列，表示学生的所有知识点总的掌握程度
    if param["case"] == "knowledge":
        df = get_student_master_all_knowledge_new(df)
    file_path = param["result_file"]
    df.to_csv(file_path, index=True)
    return df


# 分月计算学生对知识点的掌握程度时，只考虑当月做过的题，总知识点的掌握情况也只根据当月做过的知识点
def get_student_master_knowledge_month(param):
    # 根据学生对题目的掌握程度计算每个学生对不同知识点的掌握程度
    # 主要参数，学生掌握题表，知识点到题目映射表，保存路径

    def get_student_master_all_knowledge_month_new(row):
        all_knowledge = {
            "b3C9s": 10,
            "g7R2j": 15,
            "k4W1c": 3,
            "m3D1v": 36,
            "r8S3g": 5,
            "s8Y2f": 3,
            "t5V9e": 10,
            "y9W5d": 33,
        }

        # 保存做过的知识点
        done_knowledge = {}
        for k in all_knowledge.keys():
            # 做过
            if row[k] != "null":
                done_knowledge[k] = all_knowledge[k]
        # print(done_knowledge)
        master = 0
        for k in done_knowledge.keys():
            master = master + row[k] * done_knowledge[k] / sum(done_knowledge.values())
        return master

    file = param["student_master_title"]

    # knowledge_to_title_file = 'F:/vscode/vis24/data/datap/knowledge_to_title.json'
    knowledge_to_title_file = param["knowledge_to_title_file"]
    df = pd.read_csv(file, low_memory=False)
    f = open(knowledge_to_title_file, "r")
    content = f.read()
    knowledge_to_title = json.loads(content)
    f.close()

    dict_student_master_knowledge = {}
    # 依次遍历每一个学生
    for index, row in df.iterrows():
        dict_student_master_knowledge[row[0]] = {}
        # 依次遍历每一个知识点
        for knowledge in knowledge_to_title.keys():
            # 获取一个知识点对应的多个题目的题目列表
            title_list = knowledge_to_title[knowledge].keys()
            # 计算knowledge对应的题目总分，分月时，只考虑做过的题的总分
            # total_score = sum(knowledge_to_title[knowledge].values())

            done_title = {}
            for title in title_list:
                title = title.strip()
                # 做过
                if not pd.isna(row[title]):
                    done_title[title] = knowledge_to_title[knowledge][title]
            # 分月时，只考虑做过的题的总分
            total_score = sum(done_title.values())

            master_rate = 0
            flag = True  # 用于标识学生当前知识点是否没有做,先默认为没做
            # 依次遍历当前知识点对应的题目
            for title in title_list:
                title = title.strip()
                # row[title]是该题目得分，只当掌握程度不为null时计算
                if not pd.isna(row[title]):
                    flag = False
                    master_rate = (
                        master_rate
                        + knowledge_to_title[knowledge][title]
                        / total_score
                        * row[title]
                    )
            if not flag:
                dict_student_master_knowledge[row[0]][knowledge] = master_rate
    # print(dict_student_master_knowledge)
    # 将字典转换为 DataFrame
    df = pd.DataFrame.from_dict(dict_student_master_knowledge, orient="index")
    # 缺失值填充为,表示该知识点没做
    df = df.fillna("null")
    # print(df)
    # 如果是主知识点，就再添加一列，表示学生的所有知识点总的掌握程度
    if param["case"] == "knowledge":
        # df = get_student_master_all_knowledge_month_new(df)
        # 创建空的新列
        df["all_knowledge"] = None
        # 逐行迭代处理DataFrame，并计算新列的值
        for index, row in df.iterrows():
            new_value = get_student_master_all_knowledge_month_new(row)
            df.at[index, "all_knowledge"] = new_value
    # print(df)
    file_path = param["result_file"]
    df.to_csv(file_path, index=True)


def get_all_class_master_knowledge(case):
    # 所有班级，直接合并分班的数据
    df = pd.DataFrame()

    # 分班级计算掌握知识点和子知识点的
    file = "data/classes/title_master/student_master_title_"
    if case == "knowledge":
        store = "data/knowledge/knowledge/student_master_knowledge_"
        store_all = "data/knowledge/knowledge/student_master_knowledge_all.csv"

        knowledge_to_title_file = "data/classes/origin_data/knowledge_to_title.json"
    # 否则就是子知识点
    else:
        store = "data/knowledge/sub_knowledge/student_master_sub_knowledge_"
        store_all = "data/knowledge/sub_knowledge/student_master_sub_knowledge_all.csv"

        knowledge_to_title_file = "data/classes/origin_data/sub_knowledge_to_title.json"
    for i in range(1, 16):
        print(i)
        f = file + str(i) + ".csv"
        store_f = store + str(i) + ".csv"
        # # 分班获取学生对每个知识点的掌握程度
        param = {
            "student_master_title": f,
            "knowledge_to_title_file": knowledge_to_title_file,
            "result_file": store_f,
            "case": case,
        }
        result = get_student_master_knowledge(param)
        df = pd.concat([df, result])
    df.to_csv(store_all)

    # 分月份计算每个人的掌握程度
    file = "data/classes/month_data/student_master_title_"
    if case == "knowledge":
        store = "data/classes/month_data/month_knowledge/student_master_knowledge_"
        knowledge_to_title_file = "data/classes/origin_data/knowledge_to_title.json"
        for i in [9, 10, 11, 12, 1]:
            # for i in [10]:
            print(i)
            f = file + str(i) + ".csv"
            store_f = store + str(i) + ".csv"
            # # 分班获取学生对每个知识点的掌握程度
            param = {
                "student_master_title": f,
                "knowledge_to_title_file": knowledge_to_title_file,
                "result_file": store_f,
                "case": case,
            }
            # get_student_master_knowledge(param)
            get_student_master_knowledge_month(param)


def pro_basicInfo():
    master_file = "data/knowledge/knowledge/student_master_knowledge_"
    basic_file = "data/classes/origin_data/Data_StudentInfo.csv"
    store_file = "./data/classes/basic_info/basic_info_"
    basic_info = pd.read_csv(basic_file)

    # 所有班级，直接合并分班的数据
    df = pd.DataFrame()

    # 分班级
    for i in range(1, 16):
        master_file_class = pd.read_csv(master_file + str(i) + ".csv")
        store_file_class = store_file + str(i) + ".csv"
        result = pd.merge(
            master_file_class, basic_info, left_on="Unnamed: 0", right_on="student_ID"
        )
        # print(result)
        df = pd.concat([df, result], ignore_index=True)
        result.to_csv(store_file_class)
    # df = df.drop('Unnamed: 0.1', axis=1)
    # print(df)
    # 将'top','mid','low'的信息写入aaa.csv

    # 首先根据总知识点掌握情况将学生分为：top/mid/low三类
    data = df.sort_values(by="all_knowledge", ascending=False).reset_index(drop=True)
    top_count = 408
    mid_count = 954
    low_count = 1363
    # 添加'rank'列
    data["rank"] = "low"
    data.loc[:top_count, "rank"] = "top"
    data.loc[top_count + 1 : mid_count, "rank"] = "mid"
    data.to_csv("./data/classes/basic_info/basic_info_all.csv")
    all_df = pd.read_csv("data/detail/aaa.csv")
    all_df = all_df.drop(columns=["Unnamed: 0_x", "Unnamed: 0_y", "rank"])
    # 使用 merge 函数拼接两个 DataFrame 的特定列
    merged_df = pd.merge(
        all_df,
        data[["Unnamed: 0", "rank"]],
        left_on="student_ID",
        right_on="Unnamed: 0",
        how="left",
    )
    merged_df.to_csv("data/detail/aaa.csv")


# 掌握程度衡量权重变化后，top,mid,low的学生可能会变化，因次要重新计算


def pro_timeStudentInfo():
    # # 首先根据总知识点掌握情况将学生分为：top/mid/low三类
    # file = 'data/classes/basic_info/basic_info_all.csv'
    # data = pd.read_csv(file).sort_values(by='all_knowledge',
    #                                      ascending=False).reset_index(drop=True)
    # # 总共1364,分为409，546，409，
    # # print(len(data['all_knowledge']))
    # top = list(data.loc[0:408, 'Unnamed: 0'].values)
    # mid = list(data.loc[409:954, 'Unnamed: 0'].values)
    # low = list(data.loc[955:1363, 'Unnamed: 0'].values)
    # students_to = {'top': top, 'mid': mid, 'low': low}
    # print(len(top)+len(mid)+len(low))

    # 不同的时间段分类三类
    # 每一类对应的时间段
    tag_to_time = {
        0: [
            "10-1-Morning",
            "10-1-Afternoon",
            "10-0-Morning",
            "10-0-Afternoon",
            "11-1-Morning",
            "11-1-Afternoon",
            "11-0-Morning",
            "11-0-Afternoon",
            "12-1-Afternoon",
        ],
        1: [
            "9-1-Evening",
            "9-0-Evening",
            "10-1-Evening",
            "10-0-Evening",
            "11-1-Evening",
            "11-0-Evening",
            "12-1-Evening",
            "12-0-Evening",
            "1-1-Dawn",
            "1-1-Morning",
            "1-1-Afternoon",
            "1-0-Dawn",
            "1-0-Morning",
            "1-0-Afternoon",
            "1-0-Evening",
        ],
        2: [
            "9-1-Dawn",
            "9-1-Morning",
            "9-1-Afternoon",
            "9-0-Dawn",
            "9-0-Morning",
            "9-0-Afternoon",
            "10-1-Dawn",
            "10-0-Dawn",
            "11-1-Dawn",
            "11-0-Dawn",
            "12-1-Dawn",
            "12-1-Morning",
            "12-0-Dawn",
            "12-0-Morning",
            "12-0-Afternoon",
        ],
    }
    # 每个月对应的是否工作日天数
    days_to = {
        "1-0": 7,
        "1-1": 18,
        "9-0": 10,
        "9-1": 20,
        "10-0": 14,
        "10-1": 17,
        "11-0": 8,
        "11-1": 22,
        "12-0": 10,
        "12-1": 21,
    }

    df = pd.read_csv("data/detail/aaa.csv")

    groups = df.groupby(["month", "is_weekday", "time_period"])
    re = {}
    for g in groups:
        key = "-".join(str(x) for x in g[0])
        re[key] = {}
        days = days_to[str(g[0][0]) + "-" + str(g[0][1])]
        # print(g[1])  # 行414
        rank_group = g[1].groupby("rank")
        for rank in rank_group:
            # 提交次数/时间段天数
            d1 = len(rank[1]) / days
            # 活跃天数/时间段天数；题目数
            id_group = rank[1].groupby("student_ID")
            active_days = 0
            title_num = 0
            for id in id_group:
                active_days = active_days + len(id[1]["date"].value_counts().index)
                title_num = title_num + len(id[1]["title_ID"].value_counts().index)
            re[key][rank[0]] = [d1, active_days / days, title_num / days]

        # for stu in students_to.keys():
        #     students = g[1][g[1]['student_ID'].isin(students_to[stu])]
        #     # 提交次数/时间段天数
        #     d1 = len(students)/days
        #     # 活跃天数/时间段天数；题目数
        #     id_group = students.groupby('student_ID')
        #     active_days = 0
        #     title_num = 0
        #     for id in id_group:
        #         active_days = active_days + \
        #             len(id[1]['date'].value_counts().index)
        #         title_num = title_num + \
        #             len(id[1]['title_ID'].value_counts().index)
        #     re[key][stu] = [d1, active_days/days, title_num/days]
    # print(re)

    # 将相同类型的时间段数据整合
    combine_time = {0: [], 1: [], 2: []}
    for tag in combine_time.keys():
        for time in tag_to_time[tag]:
            combine_time[tag].append(re[time])
    # print(combine_time)

    get_add = {
        0: {"top": [], "mid": [], "low": []},
        1: {"top": [], "mid": [], "low": []},
        2: {"top": [], "mid": [], "low": []},
    }
    # get_add={0:{'top':[[],[]],'mid':[],'low':[]}}
    for tag in combine_time.keys():
        for item in combine_time[tag]:
            # 一个对象，top,mid,low
            for stu in item.keys():
                get_add[tag][stu].append(item[stu])
    # print(get_add)

    students_nums = {"top": 409, "mid": 546, "low": 409}
    # 计算二维列表平均值，再除以学生人数,最终结果
    final_re = {}
    for tag in get_add.keys():
        final_re[tag] = {}
        for stu in get_add[tag].keys():
            final_re[tag][stu] = [
                sum(col) / (len(col) * students_nums[stu])
                for col in zip(*get_add[tag][stu])
            ]
    # print(final_re)

    tag_label = {0: "高峰型", 1: "低峰型", 2: "平均型"}
    re_file = {}
    for key, value in final_re.items():
        re_file[tag_label[key]] = {}
        for i, j in value.items():
            re_file[tag_label[key]][i] = j
    # print(re_file)

    write_dict_to_json("data/detail/time_cluster_student_analysis.json", re_file)


# 掌握程度衡量权重变化后，top,mid,low的学生可能会变化，而且掌握程度也变了，因次要重新计算


def pro_cluster():
    file = "data/cluster/student_more_info"
    knowledge_file = "data/classes/month_data/month_knowledge/student_master_knowledge_"
    df = pd.read_csv("data/classes/basic_info/basic_info_all.csv")
    for month in [9, 10, 11, 12, 1]:
        file_name = file + str(month) + ".json"
        knowledge_file_name = knowledge_file + str(month) + ".csv"
        # print(file_name)
        data = read_json(file_name)
        df_k = pd.read_csv(knowledge_file_name)

        # print(data)

        for item in data:
            item["master"] = df_k[df_k["Unnamed: 0"] == item["key"]][
                "all_knowledge"
            ].to_list()[0]
            item["rank"] = df[df["Unnamed: 0"] == item["key"]]["rank"].to_list()[0]
        write_dict_to_json(file_name, data)


# 掌握程度衡量权重变化后，top,mid,low的学生可能会变化，而且掌握程度也变了，因次要重新计算


def pro_corr():

    def get_knowledge_master_v4(mon):
        student_to_tag = "data/cluster/student_tag_dict" + str(mon) + ".json"
        knowledge_ = (
            "data/knowledge/month_knowledge/student_master_knowledge_"
            + str(mon)
            + ".csv"
        )

        tag = read_json(student_to_tag)
        knowledge_master = pd.read_csv(knowledge_)

        # 注意类别数量
        re = {0: [], 1: [], 2: []}
        for id, value in tag.items():
            # 3表示没有做题
            if value != 3:
                knowledge = knowledge_master[knowledge_master["Unnamed: 0"] == id][
                    "all_knowledge"
                ].tolist()[0]

                re[value].append(knowledge)
        # print(re)
        return re

    def read_feature_encoder_v5(mon):
        month = {"9": 0, "10": 1, "11": 2, "12": 3, "1": 4}
        # 根据聚类后的标签，将原来的特征矩阵按照标签进行分组
        # 原始特征矩阵
        feature = read_json("data/cluster/month_student_feature_new.json")

        student_to_tag = (
            "data/cluster/month_student_to_tag/student_to_tag" + str(mon) + ".json"
        )
        tag = read_json(student_to_tag)

        # 注意类别数量
        re = {0: [], 1: [], 2: []}
        for i in range(len(tag)):
            re[tag[i][1]].append(
                [
                    feature[month[str(mon)]][i][0],
                    feature[month[str(mon)]][i][1],
                    feature[month[str(mon)]][i][3],
                    feature[month[str(mon)]][i][2],
                ]
            )
        return re

    def get_corr_v5(mon):
        feature = read_feature_encoder_v5(mon)
        master = get_knowledge_master_v4(mon)

        # feature_type = ['submit', 'active', 'correct', 'title']
        feature_type = ["submit", "active", "title", "correct"]

        # # 创建示例数据
        # data = {'变量1': [1, 2, 3, 4, 5],
        #         '变量2': [2, 4, 6, 8, 10],
        #         '变量3': [3, 6, 9, 12, 15]}

        # 每一类别分别计算
        corr_re = []
        # df_re = pd.DataFrame()
        for key in master.keys():
            # print(key, '---------------------------------------')
            arr = np.array(feature[key]).T
            # 获取每一列的值
            re = {}
            re["knowledge"] = master[key]

            for i in range(len(arr)):
                re[feature_type[i]] = list(arr[i])
            # print(re)
            df = pd.DataFrame(re)
            # df['month'] = np.arange(5).repeat(mon)
            new_df = df.corr()["knowledge"]
            corr_re.append(
                [new_df["submit"], new_df["active"], new_df["title"], new_df["correct"]]
            )
            # new_df['tag'] = [key, key, key, key, key]
            # new_df['month'] = [mon, mon, mon, mon, mon]
            # df_re = pd.concat([df_re, new_df], ignore_index=True)
        # 处理格式
        format_re = []
        if mon == 10:
            # 交换第一个和最后一个元素
            corr_re[0], corr_re[-1] = corr_re[-1], corr_re[0]

        for j in range(len(corr_re[0])):
            for i in range(len(corr_re)):
                format_re.append([j, i, corr_re[i][j].round(3)])

        return format_re

    def time_period_corr():
        # 时间段
        period = ["Dawn", "Morning", "Afternoon", "Evening"]
        feature = read_json("data/cluster/time_cluster_original_feature.json")
        re = {}
        for i in range(len(feature)):
            p = period[i % 4]
            if p in re:
                re[p].append(
                    [feature[i][3], feature[i][0], feature[i][1], feature[i][2]]
                )
            else:
                re[p] = []
                re[p].append(
                    [feature[i][3], feature[i][0], feature[i][1], feature[i][2]]
                )

        # print(re)

        feature_type = ["correct", "submit", "active", "title"]
        # 每一类别分别计算
        df_re = pd.DataFrame()
        corr_re = []
        for key in re.keys():
            print(key, "---------------------------------------")
            df = pd.DataFrame(re[key], columns=feature_type)
            new_df = df.corr()["correct"]
            corr_re.append([new_df["submit"], new_df["active"], new_df["title"]])
            # # new_df['tag'] = [key, key, key, key]
            # df_re = pd.concat([df_re, new_df])  # , ignore_index=True)

        format_re = []
        for j in range(len(corr_re[0])):
            for i in range(len(corr_re)):
                format_re.append([j, i, corr_re[i][j].round(3)])
        # print(format_re)
        return format_re

    result = []
    for month in [9, 10, 11, 12, 1]:
        # print(month, 'month')
        data = get_corr_v5(month)
        result.append(data)
    result.append(time_period_corr())
    write_dict_to_json("data/detail/corr.json", result)


# 处理雷达图数据


def pro_radar():
    # 首先根据总知识点掌握情况将学生分为：top/mid/low三类
    file = "data/classes/basic_info/basic_info_all.csv"
    data = (
        pd.read_csv(file)
        .sort_values(by="all_knowledge", ascending=False)
        .reset_index(drop=True)
    )
    # 总共1364,分为409，546，409，
    # print(len(data['all_knowledge']))
    top = list(data.loc[0:408, "Unnamed: 0"].values)
    mid = list(data.loc[409:954, "Unnamed: 0"].values)
    low = list(data.loc[955:1363, "Unnamed: 0"].values)
    students_to = {"top": top, "mid": mid, "low": low}
    # print(students_to)
    # write_dict_to_json('student_top_low.json', students_to)

    # 需要计算所有题平均正确率
    score_rate = pd.read_csv("data/classes/correct_rate/correct_rate_class_all.csv")
    score_rate = score_rate.fillna(0)
    score_rate["avg"] = score_rate.iloc[:, 1:].mean(axis=1)

    df = pd.read_csv("data/detail/aaa.csv")

    result = {}
    for stu in students_to.keys():
        # 掌握程度
        students = data[data["Unnamed: 0"].isin(students_to[stu])]
        # print(students)
        avg_k = sum(students["all_knowledge"].to_list()) / len(students_to[stu])
        # 得分率
        students = score_rate[score_rate["Unnamed: 0"].isin(students_to[stu])]
        avg_s = sum(students["avg"].to_list()) / len(students_to[stu])
        # 活跃度
        students = df[df["student_ID"].isin(students_to[stu])]
        id_group = students.groupby("student_ID")
        active_days = 0
        for id in id_group:
            active_days = active_days + len(id[1]["date"].value_counts().index)
        active_days_avg = active_days / len(students_to[stu])

        result[stu] = [avg_k, avg_s, active_days_avg]
    write_dict_to_json("data/detail/radar.json", result)


# 时间模式下，主图下方视图数据


def pro_timeEvolution():
    # 类型映射
    type_to = {0: "高峰型", 1: "低峰型", 2: "平均型"}
    month_to = {9: "9月", 10: "10月", 11: "11月", 12: "12月", 1: "1月"}
    period_to = {
        "Dawn": "凌晨",
        "Morning": "上午",
        "Afternoon": "下午",
        "Evening": "晚上",
    }
    weekday_to = {1: "weekday", 0: "weekoff"}

    tags = read_json("data/cluster/time_cluster_label.json")
    info = pd.read_csv("data/detail/aaa.csv")
    time_feature = read_json("data/cluster/time_cluster_original_feature.json")

    # 计算平均值
    result = {}
    i = 0
    for month in ["9", "10", "11", "12", "1"]:
        # 工作日、休息日
        for weekday in [1, 0]:
            # 时间段
            for period in ["Dawn", "Morning", "Afternoon", "Evening"]:
                key = month + "-" + period
                if key not in result:
                    result[key] = []
                result[key].append(time_feature[i][3])
                i = i + 1
    # 使用字典推导式计算平均值并重新赋值给键
    averages = {key: sum(values) / len(values) for key, values in result.items()}
    # print(averages)

    # 依次9到12月
    i = 0
    result = {"weekday": [], "weekoff": []}
    for month in month_to.keys():
        # 工作日、休息日
        for weekday in weekday_to.keys():
            # 时间段
            for period in period_to.keys():
                nums = []
                for rank in ["top", "mid", "low"]:
                    students = info[
                        (info["month"] == month)
                        & (info["is_weekday"] == weekday)
                        & (info["time_period"] == period)
                        & (info["rank"] == rank)
                    ]
                    nums.append(len(students.groupby("student_ID")))

                result[weekday_to[weekday]].append(
                    [
                        str(month) + "月-" + period_to[period],
                        type_to[tags[i]],
                        nums,
                        round(time_feature[i][3], 4),
                        round(averages[str(month) + "-" + period], 4),
                    ]
                )
                # print(result)

                i = i + 1
    # print(result)
    # return(result)
    write_dict_to_json("data/detail/time_evolution.json", result)


@app.route("/setWeightInfo", methods=["GET", "POST"])
def setWeightInfo():
    w1 = request.json.get("score")  # post
    w2 = request.json.get("correct")  # post
    w3 = request.json.get("time")  # post
    w4 = request.json.get("memory")  # post
    w = {"w1": w1, "w2": w2, "w3": w3, "w4": w4}

    # 分班计算获取题目掌握程度
    get_all_class_master_title("master", w)
    # 分班级获取学生对知识点的掌握程度
    get_all_class_master_knowledge("knowledge")
    # 获取所有班级对子知识点的掌握程度
    get_all_class_master_knowledge("sub_knowledge")

    # 处理basicInfo所需数据
    pro_basicInfo()  # 这一步处理了aaa.csv，理论上后面的步骤可以并行

    # 处理聚类视图的knowledge和rank
    pro_cluster()

    # 处理相关系数
    pro_corr()
    # 处理雷达图
    pro_radar()
    # 处理时间模式右下象形柱图数据
    pro_timeStudentInfo()
    # 时间模式演化图
    pro_timeEvolution()
    return "success"


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
                    master_file_class["all_knowledge"].mean(numeric_only=True).round(4),
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

    master_file = "./data/classes/title_master/student_master_title_" + str(id) + ".csv"
    score_file = (
        "./data/classes/title_score_rate/student_master_title_" + str(id) + ".csv"
    )
    correct_file = "./data/classes/correct_rate/correct_rate_class_" + str(id) + ".csv"

    num_list = list(titleTo.values())
    num_list.insert(0, "Unnamed: 0")
    master_info = (
        pd.read_csv(master_file)
        .reindex(columns=num_list)
        .mean(numeric_only=True)
        .round(4)
    )
    score_info = (
        pd.read_csv(score_file)
        .reindex(columns=num_list)
        .mean(numeric_only=True)
        .round(4)
    )
    correct_info = (
        pd.read_csv(correct_file)
        .reindex(columns=num_list)
        .mean(numeric_only=True)
        .round(4)
    )
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
        sorted(time_data[title].items(), key=lambda d: float(d[0]), reverse=False)
    )
    memory_dic = dict(
        sorted(memory_data[title].items(), key=lambda d: float(d[0]), reverse=False)
    )
    re["time"] = {"keys": list(time_dic.keys()), "value": list(time_dic.values())}
    re["memory"] = {"keys": list(memory_dic.keys()), "value": list(memory_dic.values())}

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
    store_file3 = "data/classes/title_master/student_master_title_"

    store_title_score = "./data/classes/correct_rate/correct_rate_class_"

    knowledge = pd.read_csv(store_file1 + str(id) + ".csv")
    df_knowledge = pd.concat([df_knowledge, knowledge], ignore_index=True)

    sub_knowledge = pd.read_csv(store_file2 + str(id) + ".csv")
    df_sub_knowledge = pd.concat([df_sub_knowledge, sub_knowledge], ignore_index=True)

    # 题目得分率
    if title_value == "score":
        title = pd.read_csv(store_title_score + str(id) + ".csv")
        df_title = pd.concat([df_title, title], ignore_index=True)
    else:
        title = pd.read_csv(store_file3 + str(id) + ".csv")
        df_title = pd.concat([df_title, title], ignore_index=True)

    knowledge_mean = df_knowledge.mean(numeric_only=True).round(4)

    sub_knowledge_mean = df_sub_knowledge.mean(numeric_only=True).round(4)

    title_mean = df_title.mean(numeric_only=True).round(4)

    knowledge_max = knowledge_mean.max()
    knowledge_min = knowledge_mean.min()
    title_max = title_mean.max()
    title_min = title_mean.min()

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
    return {
        "info": reInfo,
        "valueInfo": {
            "knowledge_max": knowledge_max,
            "knowledge_min": knowledge_min,
            "title_max": title_max,
            "title_min": title_min,
        },
    }


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
            strDate = str(date[0]).replace("/", "-")
            # 使用split()函数将字符串拆分为年、月、日
            year, month, day = strDate.split("-")

            # 使用zfill()函数将月份格式化为两位数
            month = month.zfill(2)
            day = day.zfill(2)

            # 格式化后的字符串
            strDate = f"{year}-{month}-{day}"
            re[g[0]][strDate] = []
            # 正确率
            result_status = date[1]["state"].value_counts(normalize=True)
            correct_rate = 0
            if "Absolutely_Correct" in result_status.index:
                correct_rate = correct_rate + result_status["Absolutely_Correct"]
            if "Partially_Correct" in result_status.index:
                correct_rate = correct_rate + result_status["Partially_Correct"]
            re[g[0]][strDate].append(correct_rate)
            # 答题数
            title_num = len(date[1]["title_ID"].value_counts().index)
            re[g[0]][strDate].append(title_num)
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
            re[g[0]][strDate].append(temp)

            # 提交次数
            re[g[0]][strDate].append(all_counts / title_num)

        # print(sort_g)
    # print(re)
    return re


# 个人提交图


@app.route("/personalSubmitInfo", methods=["GET", "POST"])
def personalSubmitInfo():
    student_id = request.json.get("data")  # 学生id列表
    learning_date = request.json.get("date")

    parts = learning_date.split("-")
    learning_date = "/".join([part.lstrip("0") for part in parts])

    # 用时分布
    title_timeconsume_count = read_json("./data/detail/title_timeconsume_count.json")
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
                total_correct_count = sum(title_timeconsume_count[g[0]].values())
                # 用时
                temp_sum = 0
                for key in title_timeconsume_count[g[0]].keys():
                    if int(float(key)) <= int(row["timeconsume"]):
                        temp_sum = temp_sum + title_timeconsume_count[g[0]][key]
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


# 帮助进行四舍五入操作
def round_if_needed(value, decimals=4):
    if isinstance(value, float) and value != int(value):
        return round(value, decimals)
    return value


@app.route("/featureStatisticsInfo", methods=["GET", "POST"])
def featureStatisticsInfo():
    # 输入：month,10月修改顺序
    month = request.json.get("data")
    month_to = {9: 0, 10: 1, 11: 2, 12: 3, 1: 4}

    result = {0: [], 1: [], 2: []}

    # 时间模式特征# 现在包含五个元素[提交次数，活跃天数，题目数，正确率，学生人数]
    if month == 2:
        feature = read_json("data/cluster/time_cluster_original_feature.json")
        tags = read_json("data/cluster/time_cluster_label.json")
        for i in range(len(tags)):
            result[tags[i]].append(
                [
                    feature[i][0],
                    feature[i][1],
                    feature[i][3],
                    feature[i][2],
                    feature[i][4],
                ]
            )

            # 其他月的分类：针对、多样、尝试
        feature_name = ["提交次数", "活跃天数", "正确占比", "答题数", "答题人数"]
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
            for key in mid_re.keys():
                final_re[i].append(mid_re[key][i])

    else:
        # 特征：提交次数、活跃天数、正确占比、题目数
        feature = read_json("./data/cluster/month_student_feature_new.json")[
            month_to[month]
        ]
        tags = read_json("data/cluster/cluster_label" + str(month) + ".json")

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
            # 四舍五入
            min_val = round_if_needed(min(data))
            q1_val = round_if_needed(np.percentile(data, 25))
            median_val = round_if_needed(np.median(data))
            q3_val = round_if_needed(np.percentile(data, 75))
            max_val = round_if_needed(max(data))
            new_final_re[key].append(
                [
                    min_val,
                    q1_val,
                    median_val,
                    q3_val,
                    max_val,
                ]
            )
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

    df = pd.read_csv("./data/detail/aaa.csv")
    tags = read_json("./data/cluster/student_tag_dict" + str(month) + ".json")

    data = df[
        (df["month"] == month)
        & (df["time_period"] == period)
        & (df["is_weekday"] == is_weekday)
    ].sort_values("date")

    date_group = data.groupby("date")
    # 根据日期进行分组，
    result = {}
    for g in date_group:
        # 如果是9，1，月，需要表示为09，01
        strDate = str(g[0]).replace("/", "-")
        # 使用split()函数将字符串拆分为年、月、日
        year, month, day = strDate.split("-")

        # 使用zfill()函数将月份格式化为两位数
        month = month.zfill(2)
        day = day.zfill(2)

        # 格式化后的字符串
        strDate = f"{year}-{month}-{day}"

        # 类型依次是针对、多样、尝试，012
        # 十月标签顺序不一样要修改210
        stu_group = g[1].groupby("student_ID")
        sum_li = [0, 0, 0]
        for student in stu_group:
            if month == 10:
                tag = abs(tags[student[0]] - 2)
                sum_li[tag] = sum_li[tag] + 1
            else:
                tag = tags[student[0]]
                sum_li[tag] = sum_li[tag] + 1

        result[strDate] = sum_li
    # print(result)
    return result


# 时间模式下，右下3图，对学生分类后的分析


@app.route("/timeStudentInfo", methods=["GET", "POST"])
def timeStudentInfo():
    feature = request.json.get("data")

    # feature = '活跃天数'
    feature_to = {"提交次数": 0, "活跃天数": 1, "题目数": 2}
    feature_label = feature_to[feature]
    data = read_json("./data/detail/time_cluster_student_analysis.json")
    result = {}
    for key, value in data.items():
        result[key] = []
        for stu in ["top", "mid", "low"]:
            result[key].append(value[stu][feature_label])

    result2 = {
        "top": [result["高峰型"][0], result["平均型"][0], result["低峰型"][0]],
        "mid": [result["高峰型"][1], result["平均型"][1], result["低峰型"][1]],
        "low": [result["高峰型"][2], result["平均型"][2], result["低峰型"][2]],
    }

    return [result, result2]


# 时间模式下，雷达图数据


@app.route("/timeRadarInfo", methods=["GET", "POST"])
def timeRadarInfo():
    data = read_json("data/detail/radar.json")
    return data


@app.route("/timeEvolutionInfo", methods=["GET", "POST"])
def timeEvolutionInfo():
    data = read_json("data/detail/time_evolution.json")
    result = [data["weekday"], data["weekoff"]]

    return result


# 协助获取聚类所需的坐标数据以及对应的标签数据


def group_cluster_data(file_path1, file_path2, classNum, num=0):
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
        else:
            # 时间模式下加标签
            if cluster_label[index] == 0:
                features["label"] = "高峰型"
            elif cluster_label[index] == 1:
                features["label"] = "低峰型"
            elif cluster_label[index] == 2:
                features["label"] = "平均型"
        grouped_data[cluster_label[index]].append(features)
    if classNum != "all" and num != -1:
        # 使用列表推导式对三个列表进行筛选
        grouped_data[0] = [
            item for item in grouped_data[0] if item["class"] == classNum
        ]
        grouped_data[1] = [
            item for item in grouped_data[1] if item["class"] == classNum
        ]
        grouped_data[2] = [
            item for item in grouped_data[2] if item["class"] == classNum
        ]
    # 10是特殊情况
    if num == 10:
        # 交换第一个元素和第三个元素的位置
        grouped_data[0], grouped_data[2] = grouped_data[2], grouped_data[0]
    return grouped_data


# 聚类数据
@app.route("/clusterData", methods=["GET", "POST"])
def cluster_data():
    classNum = request.json.get("classNum")
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
    time_feature_path = "data/cluster/time_feature_merge.json"
    time_label_path = "data/cluster/time_cluster_label.json"
    a = group_cluster_data(feature_path9, label_path9, classNum)
    b = group_cluster_data(feature_path10, label_path10, classNum, 10)
    c = group_cluster_data(feature_path11, label_path11, classNum)
    d = group_cluster_data(feature_path12, label_path12, classNum)
    e = group_cluster_data(feature_path1, label_path1, classNum)
    f = group_cluster_data(time_feature_path, time_label_path, classNum, -1)
    merged_data = [a, b, c, d, e, f]
    return merged_data


# 相关性系数列表
@app.route("/correlationData")
def correlation_data():
    data_list = read_json("data/detail/corr.json")
    # data_list = [
    #     [
    #         [0, 0, 0.139],
    #         [0, 1, 0.345],
    #         [0, 2, 0.183],
    #         [1, 0, 0.05],
    #         [1, 1, -0.504],
    #         [1, 2, 0.088],
    #         [2, 0, 0.258],
    #         [2, 1, 0.352],
    #         [2, 2, 0.443],
    #         [3, 0, 0.755],
    #         [3, 1, 0.694],
    #         [3, 2, 0.597],
    #     ],
    #     [
    #         [0, 0, -0.189],
    #         [0, 1, 0.378],
    #         [0, 2, -0.178],
    #         [1, 0, 0.133],
    #         [1, 1, -0.480],
    #         [1, 2, 0.100],
    #         [2, 0, 0.321],
    #         [2, 1, 0.148],
    #         [2, 2, 0.416],
    #         [3, 0, 0.702],
    #         [3, 1, 0.742],
    #         [3, 2, 0.594],
    #     ],
    #     [
    #         [0, 0, -0.051],
    #         [0, 1, 0.388],
    #         [0, 2, -0.227],
    #         [1, 0, -0.157],
    #         [1, 1, -0.303],
    #         [1, 2, 0.047],
    #         [2, 0, 0.096],
    #         [2, 1, 0.107],
    #         [2, 2, 0.323],
    #         [3, 0, 0.616],
    #         [3, 1, 0.777],
    #         [3, 2, 0.569],
    #     ],
    #     [
    #         [0, 0, 0.031],
    #         [0, 1, 0.472],
    #         [0, 2, -0.248],
    #         [1, 0, -0.409],
    #         [1, 1, -0.319],
    #         [1, 2, -0.046],
    #         [2, 0, 0.022],
    #         [2, 1, 0.462],
    #         [2, 2, 0.457],
    #         [3, 0, 0.585],
    #         [3, 1, 0.623],
    #         [3, 2, 0.536],
    #     ],
    #     [
    #         [0, 0, 0.039],
    #         [0, 1, 0.885],
    #         [0, 2, -0.131],
    #         [1, 0, -0.142],
    #         [1, 1, -0.854],
    #         [1, 2, -0.664],
    #         [2, 0, 0.040],
    #         [2, 1, 0.798],
    #         [2, 2, 0.160],
    #         [3, 0, 0.825],
    #         [3, 1, 0.936],
    #         [3, 2, 0.340],
    #     ],
    #     [
    #         [0, 0, -0.771],
    #         [0, 1, -0.315],
    #         [0, 2, -0.632],
    #         [0, 3, -0.190],
    #         [1, 0, -0.673],
    #         [1, 1, -0.250],
    #         [1, 2, -0.582],
    #         [1, 3, -0.167],
    #         [2, 0, -0.689],
    #         [2, 1, -0.226],
    #         [2, 2, -0.594],
    #         [2, 3, -0.168],
    #     ],
    # ]
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
    right_value_counter = Counter(right_dict.values())
    # 将 Counter 对象转换为字典，并按键排序
    sorted_counts = dict(sorted(right_value_counter.items(), key=lambda x: x[0]))
    # print(sorted_counts)
    # 将 Counter 对象的值转换为列表
    right_values_list = list(sorted_counts.values())
    transfer_matrix = [[0 for _ in range(4)] for _ in range(4)]
    student_matrix = [[[] for _ in range(4)] for _ in range(4)]
    for student_id, tag in left_dict.items():
        if tag != right_dict[student_id]:
            transfer_matrix[tag][right_dict[student_id]] += 1
            student_matrix[tag][right_dict[student_id]].append(student_id)
    return [right_values_list, transfer_matrix, student_matrix]


@app.route("/monthQuestionSubmit", methods=["GET", "POST"])
# 计算每个月学生针对每道题的提交次数和正确率
def get_month_question_submit():
    # 拿到前端传递的参数
    id = request.args.get("id")
    month = request.args.get("month")
    with open("data/monthFeature/month_question_submit.json", "r") as f:
        month_question_submit = json.load(f)
    with open("data/monthFeature/month_question_accuracy.json", "r") as f:
        month_question_accuracy = json.load(f)
    year_month = ""
    if month == "9":
        year_month = "2023-09"
    elif month == "10":
        year_month = "2023-10"
    elif month == "11":
        year_month = "2023-11"
    elif month == "12":
        year_month = "2023-12"
    elif month == "1":
        year_month = "2024-01"
    monthRecord1 = month_question_submit[id][year_month]
    monthRecord2 = month_question_accuracy[id][year_month]
    # 分别创建存放键和值的数组
    keys_array = []
    values_array1 = []
    values_array2 = []
    # 按键排序
    sorted_data1 = dict(sorted(monthRecord1.items()))
    sorted_data2 = dict(sorted(monthRecord2.items()))
    # 遍历答题情况，将键和对应的值分别放入数组中
    for key, value in sorted_data1.items():
        keys_array.append(key)
        values_array1.append(value)
    for key, value in sorted_data2.items():
        values_array2.append(value)
    return [keys_array, values_array1, values_array2]


if __name__ == "__main__":
    app.run(debug=True)
    app.logger.setLevel(logging.DEBUG)
