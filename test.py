# 特征箱线图
# data={特征名:[[类型1数据]，[]，[]]}

import pandas as pd
import os
import json
import re

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


time_feature = read_json('data/cluster/time_cluster_original_feature.json')

result = []
# [提交次数，活跃天数，题目数，正确率，学生人数]
i = 0
for month in ['9月', '10月', '11月', '12月', '1月']:
    # 工作日、休息日
    for weekday in ['工作日', '休息日']:
        # 时间段
        for period in ['凌晨', '上午', '下午', '晚上']:
            temp = {'key': month+weekday+period,
                    'submit': time_feature[i][0], 'active': time_feature[i][1], 'title': time_feature[i][2], 'correct': time_feature[i][3], 'students_num': time_feature[i][4]}
            result.append(temp)
            i = i+1
# print(result)
write_dict_to_json('./data/new/time_feature.json', result)
