import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import torch.optim as optim
import numpy as np

import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import torch.optim as optim
import numpy as np

class DKTDataSet(Dataset):
    def __init__(self, data):
        """
        :param data: 包含元组列表，每个元组格式为(question_id, knowledge_points, attempts)
            - question_id: int, 题目ID
            - knowledge_points: list of ints, 关联的知识点
            - attempts: list of ints, 每次尝试的答题结果（1正确，0错误）
        """
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        question_id, knowledge_points, attempts = self.data[idx]
        return question_id, knowledge_points, attempts

# 示例数据
data = [
    (1, [0, 1], [0, 0, 1]),
    (2, [1, 2], [1, 1, 0]),
    (3, [1, 2], [1]),
    (4, [0, 3], [0, 0, 0]),
    (5, [3], [1])
]

dataset = DKTDataSet(data)
dataloader = DataLoader(dataset, batch_size=1, shuffle=True)


class DKTModel(nn.Module):
    def __init__(self, num_questions, num_knowledge_points, hidden_dim):
        super(DKTModel, self).__init__()
        self.hidden_dim = hidden_dim
        self.embed_question = nn.Embedding(num_questions, hidden_dim)
        self.lstm = nn.LSTM(hidden_dim, hidden_dim)
        self.out = nn.Linear(hidden_dim, num_knowledge_points)  # 输出预测每个知识点掌握概率

    def forward(self, question_id, knowledge_points, attempts):
        question_embed = self.embed_question(torch.tensor(question_id)).repeat(len(attempts), 1)
        attempts_embed = torch.tensor(attempts).unsqueeze(1).float().repeat(1, self.hidden_dim)  # 扩展尝试状态为相同维度
        lstm_input = question_embed + attempts_embed  # 使用加和来合并信息
        lstm_out, _ = self.lstm(lstm_input.unsqueeze(1))
        logits = self.out(lstm_out.squeeze(1))
        predictions = torch.sigmoid(logits)
        return predictions

model = DKTModel(num_questions=6, num_knowledge_points=4, hidden_dim=128)


criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 目标标签构建
def build_targets(attempts, knowledge_points, num_knowledge_points):
    # 初始化目标矩阵，每一行对应一次尝试，每一列对应一个知识点，数据类型为 float
    targets = torch.zeros((len(attempts), num_knowledge_points), dtype=torch.float)

    # 标记每次尝试后的知识点掌握情况
    for i in range(len(attempts)):
        for kp in knowledge_points:
            targets[i, kp] = float(attempts[i])  # 确保赋值为 float 类型
    return targets


# for epoch in range(10):
#     for question_id, knowledge_points, attempts in dataloader:
#         optimizer.zero_grad()
#         predictions = model(torch.tensor([question_id]), knowledge_points, torch.tensor(attempts))
#         print(predictions)
#         targets = build_targets(attempts, knowledge_points, model.out.out_features)
#         loss = criterion(predictions, targets)
#         loss.backward()
#         optimizer.step()
#     print(f"Epoch {epoch+1}, Loss: {loss.item()}")

def train_and_collect_mastery(model, dataloader, epochs, criterion, optimizer):
    mastery_records = []  # 初始化一个列表来存储掌握程度记录

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for question_id, knowledge_points, attempts in dataloader:
            optimizer.zero_grad()
            
            # 获取模型输出
            outputs = model(torch.tensor([question_id]), knowledge_points, torch.tensor(attempts))
            targets = build_targets(attempts, knowledge_points, model.out.out_features)

            # 计算损失
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

            # 收集每个批次的掌握程度信息
            mastery_records.append(outputs.detach().cpu().numpy())  # 将输出添加到记录中

        print(f"Epoch {epoch+1}, Total Loss: {total_loss:.2f}")

    return mastery_records

# 使用自定义的训练函数
mastery_data = train_and_collect_mastery(model, dataloader, epochs=10, criterion=nn.BCEWithLogitsLoss(), optimizer=torch.optim.Adam(model.parameters(), lr=0.001))
print(mastery_data)


