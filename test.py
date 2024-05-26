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


tags = read_json('data/cluster/time_cluster_label.json')
result = {0: [], 1: [], 2: []}
label = []
for month in [9, 10, 11, 12, 1]:
    # 工作日、休息日
    for weekday in [1, 0]:
        # 时间段
        for period in ["Dawn", "Morning", "Afternoon", "Evening"]:
            key = str(month) + "-" + str(weekday) + "-" + period
            label.append(key)
for i in range(len(tags)):
    result[tags[i]].append(label[i])

print(result)
