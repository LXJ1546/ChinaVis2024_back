import pandas as pd
import os
import re
import json
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN

student_info_df = pd.read_csv("data/Data_StudentInfo.csv")


# 将字典保存为JSON文件
def save_to_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


# 聚类
def try_cluster():
    # 假设你的特征矩阵是一个numpy数组
    with open("data/temporary/month_student_feature_new_normalized.json", "r") as f:
        big_list = json.load(f)
    features = np.array(big_list[4])
    # with open("data/temporary/time/time_cluster_normalized.json", "r") as f:
    #     big_list = json.load(f)
    # features = np.array(big_list)
    # # 使用PCA进行降维
    # pca = PCA(n_components=2)
    # reduced_features = pca.fit_transform(features)
    # 使用KMeans进行聚类
    kmeans = KMeans(n_clusters=3, random_state=0).fit(features)
    # 获取聚类标签
    labels = kmeans.labels_
    # 使用t-SNE进行降维
    tsne = TSNE(n_components=2, random_state=0)
    reduced_features = tsne.fit_transform(features)
    # with open("data/temporary/classify_label_12.json", "r") as f:
    #     cluster_tag = json.load(f)
    # cluster_tag = np.array(cluster_tag)
    save_to_json(
        reduced_features.tolist(),
        f"data/cluster/cluster_features1.json",
    )
    # 绘制散点图
    plt.scatter(
        reduced_features[:, 0],
        reduced_features[:, 1],
        c=labels,
        s=50,
        cmap="viridis",
    )
    # alabels = labels.tolist()
    # save_to_json(
    #     alabels,
    #     f"data/cluster/cluster_label11.json",
    # )
    # # 创建图例
    # legend1 = plt.legend(*scatter.legend_elements(), title="Clusters")
    # plt.gca().add_artist(legend1)
    # 显示图像
    plt.savefig("my_figure.png")


# 将学生和聚类标签对应起来
def student_to_tag():
    # 假设你的特征矩阵是一个numpy数组
    with open("data/temporary/cluster1.json", "r") as f:
        cluster_tag = json.load(f)
    # 提取所有学生的ID
    student_ids = []
    for _, row in student_info_df.iterrows():
        student_id = row["student_ID"]
        student_ids.append(student_id)
    student_ids = sorted(student_ids)
    # combined_list = [[], [], [], []]
    # for index, id in enumerate(student_ids):
    #     combined_list[cluster_tag[index]].append(id)
    combined_list = list(zip(student_ids, cluster_tag))

    save_to_json(
        combined_list,
        f"data/temporary/student_to_tag.json",
    )


def student_to_tag1(aindex):
    month = 1
    if aindex == 0:
        month = 9
    elif aindex == 1:
        month = 10
    elif aindex == 2:
        month = 11
    elif aindex == 3:
        month = 12
    with open("data/temporary/month_student_feature.json", "r") as f:
        big_list = json.load(f)
    with open(f"data/abc/classify_label_{month}.json", "r") as f:
        cluster_tag = json.load(f)
    # 提取所有学生的ID
    student_ids = []
    for _, row in student_info_df.iterrows():
        student_id = row["student_ID"]
        student_ids.append(student_id)
    student_ids = sorted(student_ids)
    other_ids = []
    # 遍历某个月的列表，判断其是否不为0，是则放到other_ids中用于匹配标签
    for index, sub_list in enumerate(big_list[aindex]):
        if sum(sub_list) != 0:
            other_ids.append(student_ids[index])
    combined_list = list(zip(other_ids, cluster_tag))

    save_to_json(
        combined_list,
        f"data/abc/student_to_tag{month}.json",
    )


def elbow():
    # 假设你的特征矩阵是一个numpy数组
    with open("data/temporary/time/time_cluster_normalized.json", "r") as f:
        big_list = json.load(f)
    features = np.array(big_list)
    # 范围内的簇数
    K = range(1, 11)
    # 保存SSE值
    sse = []
    # 计算每个K值对应的SSE
    for k in K:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(features)
        sse.append(kmeans.inertia_)  # inertia_属性是SSE的值

    # 绘制SSE与K值的关系图
    plt.figure(figsize=(8, 4))
    plt.plot(K, sse, "bo-")
    plt.xlabel("Number of clusters, K")
    plt.ylabel("Sum of squared distances (SSE)")
    plt.title("Elbow Method For Optimal k")
    plt.savefig("my_elbow.png")
    # 二阶差分法
    second_diff = np.diff(sse, 2)
    optimal_k_second_diff = np.argmax(second_diff) + 2  # 因为差分会减少一个维度

    print(f"Optimal k using second difference method: {optimal_k_second_diff}")


try_cluster()
# elbow()
# student_to_tag1(0)
# student_to_tag1(1)
# student_to_tag1(2)
# student_to_tag1(3)
# student_to_tag1(4)
