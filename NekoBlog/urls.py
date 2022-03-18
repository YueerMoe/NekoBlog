"""NekoBlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from NekoBlog.api import user, article, links
from django.urls import path
from django.conf.urls import handler404

urlpatterns = [
    path('login', user.login),
    path('user/article/upload', article.upload),
    path('article/GetList/<int:page>', article.get_list),
    path('article/<str:category>/<int:aid>', article.get_article),
    path('article/<int:aid>/Comment/Send', article.comment),
    path('article/<int:aid>/Comment/Get', article.get_comment),
    #  path('article/<int:aid>/Like/', article.like),
    path('friend', links.get_links),
]

handler404()
