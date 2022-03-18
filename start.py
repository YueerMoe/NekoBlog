import datetime
import sys
import uuid

import bcrypt

from NekoBlog.NekoPack.db import get_session, User, Category, Article

data = sys.argv
try:
    name = data[1]
    mail = data[2]
    pwd = data[3]
    nick = data[4]
    session = get_session()
    user = User(
        name=name,
        uuid=uuid.uuid1(),
        mail=mail,
        pwd=bcrypt.hashpw(pwd.encode('utf8'), bcrypt.gensalt(16)),
        nick=nick,
        permissions=3,
        reg_time=datetime.datetime.now()
    )
    session.add(user)
    session.commit()
    print(f'管理员用户创建成功，UUID:{user.uuid}')
    category = Category(
        category='other',
        name='其他',
        index=1
    )
    session.add(category)
    session.commit()
    print(f'默认文章分类创建成功')
    art = Article(
        title='你好,世界',
        content='本文由系统自动创建',
        category=category.category,
        name='hello-world',
        author=user.uuid
    )
    session.add(art)
    session.commit()
    print(f'默认文章分类创建成功')
except Exception as e:
    print(e)
