import pymysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,DATE, DATETIME,Integer, String, ForeignKey, UniqueConstraint, Index, Text,BOOLEAN
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine,and_
from timeit import default_timer

# Host = 'mysqlforshejidasai.mysql.database.azure.com'
# Port = 3306
# Db = 'test_db'
# User = 'sjds@mysqlforshejidasai'
# Password = 'Shejidasai123456'
# Charset='utf8'

# Host = 'rt-books.ltd'
# Port = 3306
# Db = 'test_db'
# User = 'root'
# Password = 'Shejidasai123456'
# Charset='utf8'

Host = 'localhost'
Port = 3306
Db = 'test_db'
User = 'root'
Password = 'shejidasai123456'
Charset='utf8'

g_mysql_url = 'mysql+pymysql://%s:%s@%s:%d/%s?charset=%s' % (User, Password, Host, Port,Db,Charset)

engine = create_engine(g_mysql_url)

Base = declarative_base()

engine.execute('ALTER DATABASE test_db CHARSET=UTF8;')

Session = sessionmaker(bind=engine)

class UsingAlchemy(object):

    def __init__(self, commit=True, log_time=True, log_label=''):
        """

        :param commit: 是否在最后提交事务(设置为False的时候方便单元测试)
        :param log_time:  是否打印程序运行总时间
        :param log_label:  自定义log的文字
        """
        self._log_time = log_time
        self._commit = commit
        self._log_label = log_label+" -- 总用时"
        self._session = Session()

    def __enter__(self):

        # 如果需要记录时间
        if self._log_time is True:
            self._start = default_timer()

        return self

    def __exit__(self, *exc_info):
        # 提交事务
        if self._commit:
            self._session.commit()

        if self._log_time is True:
            diff = default_timer() - self._start
            print('-- %s: %.6f 秒' % (self._log_label, diff))

    @property
    def session(self):
        return self._session