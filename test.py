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


f1 = './data/cluster/student_more_info'
f2 = './data/knowledge/month_knowledge/student_master_knowledge_'
store = 'data/new/student_more_info'

for month in [9, 10, 11, 12, 1]:
    print(month)
    f1_n = f1+str(month)+'.json'
    f2_n = f2+str(month)+'.csv'
    store_n = store+str(month)+'.json'
    json_data = read_json(f1_n)
    csv_data = pd.read_csv(f2_n)
    # print(csv_data)

    for item in json_data:
        master = csv_data[csv_data['Unnamed: 0']
                          == item['key']]['all_knowledge'].to_list()[0]
        item['master'] = master
    # print(json_data)
    write_dict_to_json(store_n, json_data)
