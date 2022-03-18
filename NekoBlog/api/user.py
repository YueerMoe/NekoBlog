import ipaddress
import json
import time

import bcrypt
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from NekoBlog.NekoPack.NekoJWT import gen_jwt
from NekoBlog.NekoPack.db import get_session, Article, User, Log
from NekoBlog.NekoPack.ip import get_ip

ERROR405 = JsonResponse({"success": False, "message": "Method Not Allowed"}, status=405)
SOMETHING_EMPTY = JsonResponse({"success": False, "message": "缺少参数"}, status=400)
TYPEERROR = JsonResponse({"success": False, "message": "请求格式错误"}, status=400)


def verify(key: [str, None]) -> bool:
    if key:
        return True
    else:
        return False


def login(request: WSGIRequest):
    if request.method == 'POST':
        try:
            r = json.loads(request.body)
        except Exception as e:
            print(e)
            return TYPEERROR
        uname = r.get('username')
        pwd = r.get('password')
        # recaptcha = r.get('g-recaptcha-response')
        if True:  # verify(recaptcha):
            session = get_session()
            ip_adr = int(ipaddress.ip_address(get_ip(request)))
            ua = request.META.get('HTTP_USER_AGENT')
            if '@' in uname:
                info: User = session.query(User).filter(User.mail == uname).one_or_none()
            else:
                info: User = session.query(User).filter(User.name == uname).one_or_none()
            if info:
                if bcrypt.checkpw(pwd.encode('utf8'), info.pwd.encode('utf8')):
                    access = gen_jwt({
                        'iss': 'NekoBlog',
                        'sub': 'access_token',
                        'aud': info.name,
                        'iat': int(time.time()),
                        'exp': int(time.time()) + 2592000,
                        'info': {
                            'uuid': info.uuid,
                            'permissions': info.permissions
                        }
                    }, 'access')
                    refresh = gen_jwt({
                        'iss': 'NekoBlog',
                        'sub': 'refresh_token',
                        'aud': info.name,
                        'iat': int(time.time()),
                        'exp': int(time.time()) + 2599200,
                        'info': {
                            'uuid': info.uuid,
                            'permissions': info.permissions
                        }
                    }, 'refresh')
                    session.add(Log(
                        uuid=info.uuid,
                        ip=ip_adr,
                        ua=ua,
                        success=True
                    ))
                    session.commit()
                    return JsonResponse(
                        data={
                            "success": True,
                            "access_token": access,
                            "token_type": "Bearer",
                            "exp": 2599200,
                            "refresh_token": refresh,
                            "uuid": info.uuid
                        }, status=200
                    )
                else:
                    session.add(Log(
                        uuid=info.uuid,
                        ip=ip_adr,
                        ua=ua,
                        success=False
                    ))
                    return JsonResponse(data={"success": False, "message": '用户名或密码错误'}, status=401)
            else:
                session.add(Log(
                    uuid=info.uuid,
                    ip=ip_adr,
                    ua=ua,
                    success=False
                ))
                return JsonResponse(data={"success": False, "message": '用户名或密码错误'}, status=401)
        else:
            return JsonResponse(data={"success": False, "message": '未通过人机验证'}, status=403)
    else:
        return ERROR405


