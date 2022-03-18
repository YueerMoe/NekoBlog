import re
from hashlib import md5


def email_desensitization(mail):
    name = mail[:mail.index('@')]
    domain = mail[mail.index('@') - 1:]
    if len(name) >= 3:
        return name[:1] + '***' + name[-1:-1] + domain
    else:
        return '***' + domain


def get_comment_avatar(mail='null'):
    mail = mail.swapcase()
    if re.match(r"\d{5,11}", mail):
        qq = mail.replace('@qq.com', '')
        return f'//q1.qlogo.cn/g?b=qq&nk={qq}&s=100'
    else:
        hashed_mail = str(md5(mail.encode('utf8')))
        return f'https://dn-qiniu-avatar.qbox.me/avatar/{hashed_mail}?s=100'
