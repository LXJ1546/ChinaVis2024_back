#自编码器方法一
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
import json
from sklearn.cluster import DBSCAN
import tensorflow.keras.backend as K
from tensorflow.keras import regularizers
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.cluster import SpectralClustering
from sklearn.mixture import GaussianMixture
from minisom import MiniSom
# 假设特征矩阵为 features_matrix，每个学生的特征是一个一维数组
# 示例特征矩阵的形状为 (num_students, feature_size)
# 注意：确保特征矩阵已经被标准化或归一化处理
# 创建自编码器模型
# def build_autoencoder(input_shape, encoding_dim):
#     input_data = layers.Input(shape=input_shape)
#     encoded = layers.Dense(encoding_dim, activation='relu')(input_data)
#     decoded = layers.Dense(input_shape[0], activation='sigmoid')(encoded)  
#     autoencoder = models.Model(input_data, decoded)
#     encoder = models.Model(input_data, encoded)
#     autoencoder.compile(optimizer='adam', loss='contrastive_loss')
#     return autoencoder, encoder


def build_autoencoder(input_shape, encoding_dim):
    input_data = layers.Input(shape=input_shape)
    
    # 编码器
    encoded = layers.Dense(32, activation='relu')(input_data)
    encoded = layers.Dropout(0.2)(encoded) 
    encoded = layers.Dense(encoding_dim, activation='relu')(encoded)
    
    # 解码器
    decoded = layers.Dense(32, activation='relu')(encoded)
    decoded = layers.Dropout(0.2)(decoded)
    decoded = layers.Dense(input_shape[0], activation='sigmoid')(decoded)
    
    # 构建自编码器模型
    autoencoder = models.Model(input_data, decoded)
    encoder = models.Model(input_data, encoded)
    
    # # 定义对比损失函数
    # def contrastive_loss(y_true, y_pred):
    #     margin = 1
    #     return K.mean(y_true * K.square(y_pred) + (1 - y_true) * K.square(K.maximum(margin - y_pred, 0)))
    
    # 编译模型
    autoencoder.compile(optimizer='adam', loss='mean_squared_error')
    
    return autoencoder, encoder


# 划分训练集和测试集
def split_train_test(data, train_ratio=0.8):
    np.random.shuffle(data)
    split_index = int(train_ratio * len(data))
    train_data = data[:split_index]
    test_data = data[split_index:]
    return train_data, test_data

# 训练自编码器模型
def train_autoencoder(autoencoder, train_data, epochs=50, batch_size=16):
    autoencoder.fit(train_data, train_data, epochs=epochs, batch_size=batch_size, shuffle=True, verbose=1)

# 评估自编码器模型
def evaluate_autoencoder(autoencoder, test_data):
    loss = autoencoder.evaluate(test_data, test_data, verbose=0)
    print("Evaluation Loss:", loss)

# 使用自编码器进行特征提取
def extract_features(encoder, data):
    encoded_features = encoder.predict(data)
    return encoded_features

# 降维可视化
def visualize_tsne(features, labels=None):
    tsne = TSNE(n_components=2, random_state=42)
    projected_features = tsne.fit_transform(features)
    plt.figure(figsize=(8, 6))
    if labels is None:
        plt.scatter(projected_features[:, 0], projected_features[:, 1])
    else:
        for label in np.unique(labels):
            plt.scatter(projected_features[labels == label, 0], projected_features[labels == label, 1], label=label)
        plt.legend()
    plt.title('TSNE Visualization')
    plt.xlabel('TSNE Component 1')
    plt.ylabel('TSNE Component 2')
    plt.show()

#聚类可视化
def visualize_clusters(features, num_clusters):
    # # 使用 KMeans 对高维特征进行聚类
    # kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    # cluster_labels = kmeans.fit_predict(features)
    # 使用高斯混合模型进行聚类
    gmm = GaussianMixture(n_components=num_clusters, random_state=42)
    cluster_labels = gmm.fit_predict(features)
    print(cluster_labels)

    features_list = cluster_labels.tolist()  # 将NumPy数组转换为Python列表
    output_file_path = 'cluster.json'
    with open(output_file_path, 'w') as f:
        json.dump(features_list, f, indent=4)

    #使用 t-SNE 将聚类后的特征投影到二维空间
    tsne = TSNE(n_components=2, random_state=42)
    projected_features = tsne.fit_transform(features)
    # # 使用 PCA 将聚类后的特征投影到二维空间
    # pca = PCA(n_components=2, random_state=42)
    # projected_features = pca.fit_transform(features)

    # 绘制聚类可视化图
    plt.figure(figsize=(8, 6))
    plt.scatter( projected_features[:, 0], projected_features[:, 1], c=cluster_labels, cmap='viridis')
    plt.title('Cluster Visualization')
    plt.xlabel('t-SNE Component 1')
    plt.ylabel('t-SNE Component 2')
    plt.colorbar(label='Cluster')
    plt.show()


# def visualize_clusters(features):
#     # 使用 DBSCAN 对高维特征进行聚类
#     dbscan = DBSCAN(eps=3, min_samples=2)
#     cluster_labels = dbscan.fit_predict(features)

#     # 使用 t-SNE 将聚类后的特征投影到二维空间
#     tsne = TSNE(n_components=2, random_state=42)
#     projected_features = tsne.fit_transform(features)

#     # 绘制聚类可视化图
#     plt.figure(figsize=(8, 6))
#     plt.scatter(projected_features[:, 0], projected_features[:, 1], c=cluster_labels, cmap='viridis')
#     plt.title('Cluster Visualization')
#     plt.xlabel('t-SNE Component 1')
#     plt.ylabel('t-SNE Component 2')
#     plt.colorbar(label='Cluster')
#     plt.show()

# 使用示例
# visualize_clusters(your_features)


# # 示例数据
# features_matrix = np.random.rand(1000, 17)  # 100个学生，每个学生15个特征

# 读取 JSON 文件
with open('../data/month_student_feature_normalized(3).json', 'r') as file:
    data = json.load(file)
# print(data[0])
# # 新的数组用来存放符合条件的学生属性
# selected_students = []

# # 遍历每个学生
# for student_id, attributes in data.items():
#     # 检查学生是否有属性为"2023-09"
#     if '2023-09' in attributes:
#         selected_students.append(attributes['2023-09'])

# 输出结果
features_matrix = np.array(data[3])
# features_matrix = np.random.rand(1000, 17)  # 100个学生，每个学生50个特征
# print(features_matrix)
# 加载鸢尾花数据集
# iris = load_iris()
# X = iris.data   # 特征数据
# features_matrix = X

# # 获取特征数据和标签
# X = iris.data   # 特征数据
# y = iris.target  # 标签

# # 输出数据集的特征和标签数量
# print("特征数量:", X.shape[1])
# print("样本数量:", X.shape[0])
# print("标签类别数量:", len(set(y)))

# 示例数据
# num_students = 1000
# num_features = 17
# num_clusters = 5
# cluster_std =0.1
# features_matrix = generate_mixed_data(num_students, num_features, num_clusters, cluster_std)
# print(features_matrix)

# 构建自编码器模型
input_shape = (features_matrix.shape[1],)
# input_shape = (X.shape[1],)
encoding_dim = 11
autoencoder, encoder = build_autoencoder(input_shape, encoding_dim)
# autoencoder, encoder = build_autoencoder(input_shape)
# # 划分训练集和测试集
train_data, test_data = split_train_test(features_matrix)
# 划分训练集和测试集
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=42)

# 训练自编码器模型
train_autoencoder(autoencoder, train_data)

# 评估自编码器模型
evaluate_autoencoder(autoencoder,  test_data)

# 使用自编码器进行特征提取
encoded_features = extract_features(encoder, features_matrix)
# encoded_train_features = extract_features(encoder, train_data)
# encoded_test_features = extract_features(encoder, test_data)
print("Encoded features shape:", encoded_features.shape)
#鸢尾花数据集
# encoded_train_features = extract_features(encoder, X_train)
# encoded_test_features = extract_features(encoder, X_test)

# # 使用编码后的特征进行分类鸢尾花数据集测试
# clf = LogisticRegression(max_iter=1000)
# clf.fit(encoded_train_features, y_train)
# y_pred = clf.predict(encoded_test_features)
# # 计算分类准确率
# accuracy = accuracy_score(y_test, y_pred)
# print("分类准确率:", accuracy)

# # 输出特征提取结果
# print("编码后的特征提取结果：")
# print(encoded_features)

# 降维可视化
# visualize_tsne(encoded_features)

# 聚类可视化
visualize_clusters(features_matrix,num_clusters=4)
# visualize_clusters(encoded_features,num_clusters=4)

