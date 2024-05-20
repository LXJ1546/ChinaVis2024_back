from flask import Flask, request
from flask_cors import CORS
import pandas as pd
import os
import re
import json
import logging


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
    file_temp = "./data/classes/basic_info_"
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


# 知识点


@app.route("/knowledgeMasterInfo")
def knowledgeMasterInfo():
    file = "./data/knowledge/Data_TitleInfo.csv"
    title = pd.read_csv(file)
    re = []
    knowledge_group = title.groupby("knowledge")
    for knowledge in knowledge_group:
        print(knowledge[0])
        re.append({"name": knowledge[0], "children": []})
        sub_knowledge_group = knowledge[1].groupby("sub_knowledge")
        for sub_knowledge in sub_knowledge_group:
            # re[-1]表示该列表最后一个元素
            re[-1]["children"].append({"name": sub_knowledge[0], "children": []})
            for index, row in sub_knowledge[1].iterrows():
                # print(row)
                re[-1]["children"][-1]["children"].append(
                    {"name": row["title_ID"], "value": row["score"]}
                )
    return re


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


if __name__ == "__main__":
    app.run(debug=True)
    app.logger.setLevel(logging.DEBUG)
