import datetime
import ipaddress
import json
import re

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from sqlalchemy import desc
from sqlalchemy.sql.elements import and_

from NekoBlog.NekoPack.db import get_session, Article, Comment, Category, User
from NekoBlog.NekoPack.ip import get_ip

ERROR405 = JsonResponse({"success": False, "message": "Method Not Allowed"}, status=405)
SOMETHING_EMPTY = JsonResponse({"success": False, "message": "缺少参数"}, status=400)
permissions = JsonResponse({"success": False, "message": "权限不足"}, status=403)
TYPEERROR = JsonResponse({"success": False, "message": "请求格式错误"}, status=400)


def not_found(r, e):
    return JsonResponse({"success": False, "message": "Page Not Found"}, status=404)


def upload(request: WSGIRequest):
    if request.method == 'POST':
        try:
            req = request.body.decode(encoding='utf8')
            r = json.loads(req)
        except Exception as e:
            print(e)
            return TYPEERROR
        jwt = r.get('jwt')
        title = r.get('title')
        content = r.get('content')
        if jwt['info']['permissions'] > 1:
            if content is not None and title is not None:
                session = get_session()
                art = Article(
                    title=title,
                    author=jwt['info']['uuid'],
                    content=content,
                    up_time=datetime.datetime.now(),
                    alt_time=datetime.datetime.now()
                )
                session.add(art)
                session.commit()
                return JsonResponse(data={"success": True, "aid": art.id}, status=200)
            else:
                return SOMETHING_EMPTY
        else:
            return permissions
    else:
        return ERROR405


def get_list(request: WSGIRequest, page: int):
    if request.method == 'GET':
        if page is not None:
            page = int(page)
            if page > 0:
                session = get_session()
                try:
                    art: Article = session.query(Article).filter(
                        Article.show == 1
                    ).order_by(desc(Article.id)).limit(10).offset((page - 1) * 10)
                    if art.count() > 0:
                        data = list(map(
                            lambda x: {
                                "aid": x.id,
                                "title": x.title,
                                "name": x.name,
                                "category": x.category,
                                "preview": x.preview if x.preview is not None else
                                'https://tva1.sinaimg.cn/large/0072Vf1pgy1fodqop5rd7j31kw148npj.jpg',
                                "content": re.sub(r'</?\w+[^>]*>', '  ', x.content[:100]) + '......',
                                "comment": len(x.comments),
                                "up_time": x.up_time
                            },
                            art
                        ))
                        return JsonResponse(data={"success": True, "list": data}, status=200)
                    else:
                        return JsonResponse(data={"success": False, "message": '超过文章数量'}, status=400)
                except Exception as e:
                    print(e)
                    return JsonResponse(data={"success": False, "message": '超过文章数量'}, status=400)
            else:
                return JsonResponse(data={"success": False, "message": '页码不能为零'}, status=404)
        else:
            return SOMETHING_EMPTY
    else:
        return ERROR405


def get_article(request: WSGIRequest, category: str, aid: int):
    if request.method == 'GET':
        if aid > 0:
            session = get_session()
            art: Article = session.query(Article).filter(and_(Article.id == aid, Article.category == category)).one_or_none()
            if art is not None:
                if art.show:
                    art.views = art.views + 1
                    article = art.to_dict()
                    category = session.query(Category).filter(Category.category == art.category).one_or_none()
                    if category:
                        article['category'] = category.to_dict()
                    else:
                        article['category'] = {"id": 0, "category": art.category, "name": "其他"}
                    if art.comment:
                        article['comment'] = len(art.comments)
                    else:
                        article['comment'] = False
                    if article['preview'] is None:
                        article['preview'] = 'https://tva1.sinaimg.cn/large/0072Vf1pgy1fodqop5rd7j31kw148npj.jpg'
                    info: User = session.query(User).filter(User.uuid == art.author).one_or_none()
                    if info:
                        article['author'] = info.to_dict()
                    session.commit()
                    return JsonResponse(data={"success": True, "article": article}, status=200)
                else:
                    return JsonResponse(data={"success": False, "message": '文章不可见'}, status=404)
            else:
                return JsonResponse(data={"success": False, "message": '文章不存在'}, status=404)
        else:
            return JsonResponse(data={"success": False, "message": '文章不存在'}, status=404)
    else:
        return ERROR405


def comment(request: WSGIRequest, aid: int):
    if request.method == 'POST':
        if aid < 0:
            return JsonResponse(data={"success": False, "message": '文章不存在'}, status=404)
        try:
            r = json.loads(request.body)
            nick = str(r.get('nick'))
            mail = str(r.get('mail'))
            site = str(r.get('site'))
            if r.get('fid') is not None:
                fid = int(r.get('fid'))
            else:
                fid = 0
            content = str(r.get('content'))
            ip = int(ipaddress.ip_address(get_ip(request)))
            ua = request.META.get('HTTP_USER_AGENT')
        except Exception as e:
            print(e)
            return TYPEERROR
        if content != '' and nick != '' and mail != '' and site != '':
            session = get_session()
            art: Article = session.query(Article).filter(Article.id == aid, Article.show == 1).one_or_none()
            if art:
                if art.comment is True:
                    if fid <= len(art.comments) or fid == 0:
                        cmt = Comment(
                            aid=aid,
                            fid=fid,
                            content=content,
                            site=site,
                            nick=nick,
                            ip=ip,
                            ua=ua,
                            mail=mail
                        )
                        session.add(cmt)
                        session.commit()
                        return JsonResponse(data={"success": True, "cid": cmt.id}, status=200)
                    else:
                        return JsonResponse(data={"success": False, "message": '评论不存在'}, status=404)
                else:
                    return JsonResponse(data={"success": False, "message": '评论区已关闭'}, status=404)
            else:
                return JsonResponse(data={"success": False, "message": '文章不存在'}, status=404)
        else:
            return SOMETHING_EMPTY
    else:
        return ERROR405


def get_comment(request: WSGIRequest, aid: int):
    if request.method == 'GET':
        if aid < 0:
            return JsonResponse(data={"success": False, "message": '文章不存在'}, status=404)
        session = get_session()
        art: Article = session.query(Article).filter(Article.id == aid, Article.show == 1).one_or_none()
        if art:
            if art.comment is True:
                cmt = []
                cmts = list(map(lambda x: x.to_dict(), art.comments))
                cmt_num = len(cmts)
                while len(cmts) > 0:
                    index = len(cmts) - cmt_num
                    if cmts[index]['fid'] > 0:
                        for x in range(len(cmt)):
                            if cmt[x]['id'] == cmts[index]['fid']:
                                cmt[x]['reply'].append(cmts[index])
                            else:
                                pass
                    else:
                        cmts[index]['reply'] = []
                        cmt.append(cmts[index])
                    cmts.pop(index)
                    cmt_num -= 1
                session.commit()
                return JsonResponse(data={"success": True, "comments": cmt[::-1]}, status=200)
        else:
            return JsonResponse(data={"success": False, "message": '文章不存在'}, status=404)
    else:
        return ERROR405
