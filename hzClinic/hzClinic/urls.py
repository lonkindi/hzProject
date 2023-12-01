"""hzClinic URL Configuration

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
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from crm import views

urlpatterns = [
    path('hzhzhz/', admin.site.urls),
    path('', views.main_view, name='main'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('recording/', views.recording_view, name='recording'),
    path('recording/<str:date>', views.recording_view, name='recording'),
    path('updrecord/<int:pk>', views.updrecord_view, name='updrecord'),
    path('delrecord/<int:pk>', views.delrecord_view, name='delrecord'),
    path('timeline/', views.timeline_view, name='timeline'),
    path('timeline/<str:set_date>', views.timeline_view, name='timeline'),
    path('quests/', views.quests_view, name='quests'),
    path('quests/<int:state_id>', views.quests_view, name='quests'),
    path('quest/<int:ext_id>', views.quest_view, name='quest'),
    path('analyzes/', views.analyzes_view, name='analyzes'),
    path('loadrec/', views.loadrec_view, name='loadrec'),

]

handler404 = views.page_not_found_view

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
