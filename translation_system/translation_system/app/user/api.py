import random
from flask import request, jsonify, session, g, make_response, render_template, url_for
from . import user
from ..utils.tool import user_login_required
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from Database import *


@user.after_request
def func_res(resp):
    res = make_response(resp)
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'GET,POST,DELETE,PUT'
    res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return res


# 游客首页
@user.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template("index.html", )


# 普通用户首页
@user.route('/indexsucess', methods=['GET', 'POST'])
@user_login_required
def indexsucess():
    if request.method == 'GET':
        return render_template("indexsucess.html")


# 译者用户首页
@user.route('/indexsucessauthor', methods=['GET', 'POST'])
@user_login_required
def idexsucessauthor():
    if request.method == 'GET':
        return render_template('indexsucessauothor.html')


# 用户注册界面
@user.route('/register', methods=['POST', 'GET'])
def register():
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
        avatar = url_for('static', filename='img/b2.jpg')  # 这里是默认头像
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
                is_author = select_user(user_id).get("is_author")
                if not is_author:
                    return jsonify(msg="登录成功", code=200)
                else:
                    return jsonify(msg='登录成功', code=202)
            else:
                return jsonify(msg='账号或密码错误', code=4000)


# 检查登录状态
@user.route('/session', methods=['GET'])
def check_session():
    user_id = session.get("user_id")
    username = session.get("user_name")
    user_gender = session.get("gender")
    user_birthday = session.get("birthday")
    user_area = session.get("area")
    user_describe = session.get("user_describe")
    user_avatar = session.get("picture")
    is_author = session.get("is_author")
    if user_id is not None:
        return jsonify(username=username, user_birthday=user_birthday, user_area=user_area,
                       user_gender=user_gender, user_describe=user_describe, user_avatar=user_avatar,
                       is_author=is_author, user_id=user_id, code=200)
    else:
        return jsonify(msg='未登录', code=4000)


# 退出登录
@user.route('/logout', methods=['DELETE'])
@user_login_required  # 验证用户登录的装饰器
def logout():
    if request.method == 'DELETE':
        session.clear()
        return jsonify(msg="成功退出登录", code=200)


###########################################################################################


# 查看用户个人信息界面
@user.route('/readerinformation', methods=['GET'])
@user_login_required
def user_information():
    if request.method == 'GET':
        try:
            user_id = g.user_id
            data = select_user(user_id)
        except Exception as e:
            print(e)
            return jsonify("查不到该用户或该用户未登录", code=4000)
        username = data.get("user_name")
        user_gender = data.get("gender")
        user_birthday = data.get("birthday")
        user_area = data.get("area")
        user_describe = data.get("user_describe")
        user_avatar = data.get("picture")
        is_author = data.get("is_author")
        return render_template('readerinformation.html',
                               username=username, user_birthday=user_birthday, user_area=user_area,
                               user_gender=user_gender, user_describe=user_describe, user_avatar=user_avatar,
                               is_author=is_author, user_id=user_id)


# 修改密码
@user.route('/sucesscheckpassword', methods=['POST', 'GET'])
@user_login_required  # 验证用户登录装的饰器
def change_password():
    if request.method == 'POST':
        uid = g.user_id
        data = request.form
        password = data.get("password")
        new_password = data.get("new_password")
        # 校验参数完整
        if not all([new_password, password, uid]):
            return jsonify(msg="参数不完整", code=4000)

        try:
            data_user = select_user(uid)
        except Exception as e:
            print(e)
            return jsonify(msg="获取用户信息失败", code=4000)
        # 用数据库里的密码与用户输入的密码进行对比验证
        if password != data_user.get("password"):
            return jsonify(msg="原始密码错误", code=4000)

        # 修改密码
        update_user(uid, {"password": new_password})
        is_author = session.get("is_author")
        if not is_author:
            return jsonify(msg='修改密码成功', code=200)
        else:
            return jsonify(msg="修改密码成功", code=202)
    if request.method == 'GET':
        return render_template("sucesscheckpassword.html")


# 用户修改基本信息
@user.route('/userinformation/modification', methods=['POST', 'GET'])
@user_login_required  # 验证用户登录的装饰器
def update_user_information():
    if request.method == 'GET':
        return render_template('checkinformation.html')
    if request.method == 'POST':
        # 从管道获取user的id
        user_id = g.user_id
        # 获取用户修改的信息
        data = request.form
        username = data.get("user_name")
        user_gender = data.get("gender")
        user_birthday = data.get("birthday")
        user_area = data.get("area")
        user_describe = data.get("user_describe")
        # 保存成功并返回
        session["username"] = username
        session["user_describe"] = user_describe
        session["user_gender"] = user_gender
        session["user_birthday"] = user_birthday
        session["user_area"] = user_area
        new_data = {
            "user_id": user_id,
            "user_gender": user_id,
            "user_birthday": user_birthday,
            "user_area": user_area,
            "user_describe": user_describe,
        }
        return jsonify(mag="保存成功", data=new_data, code=200)


# 用户修改头像  需要有一个单独的提交头像文件的页面
@user.route('/userinformation/modification/update_avatar', methods=['POST', 'GET'])
@user_login_required
def update_user_avatar():
    if request.method == 'GET':
        return render_template("checkinformation.html")
    if request.method == 'POST':
        user_id = g.user_id
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
        file_path = basedir + "/app/static/avatar_file/" + filename
        if image_file is None:
            return jsonify(msg="未上传图片", code=4000)
        try:
            image_file.save(file_path)
            my_host = "http://127.0.0.1:5000"
            avatar_url = my_host + "/static/avatar_file/" + filename
        except Exception as e:
            print(e)
            return jsonify(msg="上传图片失败", code=4001)
        session["user_avatar"] = avatar_url
        update_user(user_id, {"picture": avatar_url})
        return jsonify(msg="修改头像成功", user_avatar=avatar_url, code=200)


###################################################################################################
# 搜索
@user.route('/book/search', methods=['POST'])
def book_search(lang_id):
    if request.method == 'POST':
        keyword = request.form.get("keyword")
        if keyword is None:
            return jsonify(msg='请输入搜索内容', code=4000)
        books = search_chinesebook(keyword)  # 数据库中搜寻到的书籍相关内容保存到books里
        payload = [book.to_dict() for book in books]
        return jsonify(msg='搜索结束', data=payload, code=200)


# 书籍简介
@user.route('/read_book/introduce/<int:book_id>/<int:author_id>/<int:lang_id>', methods=['GET', 'POST'])
def read_book_index(book_id, author_id, lang_id):
    if request.method == 'GET':
        if lang_id == 1:
            book_name = select_chinesebook(book_id, author_id, lang_id).get('name')
            book_describe = select_chinesebook(book_id, author_id, lang_id).get('desc')
            cover_path = select_book(book_id, author_id, lang_id).get("cover_name")
        elif lang_id == 2:
            book_name = select_englishbook(book_id, author_id, lang_id).get('name')
            book_describe = select_englishbook(book_id, author_id, lang_id).get('desc')
            cover_path = select_book(book_id, author_id, lang_id).get("cover_name")
        elif lang_id == 3:
            book_name = select_japanesebook(book_id, author_id, lang_id).get('name')
            book_describe = select_japanesebook(book_id, author_id, lang_id).get('desc')
            cover_path = select_book(book_id, author_id, lang_id).get("cover_name")
        author_name = select_author_by_author_id(author_id).get("author_name")
        return render_template("bookintroduce.html", book_name=book_name, author_name=author_name,
                               book_describe=book_describe, cover_path=cover_path)


# 开始阅读
@user.route('/read_book/start_read/<int:book_id>/<int:lang_id>/<int:author_id>/<int:content>', methods=['GET'])
def start_read(book_id, lang_id, author_id, content):
    if request.method == 'GET':
        title = select_content(book_id, author_id, lang_id, content).get('title')
        text_path = select_content(book_id, author_id, lang_id, content).get('text_path')
        content_file = open(text_path, 'r', encoding='utf-8')
        content_file_text = content_file.read()
        content_file.close()
        return render_template("bookreading.html", content_file_text=content_file_text, title=title)


###############################################################################################

# 判断该用户是否为译者
@user.route('/judge_author', methods=['GET'])
@user_login_required  # 验证用户登录的装饰器
def judge_author():
    is_author = session.get("is_author")
    if not is_author:
        return jsonify(msg="该用户还不是译者", code=4000)
    return jsonify(msg="该用户是译者", code=200)


# 用户注册译者界面
@user.route('/author_register', methods=['POST', 'GET'])
@user_login_required
def author_register():
    if request.method == 'POST':
        data = request.form
        author_name = data.get("author_name")
        user_id = g.user_id
        try:
            author = authores(author_name=author_name, user_id=user_id)
            author_id = add_author(author, user_id)
        except Exception as e:
            print(e)
            return jsonify(msg="注册译者失败", code=4000)
        update_user(user_id, {"is_author": True})
        session['is_author'] = True
        return jsonify(msg="恭喜你成为译者", author_id=author_id, code=200)
    elif request.method == 'GET':
        return render_template("registeraouthor.html")


# 查看译者信息
@user.route('/authorinfo', methods=['POST', 'GET'])
@user_login_required
def readerinformation():
    if request.method == 'GET':
        try:
            user_id = g.user_id
            data = select_author_by_user_id(user_id)
        except Exception as e:
            print(e)
            return jsonify("查不到该用户或该用户未登录", code=4000)
        author_id = data.get('author_id')
        author_name = data.get('author_name')
        author_describe = data.get('author_describe')

        return render_template('authorinfo.html',
                               author_name=author_name, author_id=author_id, author_describe=author_describe,
                               )


# 作者首页
@user.route('/author_index', methods=['POST', 'GET'])
@user_login_required
def author_index():
    if request.method == 'GET':
        return render_template('indexsucessauothor.html')


# 文本文件读写时记得要设置utf-8格式

# 作者添加书籍选项页面
@user.route('/author/add_books_index', methods=['POST', 'GET'])
@user_login_required
def author_add_books_index():
    if request.method == 'GET':
        user_id = g.user_id
        author_id = select_author_by_user_id(user_id).get('author_id')
        return render_template("addbooks.html", author_id=author_id)
    elif request.method == 'POST':
        user_id = g.user_id
        author_id = select_author_by_user_id(user_id).get('author_id')
        data = request.form
        book_name = data.get("book_name")
        book_lang = int(data.get("book_lang"))
        book_class_id = int(data.get("book_class_id"))
        book_describe = data.get("book_describe")

        try:
            book_id = add_book(booklib(author_id=author_id, book_lang=book_lang, bc_id=book_class_id))
            if book_lang == 1:
                add_chinese_book(
                    chinesebooklib(b_id=book_id, author_id=author_id, book_lang=book_lang, name=book_name,
                                   desc=book_describe), book_id,
                    author_id, book_lang)
            elif book_lang == 2:
                add_english_book(
                    englishbooklib(b_id=book_id, author_id=author_id, book_lang=book_lang, name=book_name,
                                   desc=book_describe), book_id,
                    author_id, book_lang)
            elif book_lang == 3:
                add_japanese_book(
                    japanesebooklib(b_id=book_id, author_id=author_id, book_lang=book_lang, name=book_name,
                                    desc=book_describe), book_id,
                    author_id, book_lang)
        except Exception as e:
            print(e)
            return jsonify(msg="建立新书失败请重试", code=4000)
        return jsonify(msg="建立新书成功", code=200, book_id=book_id, author_id=author_id, book_lang=book_lang)


# 作者上传书籍封面
@user.route('/author/add_cover/<int:book_id>/<int:lang_id>', methods=['GET', 'POST'])
@user_login_required
def add_cover(book_id, lang_id):
    if request.method == 'GET':
        return render_template("")
    elif request.method == 'POST':
        author_id = select_author_by_user_id(g.user_id).get('author_id')
        cover_file = request.files.get("cover_file")
        filename = secure_filename(cover_file.filename)
        basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        # 获取该lang的英文名
        for i in select_all_english_lang_id():
            if i["lang_id"] == lang_id:
                book_lang = i["englishlang"]
        book_dir_name = str(book_id) + '_' + str(author_id)
        book_lang_dir_name = str(book_lang)
        # 如果没有原始语言目录就创建
        if not os.path.exists(basedir + "/app/static/book_file/" + book_lang_dir_name):
            os.mkdir(basedir + "/app/static/book_file/" + book_lang_dir_name)
            # 如果没有对应的书籍目录就创建
        if not os.path.exists(basedir + "/app/static/book_file/" + book_lang_dir_name + '/' + book_dir_name):
            os.mkdir(basedir + "/app/static/book_file/" + book_lang_dir_name + '/' + book_dir_name)
        cover_file_path = basedir + "/app/static/book_file/" + book_lang_dir_name + '/' + book_dir_name + "/" + filename
        cover_file_url = url_for('static',
                                 filename='book_file/' + book_lang_dir_name + '/' + book_dir_name + '/' + filename)
        update_book(book_id, author_id, book_lang, {"cover_path": cover_file_path})
        if cover_file is None:
            return jsonify(msg="未上传图片", code=4000)
        try:
            cover_file.save(cover_file_path)
            my_host = "http://127.0.0.1:5000"
            cover_url = my_host + "/app/static/book_file/" + book_lang_dir_name + '/' + book_dir_name + "/" + filename
        except Exception as e:
            print(e)
            return jsonify(msg="上传图片失败", code=4001)
        return jsonify(msg='上传图片成功', cover_url=cover_url, code=200)


# 作者添加书籍(只能是原始语言) (还需修改)!!!
@user.route('/author/addbooks/<int:book_id>/<int:lang_id>/<int:content>', methods=['GET', 'POST'])
@user_login_required
def add_books(book_id, lang_id, content):
    if request.method == 'GET':
        return render_template("addbookcontent.html")
    elif request.method == 'POST':
        data = request.form
        content_title = data.get("title")
        text = data.get("text")
        # 获取该lang的英文名
        for i in select_all_english_lang_id():
            if i["lang_id"] == lang_id:
                book_lang = i["englishlang"]

        author_id = select_author_by_user_id(g.user_id).get("author_id")
        book_lang_dir_name = str(book_lang)
        book_dir_name = str(book_id) + '_' + str(author_id)

        # 获取上上级路径
        basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        # 如果没有原始语言目录就创建
        if not os.path.exists(basedir + "/app/static/book_file/" + book_lang_dir_name):
            os.mkdir(basedir + "/app/static/book_file/" + book_lang_dir_name)
        # 如果没有对应的书籍目录就创建
        if not os.path.exists(basedir + "/app/static/book_file/" + book_lang_dir_name + '/' + book_dir_name):
            os.mkdir(basedir + "/app/static/book_file/" + book_lang_dir_name + '/' + book_dir_name)

        # 章节内容文件名
        content_filename = str(content) + '_' + str(content_title)

        content_file = open(
            basedir + "/app/static/book_file/" + book_lang_dir_name + '/' + book_dir_name + "/" + content_filename + '.txt',
            'w', encoding='utf-8')
        content_file.write(text)
        content_file.close()

        # 绝对路径
        book_file_path = basedir + "/app/static/book_file/" + book_lang_dir_name + '/' + book_dir_name
        content_file_path = basedir + "/app/static/book_file/" + book_lang_dir_name + '/' + book_dir_name + "/" + content_filename
        # 相对路径
        book_file_url = url_for('static', filename='book_file/' + book_lang_dir_name + '/' + book_dir_name)
        content_file_url = url_for('static',
                                   filename='book_file/' + book_lang_dir_name + '/' + book_dir_name + '/' + content_filename)

        print(book_id, author_id, lang_id)
        add_content(book_id, author_id, lang_id)
        if book_lang == 1:
            add_chinese_content(chinesecontent(b_id=book_id, author_id=author_id, book_lang=book_lang, c_no=content),
                                book_id, author_id, book_lang, content)
        elif book_lang == 2:
            add_english_content(englishcontent(b_id=book_id, author_id=author_id, book_lang=book_lang, c_no=content),
                                book_id, author_id, book_lang, content)
        elif book_lang == 3:
            add_japanese_content(japanesecontent(b_id=book_id, author_id=author_id, book_lang=book_lang, c_no=content),
                                 book_id, author_id, book_lang, content)

        return jsonify(msg="提交成功", book_file_path=book_file_url, content_file_path=content_file_url,
                       code=200)


# 译者翻译首页界面
@user.route('/author/translate_index', methods=['GET', 'POST'])
@user_login_required
def translate_index():
    if request.method == 'GET':
        return render_template("", )


# 译者翻译选项界面
@user.route('/author/translate_option/<int:book_id>/<int:o_author_id>/<int:lang_id>', methods=['GET', 'POST'])
@user_login_required
def translate_option(book_id, lang_id, o_author_id):
    if request.method == 'GET':
        # 获取该lang的中文名
        book_lang = select_chineselanguage(lang_id).get("chineselang")
        if lang_id == 1:
            book_name = select_chinesebook(book_id=book_id, author_id=o_author_id, lang_id=lang_id).get("name")
        elif lang_id == 2:
            book_name = select_englishbook(book_id=book_id, author_id=o_author_id, lang_id=lang_id).get("name")
        elif lang_id == 3:
            book_name = select_japanesebook(book_id=book_id, author_id=o_author_id, lang_id=lang_id).get("name")

        return render_template("", author_id=o_author_id, book_lang=book_lang, book_name=book_name)
    elif request.method == 'POST':
        user_id = g.user_id
        data = request.form
        book_name = data.get("name")
        # 选择要翻译的语言版本
        new_lang_id = int(data.get("new_lang_id"))
        author_id = select_author_by_user_id(user_id).get('author_id')
        if new_lang_id == lang_id:
            return jsonify(msg="您选择的语言版本与原始版本相同，请重新选择", code=4000)
        else:
            add_book_support_language(book_id, author_id, lang_id, new_lang_id)
            origin_book = select_book(book_id, author_id, lang_id)
            add_book(
                booklib(b_id=book_id, author_id=author_id, book_lang=new_lang_id, bc_id=origin_book.get("bc_id"),
                        support_lang=origin_book.get("support_lang")))
        if new_lang_id == 1:
            add_chinese_book(
                chinesebooklib(b_id=book_id, author_id=author_id, book_lang=lang_id, name=book_name
                               ), book_id,
                author_id, lang_id)
        elif new_lang_id == 2:
            add_english_book(
                englishbooklib(b_id=book_id, author_id=author_id, book_lang=lang_id, name=book_name
                               ), book_id,
                author_id, lang_id)
        elif new_lang_id == 3:
            add_japanese_book(
                japanesebooklib(b_id=book_id, author_id=author_id, book_lang=lang_id, name=book_name
                                ), book_id,
                author_id, lang_id)
        return jsonify(msg="可以开始翻译", code=200)


# 译者翻译界面
@user.route('/author/translate/<int:book_id>/<int:o_author_id>/<int:lang_id>/<int:translate_lang_id>/<int:content>',
            methods=['GET', 'POST'])
@user_login_required
def translate_book(book_id, translate_lang_id, lang_id, content, o_author_id):
    # 显示原文
    if request.method == 'GET':

        title = select_chinesecontent(book_id, o_author_id, lang_id, content).get('title')
        content_file_path = select_chinesecontent(book_id, o_author_id, lang_id, content).get('text_path')

        content_file = open(content_file_path, 'r', encoding='utf-8')
        content_file_text = content_file.read()
        content_file.close()

        return render_template('', content_file_text=content_file_text, title=title)
    # 提交译文
    elif request.method == 'POST':
        author_id = select_author_by_user_id(g.user_id).get("author_id")
        data = request.form
        content_text = data.get("text")
        title = data.get('title')
        # 获取该lang的英文名
        for i in select_all_english_lang_id():
            if i["lang_id"] == translate_lang_id:
                book_lang = i["englishlang"]
        book_dir_name = str(book_id) + '_' + str(author_id)
        book_lang_dir_name = str(book_lang)
        # 获取上上级路径
        basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

        # 如果没有原始语言目录就创建
        if not os.path.exists(basedir + "/app/static/book_file/" + book_lang_dir_name):
            os.mkdir(basedir + "/app/static/book_file/" + book_lang_dir_name)
        # 如果没有对应的书籍目录就创建
        if not os.path.exists(basedir + "/app/static/book_file/" + book_lang_dir_name + '/' + book_dir_name):
            os.mkdir(basedir + "/app/static/book_file/" + book_lang_dir_name + '/' + book_dir_name)

        # 章节内容文件名
        content_filename = str(content) + '_' + str(title)

        content_file_path = basedir + "/app/static/book_file/" + book_lang_dir_name + '/' + book_dir_name + "/" + content_filename + '.txt'
        # 将译文写进文本文件里
        content_file = open(content_file_path, 'w', encoding='utf-8')
        content_file.write(content_text)
        content_file.close()
        if translate_lang_id == 1:
            add_chinese_content(
                chinesecontent(b_id=book_id, author_id=author_id, book_lang=translate_lang_id, c_no=content,
                               title=title, text_path=content_file_path), book_id, author_id, lang_id, content)
        elif translate_lang_id == 2:
            add_english_content(
                englishcontent(b_id=book_id, author_id=author_id, book_lang=translate_lang_id, c_no=content,
                               title=title, text_path=content_file_path), book_id, author_id, lang_id, content)
        elif translate_lang_id == 3:
            add_japanese_content(
                japanesecontent(b_id=book_id, author_id=author_id, book_lang=translate_lang_id, c_no=content,
                                title=title, text_path=content_file_path), book_id, author_id, lang_id, content)
        return jsonify(msg="译文提交成功", code=200)
