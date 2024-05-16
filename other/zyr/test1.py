# 查看数据分布？

from scipy.stats import norm  # 使用直方图和最大似然高斯分布拟合绘制分布
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option('display.width', 1000)
# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)


sns.set(context='notebook', font='simhei', style='whitegrid')
# 设置风格尺度和显示中文

warnings.filterwarnings('ignore')  # 不发出警告

# 直方图

# 选择要保留的字段# 读取数据
desired_columns = ['student_ID', 'title_ID', 'time', 'memory']
file = "F:/vscode/vis24/data/combined_data.csv"
df = pd.read_csv(file, low_memory=False)
condition = df['timeconsume'] == '--'
df['timeconsume'] = pd.to_numeric(df['timeconsume'], errors='coerce')
df['timeconsume'].loc[condition] = 10000


step = 10
# 划分区间并统计每个区间的数据个数
bins = range(int(df['timeconsume'].min()), int(
    df['timeconsume'].max()) + step, step)
binned_data = pd.cut(df['timeconsume'], bins)
bin_counts = binned_data.value_counts().sort_index()

# 打印每个区间的数据个数
print(bin_counts)
