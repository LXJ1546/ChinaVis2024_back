from flask import Flask
from flask_cors import CORS
import pandas as pd


app = Flask(__name__)
# 允许跨域传输数据
CORS(app)


@app.route('/back')
def hello():
    return 'Hello, World!'


@app.route('/basicInfo')
def basicInfo():
    # 后续需要根据班级获取不同班的数据
    file_temp = './data/classes/basic_info_'
    file = file_temp+'1.csv'
    data = pd.read_csv(file).sort_values(by='all_knowledge', ascending=False)
    result = []
    for index, row in data.iterrows():
        result.append([row['student_ID'], row['major'], row['age'],
                       row['sex'], row['all_knowledge'], 'class1'])
    # print(result)

    return (result)


if __name__ == '__main__':
    app.run(debug=True)
