from app import create_app
from flask_script import Manager  # 管理项目的，额外指定一些命令
from flask_migrate import Migrate, command  # 管理数据库需要的脚本，追踪数据库的变化的脚本

app = create_app("develop")

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0',port=8000)
