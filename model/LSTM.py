import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture
from sklearn.manifold import TSNE

# 生成示例数据
num_students = 1000
num_months = 30
num_features = 4

# 生成随机示例数据
data = np.random.rand(num_students, num_months, num_features)
print(data)

# 划分训练集和测试集
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

# 将数据转换为张量
train_data_tensor = torch.tensor(train_data, dtype=torch.float32)
test_data_tensor = torch.tensor(test_data, dtype=torch.float32)
all_data = torch.tensor(data, dtype=torch.float32)

# class TimeSeriesModel(nn.Module):
#     def __init__(self, input_size, hidden_size, num_layers, dropout_rate, output_size):
#         super(TimeSeriesModel, self).__init__()
#         self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout_rate)
#         self.fc = nn.Linear(hidden_size, output_size)
        
#     def forward(self, x):
#         lstm_out, _ = self.lstm(x)
#         output = self.fc(lstm_out[:, -1, :])
#         return output

# 定义模型参数
input_size = num_features
hidden_size = 16
num_layers = 2
dropout_rate = 0.2
output_size = 1

# # 创建模型实例
# model = TimeSeriesModel(input_size, hidden_size, num_layers, dropout_rate, output_size)


# # 模型训练
# num_epochs = 100
# for epoch in range(num_epochs):
#     model.train()
#     optimizer.zero_grad()
#     outputs = model(train_data_tensor)
#     # loss = criterion(outputs.squeeze(), torch.randn(train_data_tensor.size(0)))
#     # 生成与模型输出相同维度的随机张量作为目标张量
#     target = torch.randn_like(outputs)
#     loss = criterion(outputs.squeeze(), target)
#     loss.backward()
#     optimizer.step()
#     print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")

# # 模型评估
# model.eval()
# with torch.no_grad():
#     test_outputs = model(test_data_tensor)
#     # 生成与模型输出相同维度的随机张量作为目标张量
#     target = torch.randn_like(outputs)
#     test_loss = criterion(outputs.squeeze(), target)
#     # test_loss = criterion(test_outputs.squeeze(), torch.randn(test_data_tensor.size(0)))
#     print(f"Test Loss: {test_loss.item():.4f}")

# # 特征提取
# model.eval()
# with torch.no_grad():
#     feature_vectors = model(all_data)
#     print("Feature vectors shape:", feature_vectors.shape)
#     print(feature_vectors)
#     print(feature_vectors[:, -1, :])

class TimeSeriesModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, dropout_rate, output_size):
        super(TimeSeriesModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout_rate)
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        # 返回整个时间序列的隐藏状态
        return lstm_out

# 创建模型实例
model = TimeSeriesModel(input_size, hidden_size, num_layers, dropout_rate, output_size)

# 定义损失函数和优化器
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 模型训练
num_epochs = 100
for epoch in range(num_epochs):
    model.train()
    optimizer.zero_grad()
    outputs = model(train_data_tensor)
    target = torch.randn_like(outputs)
    loss = criterion(outputs.squeeze(), target)
    loss.backward()
    optimizer.step()
    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")

# 模型评估
model.eval()
with torch.no_grad():
    test_outputs = model(test_data_tensor)
    target = torch.randn_like(test_outputs)
    test_loss = criterion(test_outputs.squeeze(), target)
    print(f"Test Loss: {test_loss.item():.4f}")

# 特征提取
model.eval()
with torch.no_grad():
    feature_vectors = model(all_data)
    print("Feature vectors shape:", feature_vectors.shape)
    # print(feature_vectors)
    last_hidden_state = feature_vectors[:, -1, :]
    print(last_hidden_state)


#聚类可视化
def visualize_clusters(features, num_clusters):
    # # 使用 KMeans 对高维特征进行聚类
    # kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    # cluster_labels = kmeans.fit_predict(features)
    # 使用高斯混合模型进行聚类
    # gmm = GaussianMixture(n_components=num_clusters)
    gmm = GaussianMixture(n_components=num_clusters, random_state=42)
    cluster_labels = gmm.fit_predict(features)
    # print(cluster_labels)
    tsne = TSNE(n_components=2, random_state=42)
    projected_features = tsne.fit_transform(features)
    # 绘制聚类可视化图
    plt.figure(figsize=(8, 6))
    plt.scatter( projected_features [:, 0], projected_features [:, 1], c=cluster_labels, cmap='viridis')
    plt.title('Cluster Visualization')
    plt.xlabel('t-SNE Component 1')
    plt.ylabel('t-SNE Component 2')
    plt.colorbar(label='Cluster')
    plt.show()

visualize_clusters(last_hidden_state,num_clusters = 3)