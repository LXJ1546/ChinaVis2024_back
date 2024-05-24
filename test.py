# 特征箱线图
# data={特征名:[[类型1数据]，[]，[]]}

import pandas as pd
import os
import json


def read_json(f_name):
    f = open(f_name, 'r')
    content = f.read()
    f.close()
    return (json.loads(content))


# 输入：month,10月修改顺序
month = 10
month_to = {9: 0, 10: 1, 11: 2, 12: 3, 1: 4}
# 特征：提交次数、活跃天数、正确占比、题目数
feature = read_json(
    './data/cluster/month_student_feature_new.json')[month_to[month]]
tags = read_json('data/cluster/cluster_label'+str(month)+'.json')

result = {0: [], 1: [], 2: []}
for i in range(len(tags)):
    result[tags[i]].append(feature[i])

# 其他月的分类：针对、多样、尝试
feature_name = ['提交次数', '活跃天数', '正确占比', '答题数']
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
    if (month == 10):
        for key in [2, 1, 0]:
            final_re[i].append(mid_re[key][i])
    # 不是十月
    else:
        for key in mid_re.keys():
            final_re[i].append(mid_re[key][i])
print(final_re)
