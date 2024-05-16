import pandas as pd
import os
import re
import json
import numpy as np
from collections import defaultdict
import datetime
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN

# 加载学生信息表和题目信息表
student_info_df = pd.read_csv("data/Data_StudentInfo.csv")
question_info_df = pd.read_csv("data/Data_TitleInfo.csv")
# # 指定文件夹路径
folder_path = "data/Data_SubmitRecord"
# # 获取文件夹下所有文件的文件名
file_names = sorted(os.listdir(folder_path))
# print(file_names)
# file_names = [
#     "SubmitRecord-Class1.csv",
#     "SubmitRecord-Class2.csv",
#     "SubmitRecord-Class3.csv",
#     "SubmitRecord-Class4.csv",
#     "SubmitRecord-Class5.csv",
#     "SubmitRecord-Class6.csv",
#     "SubmitRecord-Class7.csv",
#     "SubmitRecord-Class8.csv",
#     "SubmitRecord-Class9.csv",
#     "SubmitRecord-Class10.csv",
#     "SubmitRecord-Class11.csv",
#     "SubmitRecord-Class12.csv",
#     "SubmitRecord-Class13.csv",
#     "SubmitRecord-Class14.csv",
#     "SubmitRecord-Class15.csv",
# ]


# 检查学生id和题目id是否存在不匹配的情况
def check_matching():
    # 初始化不匹配的数据列表
    unmatched_data1 = []
    unmatched_data2 = []
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 加载答题日志表
        answer_log_df = pd.read_csv(file_path)
        # 检查学生ID是否匹配
        for row in answer_log_df.iterrows():
            student_id = row["student_ID"]
            if student_id not in student_info_df["student_ID"].values:
                print("yes")
                unmatched_data1.append((row, "Student"))
        # 检查题目ID是否匹配
        for row in answer_log_df.iterrows():
            question_id = row["title_ID"]
            if question_id not in question_info_df["title_ID"].values:
                print("yes")
                unmatched_data2.append((row, "Question"))

    # 保存不匹配的数据
    unmatched_df = pd.DataFrame(unmatched_data1)
    unmatched_df.to_csv("unmatched_data1.csv", index=False)
    unmatched_df = pd.DataFrame(unmatched_data2)
    unmatched_df.to_csv("unmatched_data2.csv", index=False)


# 整合三个表，这里面有去除重复值
def integrate():
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    index = 0
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # print(file_name, index)
        # 加载答题日志表
        answer_log_df = pd.read_csv(file_path)
        merge_question_info_df = pd.read_csv("data/temporary/question_merged_data.csv")
        # 去除 answer_log_df 中的重复 student_ID
        # student_info_df = student_info_df.drop_duplicates(subset="student_ID")
        # question_info_df = question_info_df.drop_duplicates(subset="title_ID")
        # 检查学生ID是否匹配
        # for _, row in answer_log_df.iterrows():
        #     student_id = row["student_ID"]
        #     if student_id == "b57bc31cac59b3d26216":
        #         print(index)
        #         break
        # 将答题日志表与学生信息表和题目信息表进行左连接
        merged_df = pd.merge(
            answer_log_df,
            student_info_df.reset_index(drop=True),
            on="student_ID",
            how="left",
        )
        merged_df = pd.merge(
            merged_df,
            merge_question_info_df,
            on="title_ID",
            how="left",
            suffixes=("", "_total"),
        )
        merged_df.drop(columns=["index_y"], inplace=True)
        integrate_df = pd.DataFrame(merged_df)
        file_name = f"data/integration/integrated_data{index}.csv"
        integrate_df.to_csv(file_name, index=False)


# 找到每个表中的班级异常情况
def find_abnormal():
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    abnormal_data = []
    index = 0
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 加载答题日志表
        answer_log_df = pd.read_csv(file_path)
        # 获取第一行的class值
        first_class = answer_log_df.loc[0, "class"]
        # 找出所有跟第一行的class不一致的行
        inconsistent_rows = answer_log_df[answer_log_df["class"] != first_class]
        if not inconsistent_rows.empty:
            # 将不一致的行的class值设置为第一行的class值
            answer_log_df.loc[inconsistent_rows.index, "class"] = first_class
            print(first_class)
            print(inconsistent_rows)
        # abnormal_data.append(inconsistent_rows)
    # abnormal_data.to_csv("data/abnormal_data.csv", index=False)
    # print(abnormal_data)


# 整合题目表中的知识点
def question_merge():
    # 将大知识点和子知识点合并成一个知识点字符串
    question_info_df["knowledge"] = (
        question_info_df["knowledge"] + "," + question_info_df["sub_knowledge"]
    )
    question_info_df["knowledge"] = question_info_df["knowledge"].apply(lambda x: [x])
    # 将题目ID设置为唯一索引并合并重复题目ID的行并合并知识点
    question_info_df.set_index("title_ID", inplace=True)
    df_merged = (
        question_info_df.groupby(level=0)
        .agg({"score": "first", "knowledge": "sum"})
        .reset_index()
    )
    # 保存整合结果为 CSV 文件
    df_merged.to_csv("data/temporary/question_merged_data.csv", index=False)


# 将字典保存为JSON文件
def save_to_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


# 对每个班的日志信息按学生和题目进行合并，用于掌握程度计算分析
def student_title():
    question_info_df = pd.read_csv("data/temporary/question_merged_data.csv")
    index = 0
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 加载答题日志表
        data_info = pd.read_csv(file_path, dtype={"time": "int"})
        # 合并题目表
        merged_df = pd.merge(
            data_info,
            question_info_df,
            on="title_ID",
            how="left",
            suffixes=("", "_all"),
        )
        # 使用 defaultdict 来构建字典，初始值是一个空字典
        result_dict = defaultdict(dict)
        # 遍历答题日志表，按照学生id和题目id进行分组
        for _, row in merged_df.iterrows():
            student_id = row["student_ID"]
            question_id = row["title_ID"]

            # 检查学生id是否已经在字典中，如果不在，则将其添加进去
            if student_id not in result_dict:
                result_dict[student_id] = {}

            # 检查题目id是否已经在对应学生id的字典中，如果不在，则将其添加进去
            if question_id not in result_dict[student_id]:
                result_dict[student_id][question_id] = []

            # 将提交时间及其他字段的数据组成列表，添加到对应学生id和题目id的列表中
            result_dict[student_id][question_id].append(
                [
                    row["time"],
                    row["class"],
                    row["state"],
                    row["score"],
                    row["method"],
                    row["memory"],
                    row["timeconsume"],
                    row["score_all"],
                    row["knowledge"],
                ]
            )

        # 遍历结果字典，对每个学生id的题目id列表按提交时间进行排序
        for student_id in result_dict:
            for question_id in result_dict[student_id]:
                result_dict[student_id][question_id].sort(key=lambda x: x[0])
        # 保存为JSON文件
        save_to_json(
            result_dict, f"data/temporary/s-t-g/student_title_group{index}.json"
        )


def merge_student_title_group():
    # 指定文件夹路径
    folder_path = "data/temporary/s-m-f-n"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    all_student_title_group = {}
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取formatted_submission_counts数据
        with open(file_path, "r") as f:
            student_title_group = json.load(f)
        # 遍历每个学生的答题数据
        for student_id, answers in student_title_group.items():
            all_student_title_group[student_id] = answers
    # 保存为JSON文件
    save_to_json(
        all_student_title_group,
        f"data/temporary/s-m-f-n/all_student_merge_feature_normalized.json",
    )


# 将每个题对应的所有日志合并起来
def question_grouped():
    # 创建一个空的DataFrame来存放所有数据
    combined_data = pd.DataFrame()
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 加载答题日志表
        data_info = pd.read_csv(file_path)
        # 将数据按照题目ID合并到combined_data中
        combined_data = pd.concat([combined_data, data_info])
    # 根据题目ID进行排序
    combined_data = combined_data.sort_values(by="title_ID")
    # 保存为JSON文件
    combined_data.to_csv("data/temporary/question_combined_data.csv", index=False)


# 时间戳转换
def tranfor_time(unix_timestamp):
    # 使用datetime模块将Unix时间戳转换为具体的时间
    specific_time = datetime.datetime.utcfromtimestamp(unix_timestamp)
    # 打印转换后的具体时间
    print("具体时间:", specific_time)


# 获取每个学生每天针对多个题目的提交次数
def submit_count():
    index = 0
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 加载答题日志表
        student_logs_df = pd.read_csv(file_path)
        # 将提交时间（Unix时间戳）转换为具体的日期，并格式化日期为"YYYY-MM-DD"形式
        student_logs_df["time"] = pd.to_datetime(student_logs_df["time"], unit="s")
        student_logs_df["time"] = student_logs_df["time"].dt.strftime("%Y-%m-%d")
        # 按学生id分组，并对每个学生的答题日志按照提交时间进行排序
        grouped_logs = student_logs_df.groupby("student_ID").apply(
            lambda x: x.sort_values("time")
        )
        # 创建一个字典来保存每个学生在每天中提交每个题目的次数
        submission_counts = {}
        # 遍历分组后的数据，统计每个学生在每天中针对每个题目的提交次数
        for student_id, student_data in grouped_logs.groupby(level=0):
            submission_counts[student_id] = {}
            for date, date_data in student_data.groupby("time"):
                submission_counts[student_id][date] = {}
                for question_id in date_data["title_ID"]:
                    # 如果题目id不在日期的字典中，添加题目id
                    if question_id not in submission_counts[student_id][date]:
                        submission_counts[student_id][date][question_id] = 0
                    # 增加对应题目的提交次数
                    submission_counts[student_id][date][question_id] += 1

        # 保存为JSON文件
        save_to_json(
            submission_counts,
            f"data/temporary/s-s-c/student_submit_count{index}.json",
        )


# 查找哪个学生在哪天提交了最多的次数
def max_count():
    # 指定文件夹路径
    folder_path = "data/temporary/s-s-c"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    index = 0
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取formatted_submission_counts数据
        with open(file_path, "r") as f:
            formatted_submission_counts = json.load(f)
        # 定义变量来保存最多提交次数和对应的学生id和日期
        max_submissions = 0
        max_student_id = ""
        max_date = ""

        # 遍历每个学生和日期
        for student_id, student_data in formatted_submission_counts.items():
            for date, question_data in student_data.items():
                # 计算该学生在该日期提交的总次数
                total_submissions = sum(question_data.values())
                # 如果总次数大于之前记录的最多提交次数，则更新记录
                if total_submissions > max_submissions:
                    max_submissions = total_submissions
                    max_student_id = student_id
                    max_date = date

        # 打印结果
        print(
            "在Class",
            index,
            "中，",
            max_date,
            "，学生",
            max_student_id,
            "提交了最多次数：",
            max_submissions,
            "次",
        )


# 判断是否存在答题所得分数大于题目的满分分数的情况
def score_abnormal():
    # 指定文件夹路径
    folder_path = "data/temporary/s-t-g"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    index = 0
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取formatted_submission_counts数据
        with open(file_path, "r") as f:
            student_title_group = json.load(f)
        # 遍历每个学生的答题数据
        for student_id, answers in student_title_group.items():
            for question_id, answer in answers.items():
                for a in answer:
                    # 检查所得分数是否大于满分分数
                    if a[3] > a[7]:
                        print(
                            f"在Class{index}中，学生 {student_id} 答题异常，题目ID为 {question_id}，所得分数为 {a[3]}，满分分数为 {a[7]}"
                        )


# 查找学生中针对同一道题会有先对后错的情况，并通过次数
def first_right_then_wrong():
    # 指定文件夹路径
    folder_path = "data/temporary/s-t-g"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    index = 0
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 用于存储每个学生每个月出现先做对后做错情况的次数
        monthly_counts = defaultdict(int)
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取formatted_submission_counts数据
        with open(file_path, "r") as f:
            student_title_group = json.load(f)
        # 遍历每个学生的答题记录
        for student_id, answers in student_title_group.items():
            # 遍历每道题目的答题记录
            for question_id, answer_list in answers.items():
                # 将时间戳转换为月份
                month_logs = []
                # 判断是否存在情况
                flag = False
                # 初始化变量，用于跟踪是否先做对后做错
                correct_answered = False
                # 遍历每个答题记录
                for _, answer in enumerate(answer_list):
                    # 提取时间戳并转换为日期对象
                    timestamp = datetime.datetime.fromtimestamp(answer[0])
                    # 提取年月信息
                    year_month = timestamp.strftime("%Y-%m")
                    if year_month not in month_logs:
                        month_logs.append(year_month)
                    # # 如果答题状态为正确，并且之前已经有过正确答题记录，则增加该月份的计数
                    # if answer[2] == "Absolutely_Correct" and correct_answered:
                    #     monthly_counts[(student_id, year_month)] += 1
                    # 如果答题状态为正确，则更新correct_answered标志
                    if answer[2] == "Absolutely_Correct" and not flag:
                        correct_answered = True
                    # 如果答题状态为错误，则重置correct_answered标志
                    if (
                        answer[2]
                        in [
                            "Absolutely_Error",
                            "Error1",
                            "Error2",
                            "Error3",
                            "Error4",
                            "Error5",
                            "Error6",
                            "Error7",
                            "Error8",
                            "Error9",
                        ]
                        and correct_answered
                    ):
                        flag = True
                        correct_answered = False
                if flag:
                    monthly_counts[f"{student_id}_{question_id}"] = month_logs
        # 保存为JSON文件
        save_to_json(
            monthly_counts,
            f"data/temporary/f-r-t-w/first_right_then_wrong_count{index}.json",
        )


# 每个学生每月的总提交次数
def month_total_submit():
    # 指定文件夹路径
    folder_path = "data/temporary/s-s-c"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    index = 0
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 创建一个空字典，用于存储每个学生每个月的总提交次数
        monthly_counts = {}
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取formatted_submission_counts数据
        with open(file_path, "r") as f:
            student_submit_count = json.load(f)
        # 遍历每个学生的答题日志
        for student_id, daily_logs in student_submit_count.items():
            # 如果该学生的ID不在字典中，则将其添加到字典中
            if student_id not in monthly_counts:
                monthly_counts[student_id] = {}

            for date, question_logs in daily_logs.items():
                # 获取月份
                month = date[:7]  # 取年份和月份部分

                # 如果该月份不在学生字典中，则将其添加到字典中
                if month not in monthly_counts[student_id]:
                    monthly_counts[student_id][month] = 0
                # 统计该学生在该月份的总提交次数
                count = sum(question_logs.values())
                monthly_counts[student_id][month] += count
        # 保存为JSON文件
        save_to_json(
            monthly_counts,
            f"data/temporary/m-t-s/month_total_submit{index}.json",
        )


# 每个学生每月的活跃天数
def month_active_day():
    # 指定文件夹路径
    folder_path = "data/temporary/s-s-c"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 创建一个空字典，用于存储每个学生每个月的总提交次数
        monthly_counts = {}
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取formatted_submission_counts数据
        with open(file_path, "r") as f:
            student_submit_count = json.load(f)
        # 遍历每个学生的答题日志
        for student_id, daily_logs in student_submit_count.items():
            # 如果该学生的ID不在字典中，则将其添加到字典中
            if student_id not in monthly_counts:
                monthly_counts[student_id] = {}

            for date, question_logs in daily_logs.items():
                # 获取月份
                month = date[:7]  # 取年份和月份部分
                # 如果该月份不在学生字典中，则将其添加到字典中
                if month not in monthly_counts[student_id]:
                    monthly_counts[student_id][month] = 0
                monthly_counts[student_id][month] += 1
        # 保存为JSON文件
        save_to_json(
            monthly_counts,
            f"data/temporary/m-a-d/month_active_day{index}.json",
        )


# 每个学生每月的上、中、下旬提交次数
def ten_days_total_submit():
    # 指定文件夹路径
    folder_path = "data/temporary/s-s-c"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    index = 0
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 创建一个空字典，用于存储每个学生每个月的总提交次数
        monthly_counts = {}
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取formatted_submission_counts数据
        with open(file_path, "r") as f:
            student_submit_count = json.load(f)
        # 遍历每个学生的答题日志
        for student_id, daily_logs in student_submit_count.items():
            # 如果该学生的ID不在字典中，则将其添加到字典中
            if student_id not in monthly_counts:
                monthly_counts[student_id] = {}

            for date_str, question_logs in daily_logs.items():
                # 获取月份
                month = date_str[:7]  # 取年份和月份部分
                # 如果该月份不在学生字典中，则将其添加到字典中
                if month not in monthly_counts[student_id]:
                    monthly_counts[student_id][month] = [0, 0, 0]
                adate = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                # 判断旬份
                if adate.day <= 10:
                    monthly_counts[student_id][month][0] += sum(question_logs.values())
                elif adate.day <= 20:
                    monthly_counts[student_id][month][1] += sum(question_logs.values())
                else:
                    monthly_counts[student_id][month][2] += sum(question_logs.values())

        # 保存为JSON文件
        save_to_json(
            monthly_counts,
            f"data/temporary/t-d-t-s/ten_days_total_submit{index}.json",
        )


# 每个学生每月的上、中、下旬提交最高峰
def ten_days_max_submit():
    # 指定文件夹路径
    folder_path = "data/temporary/s-s-c"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    index = 0
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 创建一个空字典，用于存储每个学生每个月的总提交次数
        monthly_counts = {}
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取formatted_submission_counts数据
        with open(file_path, "r") as f:
            student_submit_count = json.load(f)
        # 遍历每个学生的答题日志
        for student_id, daily_logs in student_submit_count.items():
            # 如果该学生的ID不在字典中，则将其添加到字典中
            if student_id not in monthly_counts:
                monthly_counts[student_id] = {}

            for date_str, question_logs in daily_logs.items():
                # 获取月份
                month = date_str[:7]  # 取年份和月份部分
                # 如果该月份不在学生字典中，则将其添加到字典中
                if month not in monthly_counts[student_id]:
                    monthly_counts[student_id][month] = [0, 0, 0]
                adate = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                max_question_count = sum(question_logs.values())
                # 判断旬份
                if adate.day <= 10:
                    monthly_counts[student_id][month][0] = max(
                        monthly_counts[student_id][month][0], max_question_count
                    )
                elif adate.day <= 20:
                    monthly_counts[student_id][month][1] = max(
                        monthly_counts[student_id][month][1], max_question_count
                    )
                else:
                    monthly_counts[student_id][month][2] = max(
                        monthly_counts[student_id][month][2], max_question_count
                    )

        # 保存为JSON文件
        save_to_json(
            monthly_counts,
            f"data/temporary/t-d-m-s/ten_days_max_submit{index}.json",
        )


# 每个学生每个月的上、中、下旬答题数目
def month_answer_question_number():
    # 指定文件夹路径
    folder_path = "data/temporary/s-s-c"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    index = 0
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 创建一个空字典，用于存储每个学生每个月的总提交次数
        monthly_list = {}
        monthly_counts = {}
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取formatted_submission_counts数据
        with open(file_path, "r") as f:
            student_submit_count = json.load(f)
        # 遍历每个学生的答题日志
        for student_id, daily_logs in student_submit_count.items():
            # 如果该学生的ID不在字典中，则将其添加到字典中
            if student_id not in monthly_counts:
                monthly_counts[student_id] = {}
            if student_id not in monthly_list:
                monthly_list[student_id] = {}
            for date_str, question_logs in daily_logs.items():
                # 获取月份
                month = date_str[:7]  # 取年份和月份部分
                # 如果该月份不在学生字典中，则将其添加到字典中
                if month not in monthly_counts[student_id]:
                    monthly_counts[student_id][month] = [0, 0, 0]
                if month not in monthly_list[student_id]:
                    monthly_list[student_id][month] = [[], [], []]
                adate = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                if adate.day <= 10:
                    for key in question_logs.keys():
                        monthly_list[student_id][month][0].append(key)
                    monthly_counts[student_id][month][0] = len(
                        set(monthly_list[student_id][month][0])
                    )
                elif adate.day <= 20:
                    for key in question_logs.keys():
                        monthly_list[student_id][month][1].append(key)
                    monthly_counts[student_id][month][1] = len(
                        set(monthly_list[student_id][month][1])
                    )
                else:
                    for key in question_logs.keys():
                        monthly_list[student_id][month][2].append(key)
                    monthly_counts[student_id][month][2] = len(
                        set(monthly_list[student_id][month][2])
                    )
        # 保存为JSON文件
        save_to_json(
            monthly_counts,
            f"data/temporary/m-a-q-n/month_answer_question_number{index}.json",
        )


# 每个学生每个月的答题状态次数
def month_question_state_count():
    # 指定文件夹路径
    folder_path = "data/temporary/s-t-g"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    index = 0
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 用于存储每个学生每个月出现先做对后做错情况的次数
        monthly_counts = defaultdict(int)
        correct_prppotion = defaultdict(int)
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取数据
        with open(file_path, "r") as f:
            student_title_group = json.load(f)
        # 遍历每个学生的答题记录
        for student_id, answers in student_title_group.items():
            # 遍历每道题目的答题记录
            for _, answer_list in answers.items():
                # 如果该学生的ID不在字典中，则将其添加到字典中
                if student_id not in monthly_counts:
                    monthly_counts[student_id] = {}
                # 遍历每个答题记录
                for _, answer in enumerate(answer_list):
                    # 提取时间戳并转换为日期对象
                    timestamp = datetime.datetime.fromtimestamp(answer[0])
                    # 提取年月信息
                    year_month = timestamp.strftime("%Y-%m")
                    # 如果该月份不在学生字典中，则将其添加到字典中
                    if year_month not in monthly_counts[student_id]:
                        monthly_counts[student_id][year_month] = [0, 0, 0]
                    if answer[2] == "Absolutely_Correct":
                        monthly_counts[student_id][year_month][0] += 1
                    elif answer[2] == "Partially_Correct":
                        monthly_counts[student_id][year_month][1] += 1
                    else:
                        monthly_counts[student_id][year_month][2] += 1

        # 遍历monthly_counts记录
        for student_id, month_list in monthly_counts.items():
            print(month_list)
            if student_id not in correct_prppotion:
                correct_prppotion[student_id] = {}
            # 遍历每道题目的答题记录
            for year_month, status_list in month_list.items():
                print(status_list)
                if year_month not in correct_prppotion[student_id]:
                    correct_prppotion[student_id][year_month] = 0
                propotion = (status_list[0] + status_list[1]) / sum(status_list)
                correct_prppotion[student_id][year_month] = propotion
        # 保存为JSON文件
        save_to_json(
            correct_prppotion,
            f"data/temporary/m-q-s-c/month_question_state_count{index}.json",
        )


def month_prefer_language():
    # 指定文件夹路径
    folder_path = "data/temporary/s-t-g"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    index = 0
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 用于存储每个学生每个月出现先做对后做错情况的次数
        monthly_counts = defaultdict(int)
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取数据
        with open(file_path, "r") as f:
            student_title_group = json.load(f)
        # 遍历每个学生的答题记录
        for student_id, answers in student_title_group.items():
            # 遍历每道题目的答题记录
            for _, answer_list in answers.items():
                # 如果该学生的ID不在字典中，则将其添加到字典中
                if student_id not in monthly_counts:
                    monthly_counts[student_id] = {}
                # 遍历每个答题记录
                for _, answer in enumerate(answer_list):
                    # 提取时间戳并转换为日期对象
                    timestamp = datetime.datetime.fromtimestamp(answer[0])
                    # 提取年月信息
                    year_month = timestamp.strftime("%Y-%m")
                    # 如果该月份不在学生字典中，则将其添加到字典中
                    if year_month not in monthly_counts[student_id]:
                        monthly_counts[student_id][year_month] = [0, 0, 0, 0, 0]
                    if answer[4] == "Method_5Q4KoXthUuYz3bvrTDFm":
                        monthly_counts[student_id][year_month][0] += 1
                    elif answer[4] == "Method_BXr9AIsPQhwNvyGdZL57":
                        monthly_counts[student_id][year_month][1] += 1
                    elif answer[4] == "Method_Cj9Ya2R7fZd6xs1q5mNQ":
                        monthly_counts[student_id][year_month][2] += 1
                    elif answer[4] == "Method_gj1NLb4Jn7URf9K2kQPd":
                        monthly_counts[student_id][year_month][3] += 1
                    else:
                        monthly_counts[student_id][year_month][4] += 1
        # final_result = {}
        # for student_id, month_list in monthly_counts.items():
        #     # 如果该学生的ID不在字典中，则将其添加到字典中
        #     if student_id not in final_result:
        #         final_result[student_id] = {}
        #     # 遍历每道题目的答题记录
        #     for month_id, method_count in month_list.items():
        #         # 如果该月份不在学生字典中，则将其添加到字典中
        #         if month_id not in final_result[student_id]:
        #             final_result[student_id][month_id] = ""
        #         # 找到 monthly_counts[student_id][year_month] 中的最大值及其索引
        #         max_value = max(method_count)
        #         max_index = method_count.index(max_value)
        #         if max_index == 0:
        #             final_result[student_id][month_id] = "Method_5Q4KoXthUuYz3bvrTDFm"
        #         elif max_index == 1:
        #             final_result[student_id][month_id] = "Method_BXr9AIsPQhwNvyGdZL57"
        #         elif max_index == 2:
        #             final_result[student_id][month_id] = "Method_Cj9Ya2R7fZd6xs1q5mNQ"
        #         elif max_index == 3:
        #             final_result[student_id][month_id] = "Method_gj1NLb4Jn7URf9K2kQPd"
        #         else:
        #             final_result[student_id][month_id] = "Method_m8vwGkEZc3TSW2xqYUoR"

        # # 保存为JSON文件
        # save_to_json(
        #     final_result,
        #     f"data/temporary/m-p-l/month_prefer_language{index}.json",
        # )
        save_to_json(
            monthly_counts,
            f"data/temporary/m-p-l/month_use_language_count{index}.json",
        )


def student_merge_feature():
    # 指定文件夹路径
    folder_path = "data/integration"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    index = 0
    # count = 0
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    # 针对这几个月进行聚类
    date_str = ["2023-09", "2023-10", "2023-11", "2023-12", "2024-01"]
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # count += 1
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 创建一个空字典，用于存储转换后的数据
        student_dict = {}
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 加载答题日志表
        answer_log_df = pd.read_csv(file_path)
        answer_log_df = answer_log_df.drop_duplicates(subset="student_ID")
        # 将性别映射为0和1
        answer_log_df["sex"] = answer_log_df["sex"].map({"female": 0, "male": 1})
        # # 对年龄进行最小-最大归一化
        # scaler = MinMaxScaler(feature_range=(0, 1))
        # answer_log_df["age"] = scaler.fit_transform(answer_log_df[["age"]])
        # 对专业进行编码
        answer_log_df["major"] = answer_log_df["major"].map(
            {"J23517": 0, "J40192": 1, "J57489": 2, "J78901": 3, "J87654": 4}
        )
        # 遍历表格的行
        for _, row in answer_log_df.iterrows():
            # 提取每行数据的学生 ID 和其它信息
            student_id = row["student_ID"]
            if student_id not in student_dict:
                student_dict[student_id] = {}
            info = [row["sex"], row["age"], row["major"]]
            # 将学生ID、日期和其它信息添加到字典中
            for date in date_str:
                if date not in student_dict[student_id]:
                    student_dict[student_id][date] = []
                student_dict[student_id][date] = info
        # if count == 1:
        #     print(len(student_dict))
        #     break

        # merged_dict = {}
        # # 指定文件夹路径
        # folder_path1 = "data/temporary/t-d-t-s"
        # # 定义正则表达式模式，匹配文件名中的数字部分
        # pattern1 = r"\d+"
        # index1 = 0
        # # 获取文件夹下所有文件的文件名
        # file_names1 = os.listdir(folder_path1)
        # for file_name in file_names1:
        #     # 使用正则表达式进行匹配
        #     match1 = re.search(pattern1, file_name)
        #     if match1:
        #         # 如果找到匹配的数字，则提取并打印
        #         index1 = match1.group()
        #     # 拼接文件的完整路径
        #     file_path = os.path.join(folder_path1, file_name)
        #     # 从JSON文件中读取数据
        #     with open(file_path, "r") as f:
        #         other_dict = json.load(f)
        #     if index1 == index:
        #         # 遍历第二个字典中的每个学生ID和对应的日期列表
        #         for student_id, date_info in student_dict.items():
        #             if student_id in other_dict:
        #                 other_student = other_dict[student_id]
        #                 # 遍历日期列表中的每个日期和对应的值
        #                 for date, values in date_info.items():
        #                     alen = len(next(iter(other_student.values())))
        #                     if date in other_student:
        #                         data1 = other_student[date]
        #                         student_dict[student_id][date] = values + data1
        #                     else:
        #                         student_dict[student_id][date] = values + [0] * alen
        #         break
        student_dict = multipe_merge("data/temporary/t-d-t-s", student_dict, index)
        student_dict = multipe_merge("data/temporary/m-a-d", student_dict, index)
        # student_dict = multipe_merge("data/temporary/t-d-m-s", student_dict, index)
        student_dict = multipe_merge("data/temporary/m-a-q-n", student_dict, index)
        student_dict = multipe_merge("data/temporary/m-q-s-c", student_dict, index)
        # student_dict = multipe_merge("data/temporary/m-p-l", student_dict, index)
        save_to_json(
            student_dict,
            f"data/temporary/s-m-f/student_merge_feature{index}.json",
        )


def multipe_merge(folder_path, student_dict, index):
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    index1 = 0
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    parts = folder_path.split("/")
    result = "/".join(parts[2:])
    alen = 3
    if result == "m-a-d" or result == "m-q-s-c":
        alen = 1
    if result == "m-p-l":
        alen = 5
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index1 = match.group()
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取数据
        with open(file_path, "r") as f:
            other_dict = json.load(f)
        if index1 == index:
            # 遍历第二个字典中的每个学生ID和对应的日期列表
            for student_id, date_info in student_dict.items():
                if student_id in other_dict:
                    other_student = other_dict[student_id]
                    # 遍历日期列表中的每个日期和对应的值
                    for date, values in date_info.items():
                        if date in other_student:
                            data1 = other_student[date]
                            if alen == 1:
                                student_dict[student_id][date] = values + [data1]
                            else:
                                student_dict[student_id][date] = values + data1
                        else:
                            student_dict[student_id][date] = values + [0] * alen
            break
    return student_dict


def find_min_max():
    # 指定文件夹路径
    folder_path = "data/temporary/m-q-s-c"
    # folder_path = "data/temporary/m-p-l"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    top_min = 1000
    top_max = 0
    middle_min = 1000
    middle_max = 0
    bottom_min = 1000
    bottom_max = 0
    # a_min = 1000
    # a_max = 0
    # b_min = 1000
    # b_max = 0
    # c_min = 1000
    # c_max = 0
    # d_min = 1000
    # d_max = 0
    # e_min = 1000
    # e_max = 0
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取数据
        with open(file_path, "r") as f:
            file_json_data = json.load(f)
        # 遍历每个学生的答题日志
        for _, month_logs in file_json_data.items():
            # 遍历每道题目的答题记录
            for _, month_list in month_logs.items():
                top_min = min(top_min, month_list[0])
                top_max = max(top_max, month_list[0])
                middle_min = min(middle_min, month_list[1])
                middle_max = max(middle_max, month_list[1])
                bottom_min = min(bottom_min, month_list[2])
                bottom_max = max(bottom_max, month_list[2])
                # a_min = min(a_min, month_list[0])
                # a_max = max(a_max, month_list[0])
                # b_min = min(b_min, month_list[1])
                # b_max = max(b_max, month_list[1])
                # c_min = min(c_min, month_list[2])
                # c_max = max(c_max, month_list[2])
                # d_min = min(d_min, month_list[3])
                # d_max = max(d_max, month_list[3])
                # e_min = min(e_min, month_list[4])
                # e_max = max(e_max, month_list[4])
    print(
        "上旬：",
        [top_min, top_max],
        "中旬：",
        [middle_min, middle_max],
        "下旬：",
        [bottom_min, bottom_max],
    )
    # print(
    #     "完全正确：",
    #     [top_min, top_max],
    #     "部分正确：",
    #     [middle_min, middle_max],
    #     "错误：",
    #     [bottom_min, bottom_max],
    # )
    # print(
    #     "a：",
    #     [a_min, a_max],
    #     "b：",
    #     [b_min, b_max],
    #     "c：",
    #     [c_min, c_max],
    #     "d：",
    #     [d_min, d_max],
    #     "e：",
    #     [e_min, e_max],
    # )


def find_min_max1():
    # 指定文件夹路径
    folder_path = "data/temporary/m-a-d"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    min_value = 1000
    max_value = 0
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取数据
        with open(file_path, "r") as f:
            file_json_data = json.load(f)
        # 找出最大值和最小值
        all_values = [
            value
            for inner_dict in file_json_data.values()
            for value in inner_dict.values()
        ]
        max_value = max(max(all_values), max_value)
        min_value = min(min(all_values), min_value)
    print("最小值:", min_value, "最大值:", max_value)


def min_max(x, min_value, max_value):
    # 归一化处理
    normalized_values = (
        (x - min_value) / (max_value - min_value) if max_value != min_value else 0
    )
    return normalized_values


def min_max_feature():
    # 指定文件夹路径
    folder_path = "data/temporary/s-m-f"
    # 定义正则表达式模式，匹配文件名中的数字部分
    pattern = r"\d+"
    index = 0
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 使用正则表达式进行匹配
        match = re.search(pattern, file_name)
        if match:
            # 如果找到匹配的数字，则提取并打印
            index = match.group()
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取数据
        with open(file_path, "r") as f:
            file_json_data = json.load(f)
        # 创建一个空字典，用于存储转换后的数据
        student_dict = {}
        # 遍历每个学生的答题日志
        for student_id, month_data in file_json_data.items():
            if student_id not in student_dict:
                student_dict[student_id] = {}
            # 遍历每道题目的答题记录
            for month_id, month_list in month_data.items():
                if month_id not in student_dict[student_id]:
                    student_dict[student_id][month_id] = [0] * 21
                student_dict[student_id][month_id][0] = month_list[0]
                student_dict[student_id][month_id][1] = month_list[1]
                student_dict[student_id][month_id][2] = month_list[2]
                student_dict[student_id][month_id][3] = min_max(month_list[3], 0, 372)
                student_dict[student_id][month_id][4] = min_max(month_list[4], 0, 426)
                student_dict[student_id][month_id][5] = min_max(month_list[5], 0, 245)
                student_dict[student_id][month_id][6] = min_max(month_list[6], 0, 30)
                student_dict[student_id][month_id][7] = min_max(month_list[7], 0, 166)
                student_dict[student_id][month_id][8] = min_max(month_list[8], 0, 190)
                student_dict[student_id][month_id][9] = min_max(month_list[9], 0, 144)
                student_dict[student_id][month_id][10] = min_max(month_list[10], 0, 38)
                student_dict[student_id][month_id][11] = min_max(month_list[11], 0, 38)
                student_dict[student_id][month_id][12] = min_max(month_list[12], 0, 38)
                student_dict[student_id][month_id][13] = min_max(month_list[13], 0, 130)
                student_dict[student_id][month_id][13] = min_max(month_list[13], 0, 188)
                student_dict[student_id][month_id][13] = min_max(month_list[13], 0, 411)
                student_dict[student_id][month_id][13] = min_max(month_list[13], 0, 112)
                student_dict[student_id][month_id][13] = min_max(month_list[13], 0, 123)
                student_dict[student_id][month_id][13] = min_max(month_list[13], 0, 129)
                student_dict[student_id][month_id][13] = min_max(month_list[13], 0, 116)
                student_dict[student_id][month_id][13] = min_max(month_list[13], 0, 117)
        save_to_json(
            student_dict,
            f"data/temporary/s-m-f/student_merge_feature_normalized{index}.json",
        )


# 将整合的特征按月放到一个特征矩阵中
def tranfer_to_matrix():
    # 指定文件夹路径
    folder_path = "data/temporary/s-m-f"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    # 提取所有学生的ID
    student_ids = set()
    # 提取所有月份
    months = set()
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 从JSON文件中读取数据
        with open(file_path, "r") as f:
            data_dict = json.load(f)
        student_ids.update(data_dict.keys())
        for student_data in data_dict.values():
            months.update(student_data.keys())
    # 对月份排序
    months = sorted(months)
    student_ids = sorted(student_ids)
    # 创建矩阵
    matrix = []
    for month in months:
        month_data = []
        for student_id in student_ids:
            # 如果学生在该月有数据，则添加该数据；否则添加0
            student_month_data = []
            # 循环遍历文件夹下的每个文件
            for file_name in file_names:
                # 拼接文件的完整路径
                file_path = os.path.join(folder_path, file_name)
                # 从JSON文件中读取数据
                with open(file_path, "r") as f:
                    data_dict = json.load(f)
                if student_id in data_dict:
                    student_data = data_dict[student_id]
                    if month in student_data:
                        student_month_data.extend([student_data[month]])

            month_data.extend(student_month_data)
        matrix.append(month_data)
    save_to_json(
        matrix,
        f"data/temporary/month_student_feature.json",
    )


# 对特征进行标准化
def standard_feature():
    with open("data/temporary/month_student_feature.json", "r") as f:
        big_list = json.load(f)
    # 对每个月份的特征进行标准化
    scalers = []  # 存储每个月份的标准化器
    normalized_big_list = []  # 存储标准化后的特征向量

    for month_data in big_list:
        month_data_array = np.array(month_data)  # 转换为NumPy数组
        scaler = StandardScaler()
        scaler.fit(month_data_array)  # 用每个月份的数据来拟合标准化器
        scalers.append(scaler)  # 存储标准化器
        normalized_month_data = scaler.transform(
            month_data_array
        )  # 对每个月份的特征向量进行标准化
        normalized_big_list.append(
            normalized_month_data.tolist()
        )  # 存储标准化后的特征向量
    save_to_json(
        normalized_big_list,
        f"data/temporary/month_student_feature_normalized.json",
    )


def try_cluster():
    # 假设你的特征矩阵是一个numpy数组
    with open("data/temporary/month_student_feature_normalized.json", "r") as f:
        big_list = json.load(f)
    features = np.array(big_list[0])
    # # 使用DBSCAN进行密度聚类
    # dbscan = DBSCAN(eps=3, min_samples=2)  # 设置半径和最小样本数
    # labels = dbscan.fit_predict(features)
    # # 绘制聚类结果图
    # plt.figure(figsize=(8, 6))
    # # 绘制每个簇的数据点
    # for label in np.unique(labels):
    #     if label == -1:
    #         plt.scatter(
    #             features[labels == label][:, 0],
    #             features[labels == label][:, 1],
    #             c="black",
    #             marker="x",
    #             label="Noise",
    #         )
    #     else:
    #         plt.scatter(
    #             features[labels == label][:, 0],
    #             features[labels == label][:, 1],
    #             label=f"Cluster {label}",
    #         )
    # # 使用PCA进行降维
    # pca = PCA(n_components=2)
    # reduced_features = pca.fit_transform(features)
    # 使用t-SNE进行降维
    tsne = TSNE(n_components=2, random_state=0)
    reduced_features = tsne.fit_transform(features)
    # 使用KMeans进行聚类
    kmeans = KMeans(n_clusters=3, random_state=0).fit(reduced_features)
    # 获取聚类标签
    labels = kmeans.labels_
    # 绘制散点图
    plt.scatter(
        reduced_features[:, 0], reduced_features[:, 1], c=labels, s=50, cmap="viridis"
    )
    # 显示图像
    plt.savefig("my_figure.png")


def student_to_tag():
    # 假设你的特征矩阵是一个numpy数组
    with open("data/temporary/cluster.json", "r") as f:
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


# integrate()
# question_merge()
# student_title()
# question_grouped()
# tranfor_time(1703997737)
# submit_count()
# find_abnormal()
# max_count()
# score_abnormal()
# first_right_then_wrong()
# month_total_submit()
# month_active_day()
# ten_days_total_submit()
# ten_days_max_submit()
# month_answer_question_number()
# merge_student_title_group()
# month_question_state_count()
# month_prefer_language()
# find_min_max()
# find_min_max1()
# student_merge_feature()
# min_max_feature()
# tranfer_to_matrix()
# standard_feature()
# try_cluster()
student_to_tag()
