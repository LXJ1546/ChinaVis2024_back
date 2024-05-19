# 主要是对data6进行了更加规范的改写
# 学生掌握程度：题目，子知识点，主知识，总；题目得分率
import json
import pandas as pd

pd.set_option('display.width', 1000)
# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)


def write_dict_to_json(file_path, data):
    # 将字典写入 JSON 文件
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)  # 使用 indent 参数以更易读的方式写入 JSON 文件


# 计算学生对每一个题目的掌握程度或者是得分率


def get_student_master_title(case, f_name, f_store):
    '''
    case:表示计算掌握程度还是公式
    f_name:进行处理的文件
    f_store:处理结果的保存路径
    注意：后续可能还需要将掌握程度的权重也作为参数进行传递
    '''
    f = open(f_name, 'r')
    content = f.read()
    a = json.loads(content)
    f.close()

    # 读取题目用时、内存分布情况
    f = open('./datap/title_timeconsume_count.json', 'r')
    content = f.read()
    title_timeconsume_count = json.loads(content)
    f.close()
    f = open('./datap/title_memory_count.json', 'r')
    content = f.read()
    title_memory_count = json.loads(content)
    f.close()

    re = {}
    # 计算得分率
    if (case == 'score'):
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
                    # 计算得分率使用这个
                    score_rate.append(item[3]/item[7])
                score_rate_avg = sum(score_rate)/len(score_rate)
                # 计算得分率
                re[student][title] = score_rate_avg

    # 否则，就是计算掌握程度
    else:
        # 遍历学生
        for student in a.keys():
            # print(key)
            re[student] = {}
            for title in a[student].keys():
                # 读取a[student][title]是一个题目列表
                score_rate = []  # 储存得分率
                state_list = []  # 存储学生的答题状态，用以计算正确占比和错误占比
                memory_rank = 1  # 内存和用时没有完全正确的情况就设为1
                timeconsume_rank = 1
                memory_timeconsume_rank_candidata = []  # 记录正确情况下，用时和内存使用的候选，因为可能有多次完全正确

                # 遍历题目列表
                for item in a[student][title]:
                    # item:[1704206906, 'Class1', 'Absolutely_Error', 0, 'Method_m8vwGkEZc3TSW2xqYUoR', 320, '2', 3, "['b3C9s,b3C9s_l4z6od7y']"]
                    # 计算掌握程度使用这个
                    if item[2] == 'Absolutely_Correct' or 'Partially_Correct':
                        score_rate.append(item[3]/item[7])

                    # 答题状态
                    state_list.append(item[2])
                    # 用时和内存如何衡量,只有在完全正确的情况下考虑

                    if item[2] == 'Absolutely_Correct':
                        total_correct_count = sum(
                            title_timeconsume_count[title].values())
                        # memory
                        # 遍历title_timeconsume_count，计算占比前百分之多少
                        temp_sum = 0
                        for key in title_timeconsume_count[title].keys():
                            if (int(float(key)) <= int(item[6])):
                                temp_sum = temp_sum + \
                                    title_timeconsume_count[title][key]
                        memory_rank_temp = temp_sum/total_correct_count

                        # 遍历title_memory_count，计算占比前百分之多少
                        temp_sum = 0
                        for key in title_memory_count[title].keys():
                            if (int(key) <= item[5]):
                                temp_sum = temp_sum + \
                                    title_memory_count[title][key]
                        timeconsume_rank_temp = temp_sum/total_correct_count
                        memory_timeconsume_rank_candidata.append(
                            [memory_rank_temp, timeconsume_rank_temp])

                # 从memory_timeconsume_rank_candidata中获取最优的那一次
                if (len(memory_timeconsume_rank_candidata) > 0):
                    flag = float('inf')
                    flag_index = 0
                    for i in range(len(memory_timeconsume_rank_candidata)):
                        if (sum(memory_timeconsume_rank_candidata[i]) < flag):
                            flag = sum(memory_timeconsume_rank_candidata[i])
                            flag_index = i
                    memory_rank = memory_timeconsume_rank_candidata[flag_index][0]
                    timeconsume_rank = memory_timeconsume_rank_candidata[flag_index][1]

                score_rate_avg = sum(score_rate)/len(score_rate)
                # 错误占比
                error_count = 0
                for n in state_list:
                    if "Error" in n:
                        error_count = error_count+1
                error_rate = error_count/len(state_list)
                # 正确和部分正确占比
                correct_rate = 1-error_rate

                # # 新版本
                re[student][title] = 0.25*score_rate_avg+0.25*correct_rate + \
                    0.25*(1-memory_rank)+0.25*(1-timeconsume_rank)

    # 将字典转换为 DataFrame
    df = pd.DataFrame.from_dict(re, orient='index')

    # 缺失值填充为!!!!!!!!!!!!!!!!!!!!!!
    df = df.fillna('null')
    df.to_csv(f_store, index=True)


def get_all_class_master_title(case):
    # # 直接计算全体
    # file = 'F:/vscode/vis24/data/all_student_title_group.json'
    # get_student_master_title(
    #     case, file, 'F:/vscode/vis24/data/datap/all_student_master_title.csv')

    # 分班级计算掌握程度和得分率
    file = 'F:/vscode/vis24/data/datap/Data_class/student_title_group'
    if (case == 'score'):
        store = 'F:/vscode/vis24/data/datap/DataPro_class/title_score_rate/student_master_title_'
    else:
        store = 'F:/vscode/vis24/data/datap/DataPro_class/title_master/student_master_title_'
    for i in range(1, 16):
        print(i)
        f = file+str(i)+'.json'
        store_f = store+str(i)+'.csv'
        get_student_master_title(case, f, store_f)


# # 题目掌握程度
# get_all_class_master_title('master')
# # 题目得分率
# get_all_class_master_title('score')


def compare_calss_master_title():
    # 比较各班对题目掌握程度的差异
    file = 'F:/vscode/vis24/data/datap/DataPro_class/title_master/student_master_title_'
    series_list = []
    class_list = []
    for i in range(1, 16):
        print(i, '-----------------------------------')
        f = file+str(i)+'.csv'
        # 获取每一列的平均值
        df = pd.read_csv(f)
        column_means = df.mean(numeric_only=True)  # 只计算平均值

        # #到时候再看如何组织数据
        # t = df.describe()  # 所有的统计特征
        # print(t)
        series_list.append(column_means)
        class_list.append('class'+str(i))
    # 将多个Series拼接成一个DataFrame
    df = pd.concat(series_list, axis=1)
    # 添加新列'class'，并为每个Series添加特定值
    # df['class'] = class_list
    # df.to_csv('test.csv')
# compare_calss_master_title()


def get_student_master_all_knowledge_new(df):
    knowledge_to_title_file = 'F:/vscode/vis24/data/datap/knowledge_to_title.json'
    f = open(knowledge_to_title_file, 'r')
    content = f.read()
    knowledge_to_title = json.loads(content)
    f.close()

    # 所有知识点总分
    knowledge_score = 115
    origin_df = df.copy(deep=True)

    # 将取值为字符串 'null' 的元素替换为数值 0
    df.replace('null', 0, inplace=True)
    # print(df)
    # b3C9s 10
    # g7R2j 15
    # k4W1c 3
    # m3D1v 36
    # r8S3g 5
    # s8Y2f 3
    # t5V9e 10
    # y9W5d 33

    origin_df['all_knowledge'] = 10/knowledge_score * df['b3C9s'] + 15/knowledge_score * \
        df['g7R2j'] + 3/knowledge_score * \
        df['k4W1c']+36/knowledge_score * df['m3D1v']+5/knowledge_score * df['r8S3g']+3 / \
        knowledge_score * df['s8Y2f']+10/knowledge_score * \
        df['t5V9e']+33/knowledge_score * df['y9W5d']

    return origin_df


def get_student_master_knowledge(param):
    # 根据学生对题目的掌握程度计算每个学生对不同知识点的掌握程度
    # 主要参数，学生掌握题表，知识点到题目映射表，保存路径

    file = param['student_master_title']

    # knowledge_to_title_file = 'F:/vscode/vis24/data/datap/knowledge_to_title.json'
    knowledge_to_title_file = param['knowledge_to_title_file']
    df = pd.read_csv(file, low_memory=False)
    f = open(knowledge_to_title_file, 'r')
    content = f.read()
    knowledge_to_title = json.loads(content)
    f.close()

    dict_student_master_knowledge = {}
    # 依次遍历每一个学生
    for index, row in df.iterrows():
        dict_student_master_knowledge[row[0]] = {}
        # 依次遍历每一个知识点
        for knowledge in knowledge_to_title.keys():
            # 获取一个知识点对应的多个题目的题目列表
            title_list = knowledge_to_title[knowledge].keys()
            # 计算knowledge对应的题目总分
            total_score = sum(knowledge_to_title[knowledge].values())
            # print(total_score)
            master_rate = 0
            flag = True  # 用于标识学生当前知识点是否没有做,先默认为没做
            # 依次遍历一个知识点对应的题目
            for title in title_list:
                title = title.strip()
                # row[title]是该题目得分，只当掌握程度不为null时计算
                if (not pd.isna(row[title])):
                    flag = False
                    master_rate = master_rate + \
                        knowledge_to_title[knowledge][title] / \
                        total_score*row[title]
            if (not flag):
                dict_student_master_knowledge[row[0]][knowledge] = master_rate
    # print(dict_student_master_knowledge)
    # 将字典转换为 DataFrame
    df = pd.DataFrame.from_dict(dict_student_master_knowledge, orient='index')
    # 缺失值填充为
    df = df.fillna('null')
    # file_path = './datap/temp_student_master_knowledge_all.csv'
    # 如果是主知识点，就再添加一列，表示学生的所有知识点总的掌握程度
    if (param['case'] == 'knowledge'):
        df = get_student_master_all_knowledge_new(df)
    file_path = param['result_file']
    df.to_csv(file_path, index=True)


def get_all_class_master_knowledge(case):
    # # 全体
    # file = 'F:/vscode/vis24/data/datap/all_student_master_title.csv'
    # knowledge_to_title_file = 'F:/vscode/vis24/data/datap//knowledge_to_title.json'
    # store_f = 'F:/vscode/vis24/data/datap/all_student_master_knowledge.csv'

    # param = {"student_master_title": file,
    #          "knowledge_to_title_file": knowledge_to_title_file,
    #          "result_file": store_f,
    #          'case': case
    #          }
    # get_student_master_knowledge(param)

    # 分班级计算掌握知识点和子知识点的
    file = 'F:/vscode/vis24/data/datap/DataPro_class/title_master/student_master_title_'
    if (case == 'knowledge'):
        store = 'F:/vscode/vis24/data/datap/DataPro_class/knowledge/student_master_knowledge_'
        knowledge_to_title_file = 'F:/vscode/vis24/data/datap//knowledge_to_title.json'
    # 否则就是子知识点
    else:
        store = 'F:/vscode/vis24/data/datap/DataPro_class/sub_knowledge/student_master_sub_knowledge_'
        knowledge_to_title_file = 'F:/vscode/vis24/data/datap//sub_knowledge_to_title.json'
    for i in range(1, 16):
        print(i)
        f = file+str(i)+'.csv'
        store_f = store+str(i)+'.csv'
        # # 分班获取学生对每个知识点的掌握程度
        param = {"student_master_title": f,
                 "knowledge_to_title_file": knowledge_to_title_file,
                 "result_file": store_f,
                 'case': case
                 }
        get_student_master_knowledge(param)


# 分班级获取学生对知识点的掌握程度
get_all_class_master_knowledge('knowledge')
# # 获取所有班级对子知识点的掌握程度
# get_all_class_master_knowledge('sub_knowledge')

# 获取学生对所有知识点总的掌握程度


def get_student_master_all_knowledge(param):
    file = param['student_master_knowledge']

    knowledge_to_title_file = 'F:/vscode/vis24/data/datap/knowledge_to_title.json'
    df = pd.read_csv(file, low_memory=False)
    f = open(knowledge_to_title_file, 'r')
    content = f.read()
    knowledge_to_title = json.loads(content)
    f.close()

    # 所有知识点总分
    knowledge_score = 115

    dict_student_master_knowledge = {}
    # 依次遍历每一个学生
    for index, row in df.iterrows():
        dict_student_master_knowledge[row[0]] = {}
        # print('student', row[0], '------------------------------------')
        master_rate = 0
        # 依次遍历每一个知识点
        for knowledge in knowledge_to_title.keys():
            if (not pd.isna(row[knowledge])):
                master_rate = master_rate + \
                    sum(knowledge_to_title[knowledge].values(
                    ))/knowledge_score*row[knowledge]
        dict_student_master_knowledge[row[0]]['all_knowledge'] = master_rate
    # 将字典转换为 DataFrame
    df = pd.DataFrame.from_dict(dict_student_master_knowledge, orient='index')
    # 缺失值填充为
    # file_path = './datap/temp_student_master_knowledge_all.csv'
    file_path = param['result_file']
    df.to_csv(file_path, index=True)


def get_all_class_master_all_knowledge():
    # 分班级计算掌握知识点和子知识点的
    file = 'F:/vscode/vis24/data/datap/DataPro_class/knowledge/student_master_knowledge_'
    store = 'F:/vscode/vis24/data/datap/DataPro_class/all_knowledge/student_master_knowledge_'
    for i in range(1, 16):
        print(i)
        f = file+str(i)+'.csv'
        store_f = store+str(i)+'.csv'
        # # 分班获取学生对每个知识点的掌握程度
        param = {"student_master_knowledge": f,
                 "result_file": store_f}
        get_student_master_all_knowledge(param)


# get_all_class_master_all_knowledge()
