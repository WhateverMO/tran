import datetime

from mysql_conn import *

class useridpool(Base):
    __tablename__ = 'useridpool'
    user_id = Column(Integer,primary_key=True,autoincrement=True)
    is_lock = Column(BOOLEAN,default=False)

class authoridpool(Base):
    __tablename__ = 'authoridpool'
    author_id = Column(Integer,primary_key=True,autoincrement=True)
    is_lock = Column(BOOLEAN,default=False)

class bookidpool(Base):
    __tablename__ = 'bookidpool'
    b_id = Column(Integer,primary_key=True,autoincrement=True)

class users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer,primary_key=True)
    is_author = Column(BOOLEAN,default=False)
    user_name = Column(String(32),nullable=False)
    picture = Column(String(64),nullable=True)
    gender = Column(String(8),nullable=True)
    phone_number = Column(String(16),nullable=True)
    email = Column(String(32),nullable=True)
    birthday = Column(DATE,nullable=True)
    area = Column(String(64),nullable=True)
    user_describe = Column(String(64),default=None)
    activate_time = Column(DATETIME,nullable=False)
    password = Column(String(64),nullable=False)

class authores(Base):
    __tablename__ = 'authores'
    author_id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey(users.user_id),nullable=False)
    author_name = Column(String(32), nullable=False)
    author_describe = Column(String(64),default=None)

class bookclass(Base):
    __tablename__ = 'bookclass'
    bookclass_id = Column(Integer,primary_key=True,autoincrement=True)

class languages(Base):
    __tablename__ = 'languages'
    lang_id = Column(Integer,primary_key=True,autoincrement=True)

class booklib(Base):
    __tablename__ = 'booklib'
    b_id = Column(Integer,primary_key=True)
    author_id = Column(Integer,ForeignKey(authores.author_id),primary_key=True)
    book_lang = Column(Integer,ForeignKey(languages.lang_id),primary_key=True)
    bc_id = Column(Integer,ForeignKey(bookclass.bookclass_id))
    support_lang = Column(String(64))
    cover_path = Column(String(128))
    create_time = Column(DATETIME,nullable=False,default=datetime.datetime.utcnow())

class bookcontent(Base):
    __tablename__ = 'bookcontent'
    b_id = Column(Integer,ForeignKey(booklib.b_id),primary_key=True)
    author_id = Column(Integer, ForeignKey(authores.author_id), primary_key=True)
    book_lang = Column(Integer, ForeignKey(languages.lang_id), primary_key=True)
    c_no = Column(Integer,primary_key=True,autoincrement=True)

class chinesebookclass(Base):
    __tablename__ = 'chinesebookclass'
    chinese_bookclass_name = Column(String(32),primary_key=True)
    bookclass_id = Column(Integer,ForeignKey(bookclass.bookclass_id))

class chineselanguages(Base):
    __tablename__ = 'chineselanguages'
    lang_id = Column(Integer,ForeignKey(languages.lang_id))
    chineselang = Column(String(32),primary_key=True)

class chinesebooklib(Base):
    __tablename__ = 'chinesebooklib'
    b_id = Column(Integer,ForeignKey(booklib.b_id),primary_key=True)
    author_id = Column(Integer, ForeignKey(authores.author_id), primary_key=True)
    book_lang = Column(Integer, ForeignKey(languages.lang_id), primary_key=True)
    name = Column(String(32),nullable=False)
    desc = Column(String(256),default=None)

class chinesecontent(Base):
    __tablename__ = 'chinesecontent'
    b_id = Column(Integer,ForeignKey(booklib.b_id),primary_key=True)
    author_id = Column(Integer, ForeignKey(authores.author_id), primary_key=True)
    book_lang = Column(Integer, ForeignKey(languages.lang_id), primary_key=True)
    c_no = Column(Integer,ForeignKey(bookcontent.c_no),primary_key=True)
    title = Column(String(64),nullable=False)
    text_path = Column(String(128),nullable=False)


class englishbookclass(Base):
    __tablename__ = 'englishbookclass'
    english_bookclass_name = Column(String(32),primary_key=True)
    bookclass_id = Column(Integer,ForeignKey(bookclass.bookclass_id))

class englishlanguages(Base):
    __tablename__ = 'englishlanguages'
    lang_id = Column(Integer,ForeignKey(languages.lang_id))
    englishlang = Column(String(32),primary_key=True)
    
class englishbooklib(Base):
    __tablename__ = 'englishbooklib'
    b_id = Column(Integer,ForeignKey(booklib.b_id),primary_key=True)
    author_id = Column(Integer, ForeignKey(authores.author_id), primary_key=True)
    book_lang = Column(Integer, ForeignKey(languages.lang_id), primary_key=True)
    name = Column(String(32),nullable=False)
    desc = Column(String(256),default=None)

class englishcontent(Base):
    __tablename__ = 'englishcontent'
    b_id = Column(Integer,ForeignKey(booklib.b_id),primary_key=True)
    author_id = Column(Integer, ForeignKey(authores.author_id), primary_key=True)
    book_lang = Column(Integer, ForeignKey(languages.lang_id), primary_key=True)
    c_no = Column(Integer,ForeignKey(bookcontent.c_no),primary_key=True)
    title = Column(String(64),nullable=False)
    text_path = Column(String(128),nullable=False)


class japanesebookclass(Base):
    __tablename__ = 'japanesebookclass'
    japanese_bookclass_name = Column(String(32), primary_key=True)
    bookclass_id = Column(Integer, ForeignKey(bookclass.bookclass_id))

class japaneselanguages(Base):
    __tablename__ = 'japaneselanguages'
    lang_id = Column(Integer, ForeignKey(languages.lang_id))
    japaneselang = Column(String(32), primary_key=True)

class japanesebooklib(Base):
    __tablename__ = 'japanesebooklib'
    b_id = Column(Integer, ForeignKey(booklib.b_id), primary_key=True)
    author_id = Column(Integer, ForeignKey(authores.author_id), primary_key=True)
    book_lang = Column(Integer, ForeignKey(languages.lang_id), primary_key=True)
    name = Column(String(32), nullable=False)
    desc = Column(String(256), default=None)

class japanesecontent(Base):
    __tablename__ = 'japanesecontent'
    b_id = Column(Integer, ForeignKey(booklib.b_id), primary_key=True)
    author_id = Column(Integer, ForeignKey(authores.author_id), primary_key=True)
    book_lang = Column(Integer, ForeignKey(languages.lang_id), primary_key=True)
    c_no = Column(Integer, ForeignKey(bookcontent.c_no), primary_key=True)
    title = Column(String(64), nullable=False)
    text_path = Column(String(128), nullable=False)

if __name__ == '__main__':
    print("清除数据库并新建")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
