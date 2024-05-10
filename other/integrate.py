import pandas as pd
import os

# 加载学生信息表和题目信息表
student_info_df = pd.read_csv("data/Data_StudentInfon.csv")
question_info_df = pd.read_csv("data/Data_TitleInfo.csv")
# 指定文件夹路径
folder_path = "data/Data_SubmitRecord"
# 获取文件夹下所有文件的文件名
file_names = os.listdir(folder_path)


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
    index = 0
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 加载答题日志表
        answer_log_df = pd.read_csv(file_path)
        index += 1
        # 去除 answer_log_df 中的重复 student_ID
        student_info_df1 = student_info_df.drop_duplicates(subset="student_ID")
        question_info_df1 = question_info_df.drop_duplicates(subset="title_ID")
        # 将答题日志表与学生信息表和题目信息表进行左连接
        merged_df = pd.merge(
            answer_log_df, student_info_df1, on="student_ID", how="left"
        )
        merged_df = pd.merge(merged_df, question_info_df1, on="title_ID", how="left")
        integrate_df = pd.DataFrame(merged_df)
        file_name = f"data/integration/integrated_data{index}.csv"
        integrate_df.to_csv(file_name, index=False)


# 找到每个表中的班级异常情况
def find_abnormal():
    abnormal_data = []
    index = 0
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        index += 1
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 加载答题日志表
        answer_log_df = pd.read_csv(file_path)
        # 获取第一行的class值
        first_class = answer_log_df.loc[0, "class"]
        # 找出所有跟第一行的class不一致的行
        inconsistent_rows = answer_log_df[answer_log_df["class"] != first_class]
        if not inconsistent_rows.empty:
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


# integrate()
question_merge()
