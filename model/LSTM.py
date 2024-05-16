import torch
import torch.nn as nn

class TimeSeriesModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(TimeSeriesModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        # x 的形状：(batch_size, seq_length, input_size)
        lstm_out, _ = self.lstm(x)
        # 取最后一个时间步的输出作为模型的输出
        output = self.fc(lstm_out[:, -1, :])
        return output

# 定义模型参数
input_size = 4  # 输入特征的维度
hidden_size = 16  # LSTM 隐藏层的维度
output_size = 1  # 输出特征的维度

# 创建时间序列模型实例
model = TimeSeriesModel(input_size, hidden_size, output_size)

# 打印模型结构
print(model)

import numpy as np

# 生成示例数据
num_students = 3
num_months = 6
num_features = 4

# 生成随机示例数据
data = np.random.rand(num_students, num_months, num_features)

print("示例数据：")
print(data)
print("示例数据形状：", data.shape)
