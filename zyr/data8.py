# 计算题型偏好
# v1,使用某个知识点的题目平均提交次数

import pandas as pd
import json
import numpy as np
import math


def read_json(f_name):
    # f_name = 'F:/vscode/vis24/data/datap/knowledge_to_title.json'
    f = open(f_name, 'r')
    content = f.read()
    f.close()
    return (json.loads(content))


def dict_to_csv(info, file_path):
    # null填充空
    # 将字典转换为 DataFrame
    df = pd.DataFrame.from_dict(info, orient='index')
    # 缺失值填充为!!!!!!!!!!!!!!!!!!!!!!
    df = df.fillna('null')
    df.to_csv(file_path, index=True)


def get_knowledge_preference():
    data = read_json('F:/vscode/vis24/data/all_student_title_group.json')
    knowledge_to_title = read_json(
        'F:/vscode/vis24/data/datap/knowledge_to_title.json')
    re = {}
    # 遍历每一个学生
    for student in data.keys():
        re[student] = {}
        # 遍历每一个题目
        for knowledge in knowledge_to_title.keys():
            re[student][knowledge] = 0
            knowledge_title_counts = len(knowledge_to_title[knowledge].keys())
            for title in data[student]:
                # 做题次数len(data[student][title])
                if title in knowledge_to_title[knowledge].keys():
                    re[student][knowledge] = re[student][knowledge] + len(
                        data[student][title]) / knowledge_title_counts
    dict_to_csv(re, 'F:/vscode/vis24/data/datap/knowledge_preference.csv')


get_knowledge_preference()
