import json
import re

from django.http import JsonResponse, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from NekoBlog.NekoPack.NekoJWT import dec_jwt
from django.core.handlers.wsgi import WSGIRequest


class Token(MiddlewareMixin):
    ERROR_AUTH = JsonResponse({"success": False, "message": "Token无效"}, status=401)

    def process_request(self, request: WSGIRequest):
        if re.match(r'/user/', request.path_info):
            request_params = json.loads(getattr(request, 'body'))
            # 复制一份请求参数，变为可以修改
            mutable_request_params = request_params.copy()
            auth_code: str = request.headers.get('Authorization')
            if auth_code is None:
                return self.ERROR_AUTH
            else:
                jwt = dec_jwt(auth_code.replace('Bearer ', ''))
                if jwt:
                    mutable_request_params['jwt'] = jwt
                    data = json.dumps(mutable_request_params).encode(encoding='utf8')
                    setattr(request, "_body", data)
                else:
                    return self.ERROR_AUTH
        else:
            pass

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_exception(self, request, exception):
        pass


class Error(MiddlewareMixin):
    def process_exception(self, request, exception):
        print(exception)
        return JsonResponse({"success": False, "message": "System Error, Try Again Later"}, status=500)
