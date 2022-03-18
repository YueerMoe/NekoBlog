import datetime
import ipaddress
import json
import re

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Text, Integer, BigInteger, Boolean, and_, TIMESTAMP, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker, Session
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, BIGINT

from NekoBlog.NekoPack.comment import email_desensitization, get_comment_avatar

with open("NekoBlog/configs/mysql.json", 'r') as f:
    cfg = json.loads(f.read())
mysql_url = 'mysql+pymysql://' + cfg['user'] + ':' + cfg['password'] + '@' + cfg['host'] + ':' + str(cfg['port']) +\
            '/' + cfg['database'] + '?charset=utf8mb4'
engine = create_engine(
        mysql_url,
        pool_size=5,
        encoding='utf8'
    )
sessions = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    uuid = Column(VARCHAR(36), primary_key=True, unique=True, index=True)
    name = Column(VARCHAR(16), primary_key=True, unique=True, index=True)
    mail = Column(VARCHAR(64), primary_key=True, unique=True, index=True)
    pwd = Column(Text)
    nick = Column(Text)
    url = Column(Text)
    permissions = Column(TINYINT, default=1)
    reg_time = Column(TIMESTAMP)
    login_record = relationship('Log')

    def to_dict(self):
        u_dict = {}
        u_dict.update(self.__dict__)
        if "_sa_instance_state" in u_dict:
            del u_dict['_sa_instance_state']
            del u_dict['pwd']
            del u_dict['mail']
        return u_dict


class Log(Base):
    __tablename__ = 'log'
    id = Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    uuid = Column(VARCHAR(36), ForeignKey('user.uuid'))
    ip = Column(BIGINT(unsigned=True))
    ua = Column(Text)
    success = Column(Boolean)
    time = Column(TIMESTAMP)


class Article(Base):
    __tablename__ = 'article'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    author = Column(VARCHAR(36), ForeignKey('user.uuid'))
    title = Column(Text, default='未命名文章')
    name = Column(VARCHAR(16), default=str(id))
    preview = Column(Text)
    content = Column(Text)
    comment = Column(Boolean, default=True)
    comments = relationship('Comment')
    views = Column(Integer, default=0)
    stars = Column(Integer, default=0)
    show = Column(Boolean, default=True)
    category = Column(VARCHAR(16), ForeignKey('category.category'), default='other')
    up_time = Column(TIMESTAMP, default=datetime.datetime.now())
    alt_time = Column(TIMESTAMP, default=datetime.datetime.now())

    def to_dict(self):
        u_dict = {}
        u_dict.update(self.__dict__)
        if "_sa_instance_state" in u_dict:
            del u_dict['_sa_instance_state']
        return u_dict


class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    fid = Column(Integer, default=0)
    aid = Column(Integer, ForeignKey('article.id'))
    content = Column(Text)
    nick = Column(VARCHAR(64))
    site = Column(Text)
    mail = Column(Text)
    time = Column(TIMESTAMP, default=datetime.datetime.now())
    ip = Column(BIGINT(unsigned=True))
    ua = Column(Text)

    def to_dict(self, desensitization=False):
        u_dict = {}
        u_dict.update(self.__dict__)
        if "_sa_instance_state" in u_dict:
            del u_dict['_sa_instance_state']
        ip: [ipaddress.IPv4Address, ipaddress.IPv6Address] = ipaddress.ip_address(u_dict['ip'])
        u_dict['avatar'] = get_comment_avatar(u_dict['mail'])
        if desensitization:
            u_dict['mail'] = email_desensitization(u_dict['mail'])
            if ip.version == 4:
                u_dict['ip'] = re.sub(r'(\d{1,3})\.(\d{1,3}).(\d{1,3}).(\d{1,3})', r'\1.**.**.\4', str(ip))
        else:
            u_dict['ip'] = str(ip)
        return u_dict


class Friend(Base):
    __tablename__ = 'friend'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    nick = Column(Text)
    site = Column(Text)
    logo = Column(Text)
    desc = Column(Text)
    index = Column(Integer)

    def to_dict(self):
        u_dict = {}
        u_dict.update(self.__dict__)
        if "_sa_instance_state" in u_dict:
            del u_dict['_sa_instance_state']
            del u_dict['index']
        return u_dict


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    category = Column(VARCHAR(16))
    name = Column(Text)
    index = Column(Integer)

    def to_dict(self):
        u_dict = {}
        u_dict.update(self.__dict__)
        if "_sa_instance_state" in u_dict:
            del u_dict['_sa_instance_state']
            del u_dict['index']
        return u_dict


Base.metadata.create_all(engine)


def get_session() -> Session:
    ss = scoped_session(sessions)
    return ss()


