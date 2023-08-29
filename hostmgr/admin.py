from django.contrib import admin
from .models import Business, Contact, MachRoom, OsType, DBType, HostSpec, HostType, HostStat, HostOsUser, Host, \
    HostDBUser, \
    HostDBInst
from .resource import HostResource, HostOsUserResource, HostDBInstResource, HostDBUserResource
from import_export.admin import ImportExportModelAdmin


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    ordering = ('id',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'mobile', 'job')
    ordering = ('id',)


@admin.register(MachRoom)
class HostRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'remark', 'contact')
    ordering = ('id',)


@admin.register(DBType)
class DBTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    ordering = ('id',)


@admin.register(OsType)
class OsTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'osname', 'osdesc')
    ordering = ('id',)


@admin.register(HostSpec)
class HostSpecAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    ordering = ('id',)


@admin.register(HostType)
class HostTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    ordering = ('id',)


@admin.register(HostStat)
class HostStatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    ordering = ('id',)


@admin.register(HostOsUser)
class HostOsUserAdmin(ImportExportModelAdmin):
    resource_class = HostOsUserResource
    list_display = ('id', 'host', 'username', 'password', 'remark')
    ordering = ('id',)


@admin.register(Host)
class HostAdmin(ImportExportModelAdmin):
    resource_class = HostResource
    list_display = (
        'id',
        'display',
        'hostname',
        'sshport',
        'ipaddr',
        'rootpswd',
        'norm_username',
        'norm_userpswd',
        'ostype',
        'machroom',
        'business',
        'hosttype_id',
        'hoststat_id',
        'hostspec',
        'contact',
        'create_time',
        'modify_time',
        'remark',
        'vip',
        'otherip',
    )
    search_fields = ('id', 'hostname', 'display')
    list_display_links = ('id', 'hostname',)
    ordering = ('id',)


@admin.register(HostDBInst)
class HostDBInstAdmin(ImportExportModelAdmin):
    resource_class = HostDBInstResource
    list_display = (
        'id',
        # 'display',
        'host',
        'dbtype',
        'inst_name',
        'serv_name',
        'serv_port',
        'other_serv_name',
        'sys_pswd',
        'system_pswd',
        'root_pswd',
        'cluster_scanip',
        'cluster_port',
        'dba_acct_name',
        'dba_acct_pswd',
        'mon_acct_name',
        'mon_acct_pswd',
    )
    search_fields = ('id', 'display', 'host', 'dbtype', 'inst_name', 'serv_name', 'serv_port', 'other_serv_name')
    list_display_links = ('id',)
    ordering = ('id',)


@admin.register(HostDBUser)
class HostDBUserAdmin(ImportExportModelAdmin):
    resource_class = HostDBUserResource
    list_display = (
        'id',
        'instance',
        'username',
        'password',
        'remark',
    )
    search_fields = ('id', 'instance', 'username',)
    list_display_links = ('id',)
    ordering = ('id',)
