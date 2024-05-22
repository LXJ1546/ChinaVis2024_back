from flask import Flask, request
from flask_cors import CORS
import pandas as pd
import os
import re
import json
import logging
from collections import Counter


app = Flask(__name__)
# 允许跨域传输数据
CORS(app)


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

    master_file = './data/classes/title_master/student_master_title_' + \
        str(id)+'.csv'
    score_file = './data/classes/title_score_rate/student_master_title_' + \
        str(id)+'.csv'
    correct_file = './data/classes/correct_rate/correct_rate_class_' + \
        str(id)+'.csv'

    time_file = './data/classes/time_count/class_' + \
        str(id)+'.json'
    memory_file = './data/classes/memory_count/class_' + \
        str(id)+'.json'

    master_info = pd.read_csv(master_file).mean(numeric_only=True).round(4)
    score_info = pd.read_csv(score_file).mean(numeric_only=True).round(4)
    correct_info = pd.read_csv(correct_file).mean(numeric_only=True).round(4)
    re = []
    re.append({'name': '掌握程度',
               'data': list(master_info.values),
               'type': 'line',
               'smooth': 'true'})
    re.append({'name': '得分率',
               'data': list(score_info.values),
               'type': 'line',
               'smooth': 'true'})
    re.append({'name': '正确占比',
               'data': list(correct_info.values),
               'type': 'line',
               'smooth': 'true'})
    print(re)
    return (re)
# 知识点


@app.route("/knowledgeMasterInfo", methods=["GET", "POST"])
def knowledgeMasterInfo():
    id = request.json.get("data")  # post

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

    store_file1 = './data/knowledge/knowledge/student_master_knowledge_'
    store_file2 = './data/knowledge/sub_knowledge/student_master_sub_knowledge_'
    store_file3 = './data/knowledge/title_master/student_master_title_'

    if (id == 'all'):
        for i in range(1, 15):
            knowledge = pd.read_csv(store_file1+str(i+1)+'.csv')
            df_knowledge = pd.concat(
                [df_knowledge, knowledge], ignore_index=True)

            sub_knowledge = pd.read_csv(store_file2+str(i+1)+'.csv')
            df_sub_knowledge = pd.concat(
                [df_sub_knowledge, sub_knowledge], ignore_index=True)

            title = pd.read_csv(store_file3+str(i+1)+'.csv')
            df_title = pd.concat([df_title, title], ignore_index=True)
    else:
        knowledge = pd.read_csv(store_file1+id+'.csv')
        df_knowledge = pd.concat([df_knowledge, knowledge], ignore_index=True)

        sub_knowledge = pd.read_csv(store_file2+id+'.csv')
        df_sub_knowledge = pd.concat(
            [df_sub_knowledge, sub_knowledge], ignore_index=True)

        title = pd.read_csv(store_file3+id+'.csv')
        df_title = pd.concat([df_title, title], ignore_index=True)

    knowledge_mean = df_knowledge.mean(numeric_only=True).round(4)

    sub_knowledge_mean = df_sub_knowledge.mean(numeric_only=True).round(4)

    title_mean = df_title.mean(numeric_only=True).round(4)
    icon = {
        'Question_q7OpB2zCMmW9wS8uNt3H': 0,
        'Question_QRm48lXxzdP7Tn1WgNOf': 1,
        'Question_pVKXjZn0BkSwYcsa7C31': 2,
        'Question_lU2wvHSZq7m43xiVroBc': 3,
        'Question_x2Fy7rZ3SwYl9jMQkpOD': 4,
        'Question_oCjnFLbIs4Uxwek9rBpu': 5
    }

    file = './data/knowledge/Data_TitleInfo.csv'
    title = pd.read_csv(file)
    re = []
    knowledge_group = title.groupby('knowledge')
    for knowledge in knowledge_group:
        # print(knowledge[0])
        re.append(
            {'name': knowledge[0], 'score': knowledge_mean[knowledge[0]], 'children': []})
        sub_knowledge_group = knowledge[1].groupby('sub_knowledge')
        for sub_knowledge in sub_knowledge_group:
            # re[-1]表示该列表最后一个元素
            re[-1]['children'].append({'name': sub_knowledge[0],
                                       'score': sub_knowledge_mean[sub_knowledge[0]], 'children': []})
            for index, row in sub_knowledge[1].iterrows():
                # print(row)
                if (row['title_ID'] in icon.keys()):
                    re[-1]['children'][-1]['children'].append(
                        {'name': row['title_ID'], 'score': title_mean[row['title_ID']], 'value': row['score'], 'icon': icon[row['title_ID']]})
                else:
                    re[-1]['children'][-1]['children'].append(
                        {'name': row['title_ID'], 'score': title_mean[row['title_ID']], 'value': row['score']})
    # print(re)
    reInfo = {'name': 'Q1',
              'children': re}
    return reInfo


# 协助获取聚类所需的坐标数据以及对应的标签数据
def group_cluster_data(file_path1, file_path2, num=0):
    with open(file_path1, "r") as f:
        cluster_features = json.load(f)
    with open(file_path2, "r") as f:
        cluster_label = json.load(f)
    grouped_data = [[], [], []]
    # 将坐标与标签对应起来
    for index, features in enumerate(cluster_features):
        grouped_data[cluster_label[index]].append(features)
    # 10是特殊情况
    if num == 10:
        # 交换第一个元素和第三个元素的位置
        grouped_data[0], grouped_data[2] = grouped_data[2], grouped_data[0]
    return grouped_data


# 聚类数据
@app.route("/clusterData")
def cluster_data():
    feature_path9 = "data/cluster/cluster_features9.json"
    label_path9 = "data/cluster/cluster_label9.json"
    feature_path10 = "data/cluster/cluster_features10.json"
    label_path10 = "data/cluster/cluster_label10.json"
    feature_path11 = "data/cluster/cluster_features11.json"
    label_path11 = "data/cluster/cluster_label11.json"
    feature_path12 = "data/cluster/cluster_features12.json"
    label_path12 = "data/cluster/cluster_label12.json"
    feature_path1 = "data/cluster/cluster_features1.json"
    label_path1 = "data/cluster/cluster_label1.json"
    time_feature_path = "data/cluster/time_cluster_features.json"
    time_label_path = "data/cluster/time_cluster_label.json"
    a = group_cluster_data(feature_path9, label_path9)
    b = group_cluster_data(feature_path10, label_path10, 10)
    c = group_cluster_data(feature_path11, label_path11)
    d = group_cluster_data(feature_path12, label_path12)
    e = group_cluster_data(feature_path1, label_path1)
    f = group_cluster_data(time_feature_path, time_label_path)
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
