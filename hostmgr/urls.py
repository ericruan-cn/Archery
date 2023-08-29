# -*- coding:utf8 -*-
# Author: RuanCT

from django.urls import path
from hostmgr import views

urlpatterns = [
    path("", views.host_list),
    path('host/list/', views.host_list),
    path('host/add/', views.host_add),
    path('host/create1/', views.host_create1),
    path('host/create2/', views.host_create2),
    path("host/<int:host_id>/", views.show_detail),
    path("host/save/", views.host_save),
    path("host/osuser/check/", views.osuser_check),
    path("host/osuser/async_check/", views.osuser_async_check),
    path("host/osuser/async_check_detail/<str:task_uuid>", views.osuser_async_check_detail, name="async_check_detail"),

    path("host/osuser/list/", views.osuser_list),

    path("host/dbinst/list/", views.dbinst_list),
    path("host/dbinst/preadd/", views.dbinst_preadd),
    path("host/dbinst/create/", views.dbinst_create),
    path("host/dbinst/add/", views.dbinst_add),
    path("host/dbinst/<int:instance_id>/", views.dbinst_detail),
    path("host/dbinst/save/", views.dbinst_save),

    path("host/dbuser/list/", views.dbuser_list),

]
