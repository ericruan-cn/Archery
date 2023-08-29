# -*- coding:utf8 -*-
# Author: RuanCT

from import_export import resources
from .models import Host, HostOsUser, HostDBInst, HostDBUser


class HostResource(resources.ModelResource):
    class Meta:
        model = Host


class HostOsUserResource(resources.ModelResource):
    class Meta:
        model = HostOsUser


class HostDBInstResource(resources.ModelResource):
    class Meta:
        model = HostDBInst


class HostDBUserResource(resources.ModelResource):
    class Meta:
        model = HostDBUser
