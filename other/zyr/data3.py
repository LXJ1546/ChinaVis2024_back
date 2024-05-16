# 用时内存归一化
# 要将内存为0的删除，为了防止影响数据分布
# 时间将--删除
from sklearn.neighbors import KernelDensity
import numpy as np
from sklearn.preprocessing import RobustScaler
import pandas as pd

# 假设 data 是你的 DataFrame，column_name 是你要归一化的列的名称
# 例如，将 'column_name' 替换为你实际使用的列名称

# 选择要保留的字段# 读取数据
desired_columns = ['student_ID', 'title_ID', 'time', 'memory']
file = "F:/vscode/vis24/data/combined_data.csv"
Compete_data = pd.read_csv(file, low_memory=False)


# column_name = 'memory'

# # 获取要归一化的列的数据
# data = Compete_data[column_name].values

# # 对数据进行排序
# sorted_data = np.sort(data[data != 0])

# # 计算累积分布函数
# cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)

# # 将归一化后的数据添加到DataFrame的新列中
# Compete_data[column_name + '_normalized'] = np.where(
#     data != 0, np.interp(data, sorted_data, cdf), 0)

# # 输出带有归一化结果的DataFrame
# print(Compete_data)

# 假设df是你的DataFrame，column_name是你想要进行归一化的列名

# column_name = 'memory'

# # 获取要归一化的列的数据
# data = Compete_data[column_name].values

# # 训练KDE模型
# kde = KernelDensity(kernel='gaussian', bandwidth=0.75).fit(
#     data[data != 0].reshape(-1, 1))

# # 生成一组用于归一化的数据点
# x = np.linspace(np.min(data[data != 0]), np.max(
#     data[data != 0]), 1000).reshape(-1, 1)

# # 计算KDE估计的概率密度函数值
# log_density = kde.score_samples(x)

# # 对于每个数据点，计算其对应的概率密度函数值，并做归一化
# normalized_data = np.where(data != 0, np.interp(
#     data, x.flatten(), np.exp(log_density)), 0)

# # 将归一化后的数据添加到DataFrame的新列中
# Compete_data[column_name + '_normalized'] = normalized_data

# # 输出带有归一化结果的DataFrame
# print(Compete_data)


# 假设df是你的DataFrame，column_name是你想要进行归一化的列名

column_name = 'memory'

# 获取要归一化的列的数据
data = Compete_data[column_name].values

file_path = 'output.csv'
# 对数据进行对数变换
log_data = np.where(data != 0, np.log(data), 0)  # 归一化对数变换后的数据
log_data = pd.DataFrame(log_data)
log_data.to_csv(file_path, index=False)
normalized_data = np.where(
    data != 0, (log_data - np.min(log_data)) / (np.max(log_data) - np.min(log_data)), 0)

# 将归一化后的数据添加到DataFrame的新列中
Compete_data[column_name + '_normalized'] = normalized_data

# 输出带有归一化结果的DataFrame
# print(Compete_data)

# file_path = 'output.csv'
# Compete_data.to_csv(file_path, index=False)
