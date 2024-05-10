# 检查是否存在前一题对了，后面错了
import pandas as pd
import json
import os
from collections import defaultdict

# pd.set_option("display.width", 1000)
# # 显示所有列
# pd.set_option("display.max_columns", None)
# # 显示所有行
# pd.set_option("display.max_rows", None)


# 定义一个函数，对每个组进行排序
def sort_by_timestamp(group):
    return group.sort_values("time", ascending=True)


def zyr_grouped():
    # 选择要保留的字段
    desired_columns = ["student_ID", "title_ID", "time", "state"]

    # 读取数据
    data = pd.read_csv("data/Data_SubmitRecord/SubmitRecord-Class1.csv")
    # 按学生id和题目id分组，并统计每个组的答题状态变化情况
    data = data[desired_columns]
    grouped_data = data.groupby(["student_ID", "title_ID"]).apply(sort_by_timestamp)[
        [
            "student_ID",
            "time",
            "state",
        ]
    ]
    # 保存整合结果为 CSV 文件
    grouped_data.to_csv("data/temporary/student_title_group.csv", index=False)
    # grouped_data = data.groupby(['student_ID', 'title_ID']).apply(
    #     sort_by_timestamp).reset_index(drop=True)

    # for i in grouped_data:
    #     print(i)

    # 输出结果
    # print(grouped_data)


# 将字典保存为JSON文件
def save_to_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


# 对每个班的日志信息按学生和题目进行合并，用掌握程度计算分析
def student_title():
    question_info_df = pd.read_csv("data/temporary/question_merged_data.csv")
    # 指定文件夹路径
    folder_path = "data/Data_SubmitRecord"
    # 获取文件夹下所有文件的文件名
    file_names = os.listdir(folder_path)
    index = 0
    # 循环遍历文件夹下的每个文件
    for file_name in file_names:
        index += 1
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file_name)
        # 加载答题日志表
        data_info = pd.read_csv(file_path)
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
                    row["method"],
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
        save_to_json(result_dict, f"data/temporary/student_title_group{index}.json")


student_title()
