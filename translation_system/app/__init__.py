from flask import Flask
from Config import config_map
from flask_cors import *


def create_app(config_name):
    """
    返回一个实例化并且配置好的app
    config_name: 选择环境的参数
    """
    app = Flask(__name__)
    # CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    # 这里需要实例化数据库

    # Session(app)  # 利用flask_session,将session数据保存到redis中
    app.secret_key = "12fa12f13f1fbb589wh4"

    # 注册蓝图

    from app import user

    app.register_blueprint(user.user, url_prefix='/user')  # 用户蓝图
    return app
