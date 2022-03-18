from NekoBlog.NekoPack.db import Article, get_session

with open('test.md', 'r', encoding='utf8') as f:
    r = f.read()

session = get_session()
art = Article(
    title='2021,再见',
    content=r,
    name='Bye-2021',
    category='live',
    author='57420a71-9be1-11ec-aedc-50eb71687d9b',
    comment=True,
    preview='https://cdn.iecy.cn/picture/cfc7195b574679dac78c745a65966c66.png'
)
session.add(art)
session.commit()
