import random
from flask import request, jsonify, session, Blueprint, g, make_response, render_template, redirect
from . import user
from ..utils.tool import user_login_required, crossdomain
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from Database import *
from flask_cors import cross_origin


@user.after_request
def func_res(resp):
    res = make_response(resp)
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'GET,POST,DELETE,PUT'
    res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return res


# 用户初始页面
@user.route('/index', methods=['GET'])
# @user_login_required
def index():
    if request.method == 'GET':
        return render_template("index.html")


@user.route('/indexsucess', methods=['GET', 'POST'])
@user_login_required
def indexsucess():
    if request.method == 'GET':
        return render_template("indexsucess.html")


# 用户注册界面
@user.route('/register', methods=['POST', 'GET'])
def register():
    """
    用户名
    密码
    确认密码
    :return:
    """
    if request.method == 'GET':
        return render_template("register.html")
    elif request.method == 'POST':
        data = request.form
        username = data.get("username")
        password = data.get("password")
        password2 = data.get("password2")

        # 校验参数
        if not all([username, password, password2]):
            return jsonify(msg="参数不完整", code=4002)

        if password != password2:
            return jsonify(msg="两次密码不一致", code=4001)

        user_id = add_user(users(is_author=False, user_name=username, password=password))
        print(user_id)
        avatar = "D:/python/translation_system/app/static/file/20220330171454_36.jpg"  # 这里是默认头像
        # 保存登陆状态到session中
        session["username"] = username
        session["user_id"] = user_id
        session["user_avatar"] = avatar

        # 返回结果
        return jsonify(msg="注册成功", user_id=user_id, code=200)


# 用户登录接口
@user.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template("enroll.html")
    elif request.method == 'POST':
        data = request.form
        user_id = data.get("user_id")
        password = data.get('password')
        if not all([user_id, password]):
            return jsonify(msg='缺少参数', code=4000)
        else:
            if login_user(user_id, password):
                # 如果验证通过保持登录状态在session中
                session["user_id"] = user_id
                username = select_user(user_id).get("user_name")
                session["username"] = username
                return jsonify(msg='登陆成功', code=200, user_id=user_id)
            else:
                return jsonify(msg='账号或密码错误', code=4000)


# 检查登录状态
@user.route('/session', methods=['GET'])
def check_session():
    username = session.get("username")
    avatar = session.get("avatar")
    user_id = session.get("user_id")
    user_describe = session.get("user_describe")
    if username is not None:
        '''
        这里就可以进行数据库的一些查询操作，然后将用户信息返回给前端
        例如 用户名 密码 id 等级 认证等
        '''
        return jsonify(user_id=user_id, username=username, avatar=avatar, user_describe=user_describe, code=200)
    else:
        return jsonify(msg='未登录', code=400)


# 退出登录
@user.route('/logout', methods=['DELETE'])
@user_login_required  # 验证用户登录的装饰器
def logout():
    if request.method == 'DELETE':
        session.clear()
        return jsonify(msg="成功退出登录", code=200)


# 修改密码
@user.route('/password', methods=['PUT'])
@user_login_required  # 验证用户登录装的饰器
def change_password():
    if request.method == 'PUT':
        uid = g.user_id
        data = request.form
        password = data.get("password")
        new_password = data.get("new_password")

        # 校验参数完整
        if not all([new_password, password, uid]):
            return jsonify(msg="参数不完整", code=4000)

        """这里开始查找这个id
        如果查不到则返回jsonify(msg="获取用户信息失败", code=4000)"""

        # 用数据库里的密码与用户输入的密码进行对比验证
        if user is None or user.password != password:
            return jsonify(msg="原始密码错误", code=4000)

        # 修改密码
        user.password = new_password

        """这里将新密码存进数据库里"""

        return jsonify(msg="修改密码成功", code=200)


# 查询用户信息
@user.route('/profile/<int:user_id>', methods=["GET"])
def get_profile(user_id):
    if request.method == 'GET':
        if not user_id:
            return jsonify(msg='参数不完整', code=4000)
        """这里通过用户的id查询用户的参数"""
        try:
            data = {select_user(user_id)}  # data保存查询的用户信息
        except Exception as e:
            print(e)
            return jsonify(msg='查询寻不到用户', code=4001)
        return jsonify(msg="查询用户信息成功", data=data, code=200)


# 用户个人信息界面
@user.route('/user_information', methods=['GET'])
def user_information():
    if request.method == 'GET':
        return render_template('userinformation.html')


# 用户修改信息
@user.route('/userinformation/modification', methods=['POST', 'GET'])
@user_login_required  # 验证用户登录的装饰器
def updata_user_information():
    if request.method == 'GET':
        return render_template('checkinformation.html')
    if request.method == 'POST':
        # 从管道获取user的id
        # user_id = g.user_id
        # 获取用户修改的信息
        data = request.form
        username = data.get('username')
        user_id = data.get('user_id')
        user_describe = data.get('user_describe')

        # 获取用户上传的头像图片文件
        image_file = request.files.get("file")
        # 获取安全的文件名
        filename = secure_filename(image_file.filename)
        # 获取上上级路径
        basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        # 文件重命名
        # filename.rsplit('.', 1)[1] 获取文件名的后缀
        filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + str(random.randint(0, 100)) + "." + \
                   filename.rsplit('.', 1)[1]
        file_path = basedir + "/app/static/file/" + filename
        if image_file is None:
            return jsonify(msg="未上传图片", code=4000)
        try:
            image_file.save(file_path)
            my_host = "http://127.0.0.1:5000"
            avatar_url = my_host + "/static/file/" + filename
        except Exception as e:
            print(e)
            return jsonify(msg="上传图片失败", code=4001)

        """随后通过数据库对头像进行修改"""

        # 保存成功并返回
        session["avatar"] = avatar_url
        session["user_id"] = user_id
        session["username"] = username
        session["user_describe"] = user_describe
        return jsonify(mag="保存成功", data={"avatar": avatar_url}, code=200)


# 用户修改密码
@user.route('/checkpassword')
def checkpassword():
    return render_template("checkpassword.html")

# 搜索
@user.route('/book/search/<int:page>', methods=['POST'])
def book_search(page):
    if request.method == 'POST':
        keyword = request.form.get("keyword")
        if not page:
            page = 1
        else:
            page = int(page)
        if keyword is None:
            return jsonify(msg='请输入搜索内容', code=4000)

        """这里根据keyword对数据库进行搜索查询"""

        books = None  # 数据库中搜寻到的书籍相关内容保存到books里
        payload = [book.to_dict() for book in books]
        return jsonify(msg='搜索结束', data=payload, code=200)


# 书籍简介
@user.route('/read_book/introduce/<int:book_id>', methods=['GET', 'POST'])
def read_book_index():
    if request.method == 'GET':
        return render_template("bookintroduce.html")
    elif request.method == 'POST':
        data = request.form
        book_id = data.get("book_id")

        """这里返回书籍的所有信息"""

        return jsonify(msg="这是书籍的所有信息", code=200)


# # 开始阅读
# @user.route('/read_book/start_read')
# def start_read():
#     """查询书籍的内容"""
#     book = bookLib()
#     data = request.get_json()
#     book_id = data.get("book_id")
#     """这里返回书籍的内容与章节"""
#     return jsonify(book.lib[book_id].bInfo, code=200)

# 译者翻译界面
@user.route('/author/translate', methods=['GET'])
def translate_book():
    data = request.get_json()
    book_id = data.get("book_id")
    author_id = data.get("author_id")

    """查询书籍章节内容"""

    return jsonify(code=200)


# 判断该用户是否为译者
@user.route('/judge_author', methods=['GET'])
@user_login_required  # 验证用户登录的装饰器
def judge_author():
    user_id = g.user_id
    data = request.get_json()
    user_id = data.get("user_id")
    user_name = data.get("user_name")
    # user = user(user_id=user_id, user_name=user_name)

    """通过数据库查询该用户的is_author"""

    is_author = True
    if not is_author:
        return jsonify(msg="该用户还不是译者", code=4000)
    return jsonify(msg="该用户是译者", code=200)


# 用户注册译者界面
@user.route('/author_register', methods=['POST'])
@user_login_required
def author_register():
    data = request.get_json()
    author_name = data.get("author_name")
    user_id = data.get("user_id")
    # author = authores(user_id=user_id, author_name=author_name)
    # add_author(author, user_id)
    return jsonify(msg="恭喜你成为译者", code=200)


@user.route('/addbooks')
def addbooks():
    return render_template("addbooks.html")
# @user.route('/author/translate', methods=['GET'])
# @user_login_required
# def translate_book():
#     data = request.get_data()
#     user_id = g.user_id
#
#     basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
