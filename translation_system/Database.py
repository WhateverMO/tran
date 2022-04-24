from platform_database import *

user_id_pool_size = 400
user_id_pool_lock_size = 200
author_id_pool_size = 400
author_id_pool_lock_size = 200
book_id_pool_size = 400


def add_user_id_pool(n, sql, is_lock=False):
    ids = []
    for a in range(n):
        ids.append(useridpool(is_lock=is_lock))
    print("user " + ("locked " if is_lock else "") + "id 生成完毕 开始添加到数据库")
    sql.session.add_all(ids)


def collect_user_id(user_id, sql):
    sql.session.add(useridpool(user_id=user_id))


def del_a_user_id_from_pool(sql):
    res = sql.session.query(useridpool.user_id).count()
    if res < user_id_pool_lock_size:
        add_user_id_pool(user_id_pool_lock_size - res, sql, True)
    if res < user_id_pool_size:
        add_user_id_pool(user_id_pool_size - res, sql)
    ret = sql.session.query(useridpool.user_id).filter(useridpool.is_lock == False).first()[0]
    sql.session.query(useridpool).filter(useridpool.user_id == ret).delete()
    return ret


def add_author_id_pool(n, sql, is_lock=False):
    ids = []
    for a in range(n):
        ids.append(authoridpool(is_lock=is_lock))
    print("author " + ("locked " if is_lock else "") + "id 生成完毕 开始添加到数据库")
    sql.session.add_all(ids)


def collect_author_id(author_id, sql):
    sql.session.add(authoridpool(author_id=author_id))


def del_a_author_id_from_pool(sql):
    res = sql.session.query(authoridpool.author_id).count()
    if res < author_id_pool_lock_size:
        add_author_id_pool(author_id_pool_lock_size - res, sql, True)
    if res < author_id_pool_size:
        add_author_id_pool(author_id_pool_size - res, sql)
    ret = sql.session.query(authoridpool.author_id).filter(authoridpool.is_lock == False).first()[0]
    sql.session.query(authoridpool).filter(authoridpool.author_id == ret).delete()
    return ret


def add_book_id_pool(n, sql):
    ids = []
    for a in range(n):
        ids.append(bookidpool())
    print("book id 生成完毕 开始添加到数据库")
    sql.session.add_all(ids)


def collect_book_id(book_id, sql):
    sql.session.add(bookidpool(book_id=book_id))


def del_a_book_id_from_pool(sql):
    res = sql.session.query(bookidpool.book_id).count()
    if res < book_id_pool_size:
        add_book_id_pool(book_id_pool_size - res, sql)
    ret = sql.session.query(bookidpool.book_id).first()[0]
    sql.session.query(bookidpool).filter(bookidpool.book_id == ret).delete()
    return ret


def add_user(user):
    with UsingAlchemy() as sql:
        user_id = del_a_user_id_from_pool(sql)
        user.user_id = user_id
        user.activate_time = datetime.datetime.utcnow()
        sql.session.add(user)
    return user_id


def del_user(user_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(users.is_author).filter(users.user_id == user_id).first()[0]
        if ret:
            print(user_id, "是一位作者，无法删除，要删除请将作者绑定到其他账户下，再删除这个用户账号")
            return 0
        sql.session.query(users).filter(users.user_id == user_id).delete()
        collect_user_id(user_id, sql)
    return 1


def select_user(user_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(users).filter(users.user_id == user_id).first()
        sql.session.query(users).filter(users.user_id == user_id).update({"activate_time": datetime.datetime.utcnow()})
    return {'user_id': ret.user_id, 'is_author': ret.is_author, 'user_name': ret.user_name,
            "picture": ret.picture, "gender": ret.gender, "phone_number": ret.phone_number,
            "email": ret.email, "birthday": ret.birthday, "area": ret.area, 'user_describe': ret.user_describe,
            "activate_time": ret.activate_time
            }


def login_user(user_id, passwd):
    with UsingAlchemy() as sql:
        ret = sql.session.query(users).filter(users.user_id == user_id).first()
        sql.session.query(users).filter(users.user_id == user_id).update({"activate_time": datetime.datetime.utcnow()})
    return passwd == ret.password


def update_user(user_id, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(users).filter(users.user_id == user_id).update(updata_dict)


def add_author(author, user_id):
    with UsingAlchemy() as sql:
        author_id = del_a_author_id_from_pool(sql)
        author.author_id = author_id
        author.user_id = user_id
        sql.session.query(users).filter(users.user_id == user_id).update({"is_author": True})
        sql.session.add(author)
    return author_id


def select_author_by_user_id(user_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(authores).filter(authores.user_id == user_id).first()
    return {'author_id': ret.author_id, 'user_id': ret.user_id, 'author_name': ret.author_name,
            'author_describe': ret.author_describe}


def select_author_by_author_id(author_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(authores).filter(authores.author_id == author_id).first()
    return {'author_id': ret.author_id, 'user_id': ret.user_id, 'author_name': ret.author_name,
            'author_describe': ret.author_describe}


def del_author(author_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(booklib.b_id).filter(booklib.author_id == author_id).count()
        if ret != 0:
            print("此作者在数据库中拥有书籍，不能删除")
            return 0
        ret = sql.session.query(authores.user_id).filter(authores.author_id == author_id).first()
        sql.session.query(users).filter(users.user_id == ret[0]).update({"is_author": False})
        sql.session.query(authores).filter(authores.author_id == author_id).delete()
        collect_author_id(author_id, sql)
    return 1


def update_author(author_id, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(authores).filter(authores.author_id == author_id).update(updata_dict)


def add_book_class(book_class):
    with UsingAlchemy() as sql:
        sql.session.add(book_class)


def select_book(b_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(booklib).filter(booklib.b_id == b_id).first()
        sql.session.query(booklib).filter(booklib.b_id == b_id).update({"activate_time": datetime.datetime.utcnow()})
    return {'b-id': ret.b_id, 'author_id': ret.author_id, 'book_lang': ret.book_lang,
            'bc_id': ret.bc_id, 'support_lang': ret.support_lang, 'cover_paht': ret.cover_path,
            'create_time': ret.create_time
            }


def add_chinese_book_class(chinese_book_class):
    with UsingAlchemy() as sql:
        sql.session.add(chinese_book_class)


def update_chinese_book_class(b_id, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(chinesebookclass).filter(chinesebookclass.b_id == b_id).update(updata_dict)


def select_chinesebook_class(b_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(chinesebookclass).filter(chinesebookclass.b_id == b_id).first()
        sql.session.query(chinesebookclass).filter(chinesebookclass.b_id == b_id).update(
            {"activate_time": datetime.datetime.utcnow()})
    return {'b_id': ret.b_id, 'name': ret.name, 'desc': ret.desc}


def add_language(language):
    with UsingAlchemy() as sql:
        sql.session.add(language)


def update_language(lang_id, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(languages).filter(languages.lang_id == lang_id).update(updata_dict)


def select_language(lang_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(languages).filter(languages.lang_id == lang_id).first()
        sql.session.query(languages).filter(languages.lang_id == lang_id).update(
            {"activate_time": datetime.datetime.utcnow()})
    return {'lang_id': ret.lang_id}


def add_chinese_language(chinese_language):
    with UsingAlchemy() as sql:
        sql.session.add(chinese_language)


def update_chineselanguage(lang_id, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(chineselanguages).filter(chineselanguages.lang_id == lang_id).update(updata_dict)


def select_chineselanguage(lang_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(chineselanguages).filter(chineselanguages.lang_id == lang_id).first()
        sql.session.query(chineselanguages).filter(chineselanguages.lang_id == lang_id).update(
            {"activate_time": datetime.datetime.utcnow()})
    return {'lang_id': ret.lang_id, 'chineselang': ret.chineselang}


def add_book(book):
    with UsingAlchemy() as sql:
        book_id = del_a_book_id_from_pool(sql)
        book.b_id = book_id
        book.support_lang = str(book.book_lang)
        sql.session.add(book)
    return book_id


def update_book(b_id, author_id, book_lang, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(booklib).filter(
            and_(booklib.b_id == b_id, booklib.author_id == author_id, booklib.book_lang == book_lang)).update(
            updata_dict)


def add_book_support_language(book_id, lang_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(booklib.support_lang).filter(booklib.b_id == book_id).first()[0]
        ret += str(lang_id)
        sql.session.query(booklib).filter(booklib.b_id == book_id).update({"support_lang": ret})


def get_support_language(book_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(booklib.support_lang).filter(booklib.b_id == book_id).first()[0]
        ret = [int(x) for x in list(ret)]
    return ret


def select_book(b_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(booklib).filter(booklib.b_id == b_id).first()
        sql.session.query(booklib).filter(booklib.b_id == b_id).update({"activate_time": datetime.datetime.utcnow()})
    return {'b_id': ret.b_id, 'author_id': ret.author_id, 'book_lang': ret.book_lang,
            'bc_id': ret.bc_id, 'support_lang': ret.support_lang, 'cover_path': ret.cover_path,
            'create_time': ret.create_time}


def add_content(b_id):
    with UsingAlchemy() as sql:
        content = bookcontent()
        content.b_id = b_id
        sql.session.add(content)


def update_content(b_id, content_no, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(bookcontent).filter(
            and_(bookcontent.b_id == b_id, bookcontent.content_no == content_no)).update(updata_dict)


def select_bookcontent(b_id, c_no):
    with UsingAlchemy() as sql:
        ret = sql.session.query(bookcontent).filter(
            and_(bookcontent.b_id == b_id, bookcontent.content_no == c_no)).first()
        sql.session.query(bookcontent).filter(and_(bookcontent.b_id == b_id, bookcontent.content_no == c_no)).update(
            {"activate_time": datetime.datetime.utcnow()})
    return {'b_id': ret.b_id, 'content_no': ret.content_no}


def add_chinese_book(chinese_book, b_id):
    with UsingAlchemy() as sql:
        chinese_book.b_id = b_id
        sql.session.add(chinese_book)


def update_chinesebook(b_id, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(chinesebooklib).filter(chinesebooklib.b_id == b_id).update(updata_dict)


def select_chinesebook(b_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(chinesebooklib).filter(chinesebooklib.b_id == b_id).first()
        sql.session.query(chinesebooklib).filter(chinesebooklib.b_id == b_id).update(
            {"activate_time": datetime.datetime.utcnow()})
    return {'b_id': ret.b_id, 'name': ret.name, 'desc': ret.desc}


def add_chinese_content(content, b_id, c_no):
    with UsingAlchemy() as sql:
        content.b_id = b_id
        content.c_no = c_no
        sql.session.add(content)


def update_chinese_content(b_id, content_no, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(chinesecontent).filter(
            and_(chinesecontent.b_id == b_id, chinesecontent.content_no == content_no)).update(updata_dict)


def select_chinesecontent(b_id, c_no):
    with UsingAlchemy() as sql:
        ret = sql.session.query(chinesecontent).filter(
            and_(chinesecontent.b_id == b_id, chinesecontent.c_no == c_no)).first()
        sql.session.query(chinesecontent).filter(and_(chinesecontent.b_id == b_id, chinesecontent.c_no == c_no)).update(
            {"activate_time": datetime.datetime.utcnow()})
    return {'b_id': ret.b_id, 'c_no': ret.c_no, 'title': ret.title, 'text_path': ret.text_path}


def add_english_book_class(english_book_class):
    with UsingAlchemy() as sql:
        sql.session.add(english_book_class)


def update_englishbookclass(bookclass_id, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(englishbookclass).filter(englishbookclass.bookclass_id == bookclass_id).update(
            updata_dict)


def select_englishbook_class(bookclass_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(englishbookclass).filter(englishbookclass.bookclass_id == bookclass_id).first()
        sql.session.query(englishbookclass).filter(englishbookclass.bookclass_id == bookclass_id).update(
            {"activate_time": datetime.datetime.utcnow()})
    return {'english_bookclass_name': ret.english_bookclass_name, 'bookclass_id': ret.bookclass_id}


def add_english_language(english_language):
    with UsingAlchemy() as sql:
        sql.session.add(english_language)


def update_englishlanguages(lang_id, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(englishlanguages).filter(englishlanguages.lang_id == lang_id).update(updata_dict)


def select_englishlanguage(lang_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(englishlanguages).filter(englishlanguages.lang_id == lang_id).first()
        sql.session.query(englishlanguages).filter(englishlanguages.lang_id == lang_id).update(
            {"activate_time": datetime.datetime.utcnow()})
    return {'lang_id': ret.lang_id, 'englishlang': ret.englishlang}


def add_english_book(english_book, b_id):
    with UsingAlchemy() as sql:
        english_book.b_id = b_id
        sql.session.add(english_book)


def update_englishbook(b_id, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(englishbooklib).filter(englishbooklib.b_id == b_id).update(updata_dict)


def select_englishbook(b_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(englishbooklib).filter(englishbooklib.b_id == b_id).first()
        sql.session.query(englishbooklib).filter(englishbooklib.b_id == b_id).update(
            {"activate_time": datetime.datetime.utcnow()})
    return {'b_id': ret.b_id, 'name': ret.name, 'desc': ret.desc}


def add_english_content(content, b_id, c_no):
    with UsingAlchemy() as sql:
        content.b_id = b_id
        content.c_no = c_no
        sql.session.add(content)


def update_english_content(b_id, content_no, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(englishcontent).filter(
            and_(englishcontent.b_id == b_id, englishcontent.content_no == content_no)).update(updata_dict)


def select_englishcontent(b_id, c_no):
    with UsingAlchemy() as sql:
        ret = sql.session.query(englishcontent).filter(
            and_(englishcontent.b_id == b_id, englishcontent.c_no == c_no)).first()
        sql.session.query(englishcontent).filter(and_(englishcontent.b_id == b_id, englishcontent.c_no == c_no)).update(
            {"activate_time": datetime.datetime.utcnow()})
    return {'b_id': ret.b_id, 'c_no': ret.c_no, 'title': ret.title, 'text_path': ret.text_path}


def add_japanese_book_class(japanese_book_class):
    with UsingAlchemy() as sql:
        sql.session.add(japanese_book_class)


def update_japanesebookclass(bookclass_id, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(japanesebookclass).filter(
            japanesebookclass.bookclass_id == bookclass_id).update(updata_dict)


def select_japanesebook_class(bookclass_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(japanesebookclass).filter(japanesebookclass.bookclass_id == bookclass_id).first()
        sql.session.query(japanesebookclass).filter(japanesebookclass.bookclass_id == bookclass_id).update(
            {"activate_time": datetime.datetime.utcnow()})
    return {'japanese_bookclass_name': ret.japanese_bookclass_name, 'bookclass_id': ret.bookclass_id}


def add_japanese_language(japanese_language):
    with UsingAlchemy() as sql:
        sql.session.add(japanese_language)


def update_japaneselanguages(lang_id, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(japaneselanguages).filter(japaneselanguages.lang_id == lang_id).update(updata_dict)


def select_japaneselanguage(lang_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(japaneselanguages).filter(japaneselanguages.lang_id == lang_id).first()
        sql.session.query(japaneselanguages).filter(japaneselanguages.lang_id == lang_id).update(
            {"activate_time": datetime.datetime.utcnow()})
    return {'lang_id': ret.lang_id, 'japaneselang': ret.japaneselang}


def add_japanese_book(japanese_book, b_id):
    with UsingAlchemy() as sql:
        japanese_book.b_id = b_id
        sql.session.add(japanese_book)


def update_japanesebook(b_id, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(japanesebooklib).filter(japanesebooklib.b_id == b_id).update(
            updata_dict)


def select_japanesebook(b_id):
    with UsingAlchemy() as sql:
        ret = sql.session.query(japanesebooklib).filter(japanesebooklib.b_id == b_id).first()
        sql.session.query(japanesebooklib).filter(japanesebooklib.b_id == b_id).update(
            {"activate_time": datetime.datetime.utcnow()})
    return {'b_id': ret.b_id, 'name': ret.name, 'desc': ret.desc}


def add_japanese_content(content, b_id, c_no):
    with UsingAlchemy() as sql:
        content.b_id = b_id
        content.c_no = c_no
        sql.session.add(content)


def update_japanese_content(b_id, content_no, updata_dict):
    with UsingAlchemy() as sql:
        ret = sql.session.query(japanesecontent).filter(
            and_(japanesecontent.b_id == b_id, japanesecontent.content_no == content_no)).update(updata_dict)


def select_japanesecontent(b_id, content_no):
    with UsingAlchemy() as sql:
        ret = sql.session.query(japanesecontent).filter(
            and_(japanesecontent.b_id == b_id, japanesecontent.c_no == content_no)).first()
        sql.session.query(japanesecontent).filter(
            and_(japanesecontent.b_id == b_id, japanesecontent.c_no == content_no)).update(
            {"activate_time": datetime.datetime.utcnow()})
    return {'b_id': ret.b_id, 'c_no': ret.c_no, 'title': ret.title, 'text_path': ret.text_path}


if __name__ == '__main__':
    u_id = add_user(users(is_author=False, user_name="张三", user_describe="我是张三haha", password="123456"))
    u_id = add_user(users(is_author=False, user_name="张三", user_describe="我是张三haha", password="123456"))
    u_id = add_user(users(is_author=False, user_name="张三", user_describe="我是张三haha", password="123456"))
    u_id = add_user(users(is_author=False, user_name="张三", user_describe="我是张三haha", password="123456"))
    u_id = add_user(users(is_author=False, user_name="张三", user_describe="我是张三haha", password="123456"))

    print(del_user(204))
    a = select_user(201)
    print(a)
    try:
        a = select_user(209)
        print(a)
    except:
        print("not found")
    print(login_user(205, "123456"))
    print(login_user(205, "12345"))
    add_author(authores(author_name="作者张三", author_describe="我成作者啦"), 203)
    add_author(authores(author_name="作者张三", author_describe="我成作者啦"), 201)
    add_author(authores(author_name="作者张三", author_describe="我成作者啦"), 202)

    b = select_author_by_user_id(202)
    print(b)
    c = select_author_by_author_id(201)
    print(c)

    del_author(202)

    add_book_class(bookclass(bookclass_id=1))
    add_book_class(bookclass(bookclass_id=2))
    add_book_class(bookclass(bookclass_id=3))

    add_chinese_book_class(chinesebookclass(bookclass_id=1, chinese_bookclass_name="科幻"))

    add_language(languages(lang_id=1))
    add_language(languages(lang_id=2))
    add_language(languages(lang_id=3))

    add_language(chineselanguages(lang_id=1, chineselang="中文"))
    add_language(chineselanguages(lang_id=2, chineselang="英文"))
    add_language(chineselanguages(lang_id=3, chineselang="日文"))

    add_book(booklib(author_id=201, book_lang=1, bc_id=1))
    add_book(booklib(author_id=201, book_lang=1, bc_id=1))
    add_book(booklib(author_id=201, book_lang=1, bc_id=1))
    print(del_author(201))
    add_book_support_language(2, 2)
    print(get_support_language(2))
    add_content(1)
    add_content(1)
    add_content(1)
    add_content(1)
    add_chinese_book(chinesebooklib(name="张三的奇妙冒险"), 1)
    add_chinese_content(chinesecontent(title="1 一", text_path="文件路径"), 1, 1)
    add_chinese_content(chinesecontent(title="2 二", text_path="文件路径"), 1, 2)
    add_chinese_content(chinesecontent(title="3 三", text_path="文件路径"), 1, 3)

# __all__ = ["user_id_pool_size","author_id_pool_size","book_id_pool_size","add_user","del_user","select_user",]
