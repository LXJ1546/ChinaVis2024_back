from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
# 允许跨域传输数据
CORS(app)


@app.route('/back')
def hello():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
