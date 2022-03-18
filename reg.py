import datetime
import sys
import uuid

import bcrypt

from NekoBlog.NekoPack.db import get_session, User, Category, Article

data = sys.argv

session = get_session()
user = User(
    name=data[1],
    uuid=uuid.uuid1(),
    mail=data[2],
    pwd=bcrypt.hashpw(data[3].encode('utf8'), bcrypt.gensalt(16)),
    nick=data[4],
    permissions=3,
    reg_time=datetime.datetime.now()
)
category = Category(
    category='other',
    name='其他',
    index=1
)
session.add(user)
session.add(category)
art = Article(
    title='你好,世界',
    content='本文由系统自动创建',
    name='hello-world',
    author=user.uuid
)
session.add(art)
session.commit()
