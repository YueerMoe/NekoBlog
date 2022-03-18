import os.path
import re
import sys

from NekoBlog.NekoPack.db import Article, get_session

data = sys.argv

try:
    uuid = data[2]
    title = data[3]
    name = data[4]
    category = data[5]
    comment = data[6]
    preview = data[7]
    if not re.match(r'[A-Za-z\d-_()]', name):
        print("name标签仅支持大小写字母、数字、-_()")
        exit()
    if os.path.isfile(data[1]):
        file = data[1]
    else:
        print("文件不存在")
        exit()
    with open(file, 'r', encoding='utf8') as f:
        r = f.read()

    session = get_session()
    art = Article(
        title=data[2],
        content=r,
        name=name,
        category='live',
        author=uuid,
        comment=(comment == 'true'),
        preview=preview
    )
    session.add(art)
    session.commit()

except Exception as e:
    print(e)
