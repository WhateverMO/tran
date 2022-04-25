from platform_database import *

user_id_pool_size = 400
user_id_pool_lock_size = 200
author_id_pool_size = 400
author_id_pool_lock_size = 200
b_id_pool_size = 400


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


def add_b_id_pool(n, sql):
    ids = []
    for a in range(n):
        ids.append(bookidpool())
    print("book id 生成完毕 开始添加到数据库")
    sql.session.add_all(ids)


def collect_b_id(b_id, sql):
    sql.session.add(bookidpool(b_id=b_id))


def del_a_b_id_from_pool(sql):
    res = sql.session.query(bookidpool.b_id).count()
    if res < b_id_pool_size:
        add_b_id_pool(b_id_pool_size - res, sql)
    ret = sql.session.query(bookidpool.b_id).first()[0]
    sql.session.query(bookidpool).filter(bookidpool.b_id == ret).delete()
    return ret


def add_user(user):
    with UsingAlchemy(log_label='添加用户') as sql:
        user_id = del_a_user_id_from_pool(sql)
        user.user_id = user_id
        user.activate_time = datetime.datetime.utcnow()
        sql.session.add(user)
    return user_id


def del_user(user_id):
    with UsingAlchemy(log_label='删除用户') as sql:
        ret = sql.session.query(users.is_author).filter(users.user_id == user_id).first()[0]
        if ret:
            print(user_id, "是一位作者，无法删除，要删除请将作者绑定到其他账户下，再删除这个用户账号")
            return 0
        sql.session.query(users).filter(users.user_id == user_id).delete()
        collect_user_id(user_id, sql)
    return 1


def select_user(user_id):
    with UsingAlchemy(log_label='获取用户信息') as sql:
        ret = sql.session.query(users).filter(users.user_id == user_id).first()
        sql.session.query(users).filter(users.user_id == user_id).update({"activate_time": datetime.datetime.utcnow()})
    return {'user_id': ret.user_id, 'is_author': ret.is_author, 'user_name': ret.user_name,
            "picture": ret.picture, "gender": ret.gender, "phone_number": ret.phone_number,
            "email": ret.email, "birthday": ret.birthday, "area": ret.area, 'user_describe': ret.user_describe,
            "activate_time": ret.activate_time
            }


def login_user(user_id, passwd):
    with UsingAlchemy(log_label='用户登录') as sql:
        ret = sql.session.query(users).filter(users.user_id == user_id).first()
        sql.session.query(users).filter(users.user_id == user_id).update({"activate_time": datetime.datetime.utcnow()})
    return passwd == ret.password


def update_user(user_id, update_dict):
    with UsingAlchemy(log_label='更新用户信息') as sql:
        ret = sql.session.query(users).filter(users.user_id == user_id).update(update_dict)


def add_author(author, user_id):
    with UsingAlchemy(log_label='添加作者') as sql:
        author_id = del_a_author_id_from_pool(sql)
        author.author_id = author_id
        author.user_id = user_id
        sql.session.query(users).filter(users.user_id == user_id).update({"is_author": True})
        sql.session.add(author)
    return author_id


def select_author_by_user_id(user_id):
    with UsingAlchemy(log_label='通过用户id获取作者信息') as sql:
        ret = sql.session.query(authores).filter(authores.user_id == user_id).first()
    return {'author_id': ret.author_id, 'user_id': ret.user_id, 'author_name': ret.author_name,
            'author_describe': ret.author_describe}


def select_author_by_author_id(author_id):
    with UsingAlchemy(log_label='通过作者id获取作者信息') as sql:
        ret = sql.session.query(authores).filter(authores.author_id == author_id).first()
    return {'author_id': ret.author_id, 'user_id': ret.user_id, 'author_name': ret.author_name,
            'author_describe': ret.author_describe}


def del_author(author_id):
    with UsingAlchemy(log_label='删除作者') as sql:
        ret = sql.session.query(booklib.b_id).filter(booklib.author_id == author_id).count()
        if ret != 0:
            print("此作者在数据库中拥有书籍，不能删除")
            return 0
        ret = sql.session.query(authores.user_id).filter(authores.author_id == author_id).first()
        sql.session.query(users).filter(users.user_id == ret[0]).update({"is_author": False})
        sql.session.query(authores).filter(authores.author_id == author_id).delete()
        collect_author_id(author_id, sql)
    return 1


def update_author(author_id, update_dict):
    with UsingAlchemy(log_label='更新作者信息') as sql:
        ret = sql.session.query(authores).filter(authores.author_id == author_id).update(update_dict)


def add_book_class(book_class):
    with UsingAlchemy(log_label='添加书记种类编号') as sql:
        sql.session.add(book_class)


def add_language(language):
    with UsingAlchemy(log_label='添加支持语言') as sql:
        sql.session.add(language)


def add_book(book):
    with UsingAlchemy(log_label='在根书籍库添加书籍') as sql:
        if book.b_id == None:
            b_id = del_a_b_id_from_pool(sql)
            book.b_id = b_id
        if book.support_lang == None:
            book.support_lang = str(book.lang_id)
        sql.session.add(book)
    return b_id


def update_book(b_id, author_id, book_lang, update_dict):
    with UsingAlchemy(log_label='在根书籍库更新书籍信息') as sql:
        ret = sql.session.query(booklib).filter(
            and_(booklib.b_id == b_id, booklib.author_id == author_id, booklib.lang_id == book_lang)).update(
            update_dict)


def add_book_support_language(b_id, author_id, book_lang, lang_id):
    with UsingAlchemy(log_label='在根书籍库增加书籍支持的语言标记') as sql:
        ret = sql.session.query(booklib.support_lang).filter(
            and_(booklib.b_id == b_id, booklib.author_id == author_id, booklib.lang_id == book_lang)).first()[0]
        ret += str(lang_id)
        sql.session.query(booklib).filter(
            and_(booklib.b_id == b_id, booklib.author_id == author_id, booklib.lang_id == book_lang)).update(
            {"support_lang": ret})


def get_support_language(b_id, author_id, book_lang):
    with UsingAlchemy(log_label='在根书籍库查询书籍支持的语言') as sql:
        ret = sql.session.query(booklib.support_lang).filter(
            and_(booklib.b_id == b_id, booklib.author_id == author_id, booklib.lang_id == book_lang)).first()[0]
        ret = [int(x) for x in list(ret)]
    return ret


def select_book(b_id, author_id, book_lang):
    with UsingAlchemy(log_label='在根书籍库获取书籍信息') as sql:
        ret = sql.session.query(booklib).filter(
            and_(booklib.b_id == b_id, booklib.author_id == author_id, booklib.lang_id == book_lang)).first()
    return {'b_id': ret.b_id, 'author_id': ret.author_id, 'book_lang': ret.lang_id,
            'bc_id': ret.bc_id, 'support_lang': ret.support_lang, 'cover_path': ret.cover_path,
            'create_time': ret.create_time}


def add_content(b_id, author_id, book_lang, c_no):
    with UsingAlchemy(log_label='在根书籍目录库添加章节') as sql:
        content = bookcontent()
        content.b_id = b_id
        content.author_id = author_id
        content.lang_id = book_lang
        content.c_no = c_no
        sql.session.add(content)


def update_content(b_id, author_id, book_lang, c_no, update_dict):
    with UsingAlchemy(log_label='在根书籍目录库更新章节') as sql:
        ret = sql.session.query(bookcontent).filter(
            and_(bookcontent.b_id == b_id, bookcontent.author_id == author_id, bookcontent.lang_id == book_lang,
                 bookcontent.c_no == c_no)).update(update_dict)


def select_bookcontent(b_id, author_id, book_lang, c_no):
    with UsingAlchemy(log_label='在根书籍目录库获取章节信息') as sql:
        ret = sql.session.query(bookcontent).filter(
            and_(bookcontent.b_id == b_id, bookcontent.author_id == author_id, bookcontent.lang_id == book_lang,
                 bookcontent.c_no == c_no)).first()
    return {'b_id': ret.b_id, 'author_id': ret.author_id, 'book_lang': ret.lang_id, 'c_no': ret.c_no}


def add_chinese_book_class(chinese_book_class):
    with UsingAlchemy(log_label='在中文映射种类库添加种类') as sql:
        sql.session.add(chinese_book_class)


def update_chinese_book_class(b_id, update_dict):
    with UsingAlchemy(log_label='在中文映射种类库更新种类') as sql:
        ret = sql.session.query(chinesebookclass).filter(chinesebookclass.b_id == b_id).update(update_dict)


def select_chinesebook_class(b_id):
    with UsingAlchemy(log_label='在中文映射种类库获取种类中文名') as sql:
        ret = sql.session.query(chinesebookclass).filter(chinesebookclass.b_id == b_id).first()
    return {'chinese_bookclass_name': ret.chinese_bookclass_name, 'bookclass_id': ret.bookclass_id}


def add_chinese_language(chinese_language):
    with UsingAlchemy(log_label='在中文映射支持语言库添加语言') as sql:
        sql.session.add(chinese_language)


def update_chineselanguage(lang_id, update_dict):
    with UsingAlchemy(log_label='在中文映射支持语言库更新语言') as sql:
        ret = sql.session.query(chineselanguages).filter(chineselanguages.lang_id == lang_id).update(update_dict)


def select_chineselanguage(lang_id):
    with UsingAlchemy(log_label='在中文映射支持语言库获取语言的中文') as sql:
        ret = sql.session.query(chineselanguages).filter(chineselanguages.lang_id == lang_id).first()
    return {'lang_id': ret.lang_id, 'chineselang': ret.chineselang}


def add_chinese_book(chinese_book, b_id, author_id, book_lang):
    with UsingAlchemy(log_label='在中文映射书籍库添加书籍') as sql:
        chinese_book.b_id = b_id
        chinese_book.author_id = author_id
        chinese_book.lang_id = book_lang
        sql.session.add(chinese_book)


def update_chinesebook(b_id, author_id, book_lang, update_dict):
    with UsingAlchemy(log_label='在中文映射书籍库更新书籍') as sql:
        ret = sql.session.query(chinesebooklib).filter(
            and_(chinesebooklib.b_id == b_id, chinesebooklib.author_id == author_id,
                 chinesebooklib.lang_id == book_lang)).update(update_dict)


def select_chinesebook(b_id, author_id, book_lang):
    with UsingAlchemy(log_label='在中文映射书籍库获取书籍') as sql:
        ret = sql.session.query(chinesebooklib).filter(
            and_(chinesebooklib.b_id == b_id, chinesebooklib.author_id == author_id,
                 chinesebooklib.lang_id == book_lang)).first()
    return {'b_id': ret.b_id, 'author_id': ret.author_id, 'book_lang': ret.lang_id, 'name': ret.name, 'desc': ret.desc}


def add_chinese_content(content, b_id, author_id, book_lang, c_no):
    with UsingAlchemy(log_label='在中文映射书籍目录库添加章节') as sql:
        content.b_id = b_id
        content.author_id = author_id
        content.lang_id = book_lang
        content.c_no = c_no
        sql.session.add(content)


def update_chinese_content(b_id, author_id, book_lang, c_no, update_dict):
    with UsingAlchemy(log_label='在中文映射书籍目录库更新章节') as sql:
        ret = sql.session.query(chinesecontent).filter(
            and_(chinesebooklib.b_id == b_id, chinesebooklib.author_id == author_id,
                 chinesebooklib.lang_id == book_lang, chinesecontent.c_no == c_no)).update(update_dict)


def select_chinesecontent(b_id, author_id, book_lang, c_no):
    with UsingAlchemy(log_label='在中文映射书籍目录库获取章节') as sql:
        ret = sql.session.query(chinesecontent).filter(
            and_(chinesebooklib.b_id == b_id, chinesebooklib.author_id == author_id,
                 chinesebooklib.lang_id == book_lang, chinesecontent.c_no == c_no)).first()
    return {'b_id': ret.b_id, 'author_id': ret.author_id, 'book_lang': ret.lang_id, 'c_no': ret.c_no,
            'title': ret.title, 'text_path': ret.text_path}


def add_english_book_class(english_book_class):
    with UsingAlchemy(log_label='在英文映射种类库添加种类') as sql:
        sql.session.add(english_book_class)


def update_englishbookclass(bookclass_id, update_dict):
    with UsingAlchemy(log_label='在英文映射种类库更新种类') as sql:
        ret = sql.session.query(englishbookclass).filter(englishbookclass.bookclass_id == bookclass_id).update(
            update_dict)


def select_englishbook_class(bookclass_id):
    with UsingAlchemy(log_label='在英文映射种类库获取种类的英文') as sql:
        ret = sql.session.query(englishbookclass).filter(englishbookclass.bookclass_id == bookclass_id).first()
    return {'english_bookclass_name': ret.english_bookclass_name, 'bookclass_id': ret.bookclass_id}


def add_english_language(english_language):
    with UsingAlchemy(log_label='在英文映射支持语言库添加语言') as sql:
        sql.session.add(english_language)


def update_englishlanguages(lang_id, update_dict):
    with UsingAlchemy(log_label='在英文映射支持语言库更新语言') as sql:
        ret = sql.session.query(englishlanguages).filter(englishlanguages.lang_id == lang_id).update(update_dict)


def select_englishlanguage(lang_id):
    with UsingAlchemy(log_label='在英文映射支持语言库获取语言') as sql:
        ret = sql.session.query(englishlanguages).filter(englishlanguages.lang_id == lang_id).first()
    return {'lang_id': ret.lang_id, 'englishlang': ret.englishlang}


def add_english_book(english_book, b_id, author_id, book_lang):
    with UsingAlchemy(log_label='在英文映射书籍库添加书籍') as sql:
        english_book.b_id = b_id
        english_book.author_id = author_id
        english_book.lang_id = book_lang
        sql.session.add(english_book)


def update_englishbook(b_id, author_id, book_lang, update_dict):
    with UsingAlchemy(log_label='在英文映射书籍库更新书籍') as sql:
        ret = sql.session.query(englishbooklib).filter(
            and_(englishbooklib.b_id == b_id, englishbooklib.author_id == author_id,
                 englishbooklib.lang_id == book_lang)).update(update_dict)


def select_englishbook(b_id, author_id, book_lang):
    with UsingAlchemy(log_label='在英文映射书籍库获取书籍') as sql:
        ret = sql.session.query(englishbooklib).filter(
            and_(englishbooklib.b_id == b_id, englishbooklib.author_id == author_id,
                 englishbooklib.lang_id == book_lang)).first()
    return {'b_id': ret.b_id, 'author_id': ret.author_id, 'book_lang': ret.lang_id, 'name': ret.name, 'desc': ret.desc}


def add_english_content(content, author_id, book_lang, b_id, c_no):
    with UsingAlchemy(log_label='在英文映射书籍目录库添加章节') as sql:
        content.b_id = b_id
        content.author_id = author_id
        content.lang_id = book_lang
        content.c_no = c_no
        sql.session.add(content)


def update_english_content(b_id, author_id, book_lang, c_no, update_dict):
    with UsingAlchemy(log_label='在英文映射书籍目录库更新章节') as sql:
        ret = sql.session.query(englishcontent).filter(
            and_(englishbooklib.b_id == b_id, englishbooklib.author_id == author_id,
                 englishbooklib.lang_id == book_lang, englishcontent.c_no == c_no)).update(update_dict)


def select_englishcontent(b_id, author_id, book_lang, c_no):
    with UsingAlchemy(log_label='在英文映射书籍目录库获取章节') as sql:
        ret = sql.session.query(englishcontent).filter(
            and_(englishbooklib.b_id == b_id, englishbooklib.author_id == author_id,
                 englishbooklib.lang_id == book_lang, englishcontent.c_no == c_no)).first()
    return {'b_id': ret.b_id, 'author_id': ret.author_id, 'book_lang': ret.lang_id, 'c_no': ret.c_no,
            'title': ret.title, 'text_path': ret.text_path}


def add_japanese_book_class(japanese_book_class):
    with UsingAlchemy(log_label='在日文映射种类库添加种类') as sql:
        sql.session.add(japanese_book_class)


def update_japanesebookclass(bookclass_id, update_dict):
    with UsingAlchemy(log_label='在日文映射种类库更新种类') as sql:
        ret = sql.session.query(japanesebookclass).filter(
            japanesebookclass.bookclass_id == bookclass_id).update(update_dict)


def select_japanesebook_class(bookclass_id):
    with UsingAlchemy(log_label='在日文映射种类库获取种类') as sql:
        ret = sql.session.query(japanesebookclass).filter(japanesebookclass.bookclass_id == bookclass_id).first()
    return {'japanese_bookclass_name': ret.japanese_bookclass_name, 'bookclass_id': ret.bookclass_id}


def add_japanese_language(japanese_language):
    with UsingAlchemy(log_label='在日文映射语言库添加语言') as sql:
        sql.session.add(japanese_language)


def update_japaneselanguages(lang_id, update_dict):
    with UsingAlchemy(log_label='在日文映射语言库更新语言') as sql:
        ret = sql.session.query(japaneselanguages).filter(japaneselanguages.lang_id == lang_id).update(update_dict)


def select_japaneselanguage(lang_id):
    with UsingAlchemy(log_label='在日文映射语言库获取语言') as sql:
        ret = sql.session.query(japaneselanguages).filter(japaneselanguages.lang_id == lang_id).first()
    return {'lang_id': ret.lang_id, 'japaneselang': ret.japaneselang}


def add_japanese_book(japanese_book, b_id, author_id, book_lang):
    with UsingAlchemy(log_label='在日文映射书籍库添加书籍') as sql:
        japanese_book.b_id = b_id
        japanese_book.author_id = author_id
        japanese_book.lang_id = book_lang
        sql.session.add(japanese_book)


def update_japanesebook(b_id, author_id, book_lang, update_dict):
    with UsingAlchemy(log_label='在日文映射书籍库更新书籍') as sql:
        ret = sql.session.query(japanesebooklib).filter(
            and_(japanesebooklib.b_id == b_id, japanesebooklib.author_id == author_id,
                 japanesebooklib.lang_id == book_lang)).update(
            update_dict)


def select_japanesebook(b_id, author_id, book_lang):
    with UsingAlchemy(log_label='在日文映射书籍库获取书籍') as sql:
        ret = sql.session.query(japanesebooklib).filter(
            and_(japanesebooklib.b_id == b_id, japanesebooklib.author_id == author_id,
                 japanesebooklib.lang_id == book_lang)).first()
    return {'b_id': ret.b_id, 'author_id': ret.author_id, 'book_lang': ret.lang_id, 'name': ret.name, 'desc': ret.desc}


def add_japanese_content(content, b_id, author_id, book_lang, c_no):
    with UsingAlchemy(log_label='在日文映射书籍目录库添加章节') as sql:
        content.b_id = b_id
        content.author_id = author_id
        content.lang_id = book_lang
        content.c_no = c_no
        sql.session.add(content)


def update_japanese_content(b_id, author_id, book_lang, c_no, update_dict):
    with UsingAlchemy(log_label='在日文映射书籍目录库更新章节') as sql:
        ret = sql.session.query(japanesecontent).filter(
            and_(japanesebooklib.b_id == b_id, japanesebooklib.author_id == author_id,
                 japanesebooklib.lang_id == book_lang, japanesecontent.c_no == c_no)).update(update_dict)


def select_japanesecontent(b_id, author_id, book_lang, c_no):
    with UsingAlchemy(log_label='在日文映射书籍目录库获取章节') as sql:
        ret = sql.session.query(japanesecontent).filter(
            and_(japanesecontent.b_id == b_id, japanesecontent.author_id == author_id,
                 japanesecontent.lang_id == book_lang, japanesecontent.c_no == c_no)).first()
    return {'b_id': ret.b_id, 'author_id': ret.author_id, 'book_lang': ret.lang_id, 'c_no': ret.c_no,
            'title': ret.title, 'text_path': ret.text_path}


def select_all_lang_id():
    with UsingAlchemy(log_label='获取所有语言编号') as sql:
        ret = sql.session.query(languages).all()
        res = list()
        for id in ret:
            res.append(id.lang_id)
    return res


def select_all_chinese_lang_id():
    with UsingAlchemy(log_label='获取所有语言编号和对应中文') as sql:
        ret = sql.session.query(chineselanguages).all()
        res = list()
        for id in ret:
            res.append({"lang_id": id.lang_id, "chineselang": id.chineselang})
    return res


def select_all_english_lang_id():
    with UsingAlchemy(log_label='获取所有语言编号和对应英文') as sql:
        ret = sql.session.query(englishlanguages).all()
        res = list()
        for id in ret:
            res.append({"lang_id": id.lang_id, "englishlang": id.englishlang})
    return res


def select_all_japanese_lang_id():
    with UsingAlchemy(log_label='获取所有语言编号和对应日文') as sql:
        ret = sql.session.query(japaneselanguages).all()
        res = list()
        for id in ret:
            res.append({"lang_id": id.lang_id, "japaneselang": id.japaneselang})
    return res


def select_this_author_s_all_book(author_id):
    with UsingAlchemy(log_label='获取这位作者的所有书籍') as sql:
        ret = sql.session.query(booklib).filter(booklib.author_id == author_id).all()
        res = list()
        for book in ret:
            res.append({'b_id': book.b_id, 'author_id': book.author_id, 'book_lang': book.lang_id,
                        'bc_id': book.bc_id, 'support_lang': book.support_lang, 'cover_path': book.cover_path,
                        'create_time': book.create_time})
    return res


def search_chinesebook(book_name):
    with UsingAlchemy(log_label='在中文映射书籍库模糊查询') as sql:
        book_name = "%" + book_name + "%"
        ret = sql.session.query(chinesebooklib).filter(chinesebooklib.name.like(book_name)).all()
        res = list()
        for book in ret:
            res.append({'b_id': book.b_id, 'author_id': book.author_id, 'book_lang': book.lang_id,
                        'name': book.name, 'desc': book.desc})
    return res


def search_englishbook(book_name):
    with UsingAlchemy(log_label='在英文映射书籍库模糊查询') as sql:
        book_name = "%" + book_name + "%"
        ret = sql.session.query(englishbooklib).filter(englishbooklib.name.like(book_name)).all()
        res = list()
        for book in ret:
            res.append({'b_id': book.b_id, 'author_id': book.author_id, 'book_lang': book.lang_id,
                        'name': book.name, 'desc': book.desc})
    return res


def search_japanesebook(book_name):
    with UsingAlchemy(log_label='在日文映射书籍库模糊查询') as sql:
        book_name = "%" + book_name + "%"
        ret = sql.session.query(japanesebooklib).filter(japanesebooklib.name.like(book_name)).all()
        res = list()
        for book in ret:
            res.append({'b_id': book.b_id, 'author_id': book.author_id, 'book_lang': book.lang_id,
                        'name': book.name, 'desc': book.desc})
    return res


select_content_lang = {
    1: select_chinesecontent,
    2: select_englishcontent,
    3: select_japanesecontent
}


def select_content(b_id, author_id, book_lang, c_no):
    return select_content_lang[book_lang](b_id, author_id, book_lang, c_no)


if __name__ == '__main__':
    u_id = add_user(users(is_author=False, user_name="张三", user_describe="我是张三haha", password="123456"))
    u_id = add_user(users(is_author=False, user_name="张三", user_describe="我是张三haha", password="123456"))
    u_id = add_user(users(is_author=False, user_name="张三", user_describe="我是张三haha", password="123456"))
    u_id = add_user(users(is_author=False, user_name="张三", user_describe="我是张三haha", password="123456"))
    u_id = add_user(users(is_author=False, user_name="张三", user_describe="我是张三haha", password="123456"))

    update_user(201, {'user_name': "李四"})

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

    add_author(authores(author_name="作者张三", author_describe="我成作者啦"), 201)
    add_author(authores(author_name="作者张三", author_describe="我成作者啦"), 201)
    add_author(authores(author_name="作者张三", author_describe="我成作者啦"), 202)

    temp_gai_author = dict()
    temp_gai_author['author_describe'] = "我改了签名"

    update_author(202, temp_gai_author)

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

    update_chineselanguage(1, {'chineselang': "简体中文"})

    add_book(booklib(author_id=201, lang_id=1, bc_id=1))
    add_book(booklib(author_id=201, lang_id=1, bc_id=1))
    add_book(booklib(author_id=201, lang_id=1, bc_id=1))

    update_book(1, 201, 1, {'bc_id': 2})
    try:
        del_author(201)
    except:
        print("del author fail")
    add_book_support_language(2, 201, 1, 2)
    print(get_support_language(2, 201, 1))
    add_content(1, 201, 1, 1)
    add_content(1, 201, 1, 2)
    add_content(1, 201, 1, 3)
    add_content(1, 201, 1, 4)
    add_chinese_book(chinesebooklib(name="张三的奇妙冒险"), 1, 201, 1)
    add_chinese_content(chinesecontent(title="1 一", text_path="文件路径"), 1, 201, 1, 1)
    add_chinese_content(chinesecontent(title="2 二", text_path="文件路径"), 1, 201, 1, 2)
    add_chinese_content(chinesecontent(title="3 三", text_path="文件路径"), 1, 201, 1, 3)
    print(select_content(1, 201, 1, 1))
    print(select_all_lang_id())
    print(select_all_chinese_lang_id())
    print(select_all_english_lang_id())
    print(select_all_japanese_lang_id())
    print(select_this_author_s_all_book(201))
    print(search_chinesebook("三"))
    print(search_englishbook("三"))
    print(search_japanesebook("三"))
    pass

# __all__ = ["user_id_pool_size","author_id_pool_size","b_id_pool_size","add_user","del_user","select_user",]
