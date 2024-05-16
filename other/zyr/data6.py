# 计算学生对题目/知识点掌握程度
# 计算知识点掌握程度，注意一个知识点可能涉及多个题目
import pandas as pd
import json

# 计算学生对每一个题目的掌握程度，但是还没有写完


def get_student_master_title():
    f = open('student_title_group1.json', 'r')
    content = f.read()
    a = json.loads(content)
    f.close()
    print(type(a))
    re = {}
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
                score_rate.append(item[3]/item[7])
                # 用时和内存如何衡量
            # 保存该学生对该题目的掌握程度
            re[student][title] = sum(score_rate)/len(score_rate)
    print(re)

    # 将字典转换为 DataFrame
    df = pd.DataFrame.from_dict(re, orient='index')

    # 缺失值填充为!!!!!!!!!!!!!!!!!!!!!!
    df = df.fillna(10)
    file_path = 'output1.csv'
    df.to_csv(file_path, index=True)

# 获取knowledge到题目id的映射字典


def get_knowledge_to_title_ID():
    file = 'F:/vscode/vis24/data/challenge1/Data_TitleInfo.csv'
    data = pd.read_csv(file, low_memory=False)
    # 假设 df 是你的 DataFrame 对象
    result = data.groupby('knowledge')['title_ID'].agg(
        lambda x: ', '.join(x.unique())).reset_index()
    # 获得一个字典，键是knowledge，值是knowledge对应的title_ID组成的字符串，用，隔开
    result_dict = result.set_index('knowledge').to_dict()['title_ID']
    return (result_dict)

# 根据学生对题目的掌握程度计算每个学生对不同知识点的掌握程度


def get_student_master_knowledge(knowledge_to_title):
    file = 'F:/vscode/vis24/data/output1.csv'
    file_title = 'F:/vscode/vis24/data/challenge1/Data_TitleInfo.csv'
    df = pd.read_csv(file, low_memory=False)
    df_title = pd.read_csv(file_title, low_memory=False)

    dict_student_master_knowledge = {}
    # 依次遍历每一个学生
    for index, row in df.iterrows():
        dict_student_master_knowledge[row[0]] = {}
        # 依次遍历每一个知识点
        for knowledge in knowledge_to_title.keys():
            # 获取一个知识点对应的多个题目的题目列表
            title_list = knowledge_to_title[knowledge].split(',')
            total_score = 0
            # 根据题目id,从df_title中计算knowledge对应的题目总分
            for title in title_list:
                title = title.strip()
                total_score = total_score+df_title[df_title['title_ID']
                                                   == title]['score'].tolist()[0]
            # print(total_score)
            master_rate = 0
            # 依次遍历一个知识点对应的题目
            for title in title_list:
                title = title.strip()
                master_rate = master_rate+df_title[df_title['title_ID']
                                                   == title]['score'].tolist()[0]/total_score*row[title]
            dict_student_master_knowledge[row[0]][knowledge] = master_rate
    # print(dict_student_master_knowledge)
    # 将字典转换为 DataFrame
    df = pd.DataFrame.from_dict(dict_student_master_knowledge, orient='index')

    # 缺失值填充为
    df = df.fillna('null')
    file_path = 'output.csv'
    df.to_csv(file_path, index=True)


knowledge_to_title = get_knowledge_to_title_ID()
get_student_master_knowledge(knowledge_to_title)
