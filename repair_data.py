import json

# 首先，读取现有的 JSON 数据
with open('backup.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 修改数据，设置某些字段为 null
for item in data:
    if item['model'] == 'design.dictionaryfields':
        item['fields']['vocabulary'] = None

# 写入修改后的数据到文件
with open('backup.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=4)  # 使用indent参数使JSON文件格式化，便于阅读
