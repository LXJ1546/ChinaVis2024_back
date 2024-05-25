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


df = pd.read_csv('./data/detail/aaa.csv')

# 传入数据month,is_weekday,period
month = 9
is_weekday = 1
period = 'Morning'
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
print(result)
