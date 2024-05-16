import json

# 创建一个空的字典，用于存放所有 JSON 数据
merged_data = {}

# 循环遍历 x1.json, x2.json, x3.json
for i in range(1, 15):
    file_name = f'data/s-m-f/student_merge_feature{i}.json'
    # 读取每个 JSON 文件并合并到 merged_data 字典中
    with open(file_name, 'r') as f:
        data = json.load(f)
        merged_data.update(data)

# 将合并后的数据写入新的 JSON 文件中
output_file_path = 'merged_data.json'
with open(output_file_path, 'w') as f:
    json.dump(merged_data, f, indent=4)

print("Merged data saved to:", output_file_path)
