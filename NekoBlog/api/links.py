
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from NekoBlog.NekoPack.db import get_session, Friend


def get_links(request: WSGIRequest):
    if request.method == "GET":
        session = get_session()
        links = [{
            "id": 0,
            "nick": "Yue's Blog",
            "site": "https://yueer.moe",
            "logo": "https://yueer.moe/logo.png",
            "desc": "喵喵喵"
        }]
        link = session.query(Friend).all()
        if len(link) > 0:
            links += list(map(lambda x: x.to_dict(), link))
        return JsonResponse({"success": True, "links": links}, status=200)
    else:
        return JsonResponse({"success": False, "message": "Method Not Allowed"}, status=405)