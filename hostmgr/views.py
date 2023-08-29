# -*- coding: UTF-8 -*-

# from django.forms.models import model_to_dict
# from django.core import serializers
# from django.core.paginator import Paginator
# import traceback

import time
import socket
import uuid

from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.urls import reverse

import simplejson as json
import paramiko
import logging
import sys

from django_q.tasks import async_task
from django.http import JsonResponse
from django.shortcuts import HttpResponse, render
from django.db.models import Q
from common.utils.paginator import Page
from .models import Host, HostOsUser, Business, HostSpec, MachRoom, OsType, \
    Contact, HostStat, HostType, HOST_OSUSER_TYPE_CHOICES, HostDBInst, DBType, HostDBUser, HOST_DBUSER_TYPE_DICT, \
    HOST_DBUSER_TYPE_CHOICES

# HOST_STAT_CHOICES, HOST_STAT_DICT
# HOST_OSUSER_TYPE_DICT,
# HOST_TYPE_CHOICES, HOST_TYPE_DICT


logger = logging.getLogger('default')


def init_logger():
    logger.setLevel(level=logging.INFO)
    logger_format = logging.Formatter("[%(asctime)s]-[%(levelname)s]: %(message)s")  # output format
    sh = logging.StreamHandler(stream=sys.stdout)  # output to standard output
    sh.setFormatter(logger_format)
    logger.addHandler(sh)


def host_create1(request):
    """
        保存
    :param request:
    :return:
    """
    osuser = request.POST.get("osuser", "")
    display = request.POST.get("display", "")
    hostname = request.POST.get("hostname", "")
    sshport = request.POST.get("sshport", "")
    ipaddr = request.POST.get("ipaddr", "")
    rootpswd = request.POST.get("rootpswd", "")
    remark = request.POST.get("remark", "")
    vip = request.POST.get("vip", "")
    otherip = request.POST.get("otherip", "")
    norm_username = request.POST.get("norm_username", "")
    norm_userpswd = request.POST.get("norm_userpswd", "")
    hosttype = request.POST.get("hosttype")
    hoststat = request.POST.get("hoststat")
    ostype = request.POST.get("ostype")
    hostspec = request.POST.get("hostspec")
    business = request.POST.get("business")
    machroom = request.POST.get("machroom")
    contact = request.POST.get("contact")
    osuser_target_list = []
    for _osuser in osuser.split("|"):
        if _osuser and len(_osuser) > 0:
            osuser_target_list.append(_osuser.split("/"))
    try:
        host = Host.objects.create(display=display, hostname=hostname, ipaddr=ipaddr, sshport=sshport,
                                   rootpswd=rootpswd)
        host.norm_username = norm_username.strip()
        host.norm_userpswd = norm_userpswd.strip()
        host.remark = remark.strip()
        host.vip = vip.strip()
        host.otherip = otherip.strip()
        if hosttype and len(hosttype) > 0:
            host.hosttype_id = int(hosttype)
        if hoststat and len(hoststat) > 0:
            host.hoststat_id = int(hoststat)
        if ostype and len(ostype) > 0:
            host.ostype_id = int(ostype)
        if hostspec and len(hostspec) > 0:
            host.hostspec_id = int(hostspec)
        if business and len(business) > 0:
            host.business_id = int(business)
        if machroom and len(machroom) > 0:
            host.machroom_id = int(machroom)
        if contact and len(contact) > 0:
            host.contact_id = int(contact)
        host.save()

        for item in osuser_target_list:
            _osuser = HostOsUser.objects.create(username=item[0], password=item[1], remark=item[2], host_id=host.id)
            _osuser.save()

    except Exception as msg:
        result = {'status': 1, 'msg': f'{msg}', 'rows': []}
        return HttpResponse(json.dumps(result), content_type='application/json')

    result = {'status': 0, 'msg': '主机%s创建成功！' % hostname}
    return HttpResponse(json.dumps(result), content_type='application/json')


def host_create2(request):
    """
        保存并添加另一个
    :param request:
    :return:
    """
    px_total = int(request.POST.get("osuser_set-TOTAL_FORMS", "9"))
    px_start = int(request.POST.get("osuser_set-INITIAL_FORMS", "0"))

    osuser_name = []
    osuser_pswd = []

    for i in range(px_start, px_total):
        _tmp_name = request.POST.get("osuser_set-%d-username" % i, "")
        _tmp_pswd = request.POST.get("osuser_set-%d-password" % i, "")
        osuser_name.append(_tmp_name)
        osuser_pswd.append(_tmp_pswd)

    # print("osuser_name ==== >")
    # print(osuser_name)
    # print("osuser_pswd ==== >")
    # print(osuser_pswd)

    try:
        pass
    except Exception as msg:
        return JsonResponse({'status': 1, 'msg': f'{msg}', 'rows': []})

    result = {'status': 0, 'msg': 'ok'}
    return HttpResponse(json.dumps(result), content_type='application/json')

    # return HttpResponseRedirect('/pre_add_host/')
    # return redirect('/pre_add_host/')


def host_add(request):
    """
        预增加主机
    :param request:
    :return:
    """
    business_list = Business.objects.all().values('id', 'name')
    hostspec_list = HostSpec.objects.all().values("id", "name")
    ostype_list = OsType.objects.all().values('id', 'osname')
    machroom_list = MachRoom.objects.all().values('id', 'name')
    contact_list = Contact.objects.all().values('id', 'name')
    hosttype_list = HostType.objects.all().values('id', 'name')
    hoststat_list = HostStat.objects.all().values('id', 'name')

    context = {
        "hosttype_list": hosttype_list,
        "hoststat_list": hoststat_list,
        "business_list": business_list,
        "hostspec_list": hostspec_list,
        "ostype_list": ostype_list,
        "machroom_list": machroom_list,
        "contact_list": contact_list,
    }
    return render(request, "host_add.html", context)


def host_list(request):
    """
        主机列表
        :param request:
        :return:
    """
    # 过滤筛选项的数据
    ostype_id = request.POST.get("ostype_id", "")
    business_id = request.POST.get("business_id", "")
    hosttype_id = request.POST.get("hosttype_id", "")
    hoststat_id = request.POST.get("hoststat_id", "")
    machroom_id = request.POST.get("machroom_id", "")
    hostspec_id = request.POST.get("hostspec_id", "")
    search = request.POST.get('search')
    filter_dict = dict()
    if business_id and len(business_id) > 0:
        filter_dict['business_id'] = business_id
    if hosttype_id and len(hosttype_id) > 0:
        filter_dict['hosttype_id'] = hosttype_id
    if ostype_id and len(ostype_id) > 0:
        filter_dict['ostype_id'] = ostype_id
    if hoststat_id and len(hoststat_id) > 0:
        filter_dict['hoststat_id'] = hoststat_id
    if machroom_id and len(machroom_id) > 0:
        filter_dict['machroom_id'] = machroom_id
    if hostspec_id and len(hostspec_id) > 0:
        filter_dict['hostspec_id'] = hostspec_id

    # 过滤组合筛选项
    host_records = Host.objects.all().filter(**filter_dict)
    # 过滤搜索项，模糊检索项包括主机名、Display、主机ip、备注
    if search:
        host_records = host_records.filter(
            Q(hostname__contains=search) | Q(display__contains=search) | Q(ipaddr__contains=search) | Q(
                remark__contains=search))
    count = host_records.count()

    if request.POST.get('page') and len(request.POST.get('page')) > 0:
        curr_page = int(request.POST.get('page'))
    else:
        curr_page = 1
    per_page = int(request.POST.get('per_page', 15))

    offset = (curr_page - 1) * per_page
    limit = offset + per_page

    host_records = host_records.order_by("id")[offset:limit]
    paginator = Page(host_records, count, per_page=per_page, number=curr_page)

    business_list = Business.objects.all().values('id', 'name')
    hostspec_list = HostSpec.objects.all().values("id", "name")
    ostype_list = OsType.objects.all().values('id', 'osname')
    machroom_list = MachRoom.objects.all().values('id', 'name')
    hosttype_list = HostType.objects.all().values('id', 'name')
    hoststat_list = HostStat.objects.all().values('id', 'name')

    param_dict = dict()
    param_dict['hosttype_id'] = hosttype_id
    param_dict['hoststat_id'] = hoststat_id
    param_dict['business_id'] = business_id
    param_dict['hostspec_id'] = hostspec_id
    param_dict['ostype_id'] = ostype_id
    param_dict['machroom_id'] = machroom_id

    context = {
        "filter_dict": filter_dict,
        "param_dict": param_dict,
        # "hosttype_id": hosttype_id, "hoststat_id": hoststat_id, "business_id": business_id,
        # "hostspec_id": hostspec_id, "ostype_id": ostype_id, "machroom_id": machroom_id,
        "hosttype_list": hosttype_list,
        "hoststat_list": hoststat_list,
        "business_list": business_list,
        "hostspec_list": hostspec_list,
        "ostype_list": ostype_list,
        "machroom_list": machroom_list,
        "paginator": paginator,
        "page": curr_page,
        "per_page": per_page,
    }
    return render(request, 'host_list.html', context)


def show_detail(request, host_id):
    # host = get_object_or_404(Host, pk=host_id)
    host = Host.objects.get(pk=host_id)
    os_user = host.hostosuser_set.all()

    business_list = Business.objects.all().values('id', 'name')
    hostspec_list = HostSpec.objects.all().values("id", "name")
    ostype_list = OsType.objects.all().values('id', 'osname')
    machroom_list = MachRoom.objects.all().values('id', 'name')
    contact_list = Contact.objects.all().values('id', 'name')
    hosttype_list = HostType.objects.all().values('id', 'name')
    hoststat_list = HostStat.objects.all().values('id', 'name')

    context = {"host": host,
               "os_user": os_user,
               "hosttype_list": hosttype_list,
               "hoststat_list": hoststat_list,
               "business_list": business_list,
               "hostspec_list": hostspec_list,
               "ostype_list": ostype_list,
               "machroom_list": machroom_list,
               "contact_list": contact_list
               }
    return render(request, 'host_detail.html', context)


def osuser_list(request):
    accttype_id = request.POST.get("accttype_id", "")  # 账号类型, 1:root,2:login_user,3:other_users
    hosttype_id = request.POST.get("hosttype_id", "")  # 主机类型
    hoststat_id = request.POST.get("hoststat_id", "")  # 主机状态
    ostype_id = request.POST.get("ostype_id", "")  # 操作系统类型
    business_id = request.POST.get("business_id", "")  # 所属业务
    search_keyword = request.POST.get('search_keyword', '')  # 搜索关键字

    # print('search_keyword =', search_keyword)

    filter_dict = dict()
    # 不能加入到filter_dict中，否则Host.objects.all().filter(**filter_dict)报错!
    if ostype_id and len(ostype_id) > 0:
        filter_dict['ostype_id'] = ostype_id
    if business_id and len(business_id) > 0:
        filter_dict['business_id'] = business_id
    if hosttype_id and len(hosttype_id) > 0:
        filter_dict['hosttype'] = hosttype_id
    if hoststat_id and len(hoststat_id) > 0:
        filter_dict['hoststat'] = hoststat_id

    host_records = Host.objects.all().filter(**filter_dict)
    if search_keyword and len(search_keyword.strip()) > 0:
        host_records = host_records.filter(
            Q(hostname__contains=search_keyword) | Q(display__contains=search_keyword) | Q(
                ipaddr__contains=search_keyword) | Q(
                remark__contains=search_keyword) | Q(display__contains=search_keyword)
        )

    result_list = []
    if accttype_id == "1" or accttype_id == '':
        for item in host_records:
            # print (item.ipaddr, item.hoststat, item.hosttype)
            if item.ostype_id == 91:
                username = "administrator"
            else:
                username = "root"
            result_list.append(
                {'host_id': item.id,
                 'hosttype_id': item.hosttype_id,
                 'hoststat_id': item.hoststat_id,
                 'business_id': item.business_id,
                 'ostype_id': item.ostype_id,
                 'display': item.display,
                 'hostname': item.hostname,
                 'ipaddr': item.ipaddr,
                 'sshport': item.sshport,
                 'accttype_id': 1,
                 'username': username,
                 'password': item.rootpswd
                 })

    if accttype_id == "2" or accttype_id == '':
        for item in host_records:
            if item.norm_username and len(item.norm_username) > 0:
                result_list.append(
                    {'host_id': item.id,
                     'hosttype_id': item.hosttype_id,
                     'hoststat_id': item.hoststat_id,
                     'business_id': item.business_id,
                     'ostype_id': item.ostype_id,
                     'display': item.display,
                     'hostname': item.hostname,
                     'ipaddr': item.ipaddr,
                     'sshport': item.sshport,
                     'accttype_id': 2,
                     'username': item.norm_username,
                     'password': item.norm_userpswd
                     })

    if accttype_id == "3" or accttype_id == '':
        for item in host_records:
            if item.hostosuser_set:
                # print(item.hostosuser_set.all())
                for osu in item.hostosuser_set.all():
                    result_list.append(
                        {'host_id': item.id,
                         'hosttype_id': item.hosttype_id,
                         'hoststat_id': item.hoststat_id,
                         'business_id': item.business_id,
                         'ostype_id': item.ostype_id,
                         'display': item.display,
                         'hostname': item.hostname,
                         'ipaddr': item.ipaddr,
                         'sshport': item.sshport,
                         'accttype_id': 3,
                         'username': osu.username,
                         'password': osu.password
                         })

    count = len(result_list)
    if request.POST.get('page') and len(request.POST.get('page')) > 0:
        curr_page = int(request.POST.get('page'))
    else:
        curr_page = 1
    per_page = int(request.POST.get('per_page', 15))

    offset = (curr_page - 1) * per_page
    limit = offset + per_page
    paginator = Page(result_list[offset:limit], count, per_page=per_page, number=curr_page)

    business_list = Business.objects.all().values('id', 'name')
    ostype_list = OsType.objects.all().values('id', 'osname')
    hosttype_list = HostType.objects.all().values('id', 'name')
    hoststat_list = HostStat.objects.all().values('id', 'name')

    param_dict = dict()
    param_dict['accttype_id'] = accttype_id
    param_dict['hosttype_id'] = hosttype_id
    param_dict['hoststat_id'] = hoststat_id
    param_dict['business_id'] = business_id
    param_dict['ostype_id'] = ostype_id
    param_dict['search_keyword'] = search_keyword if search_keyword and len(search_keyword) > 0 else ''

    context = {
        "param_dict": param_dict,
        "filter_dict": filter_dict,
        "accttype_list": HOST_OSUSER_TYPE_CHOICES,
        "hosttype_list": hosttype_list,  # HOST_TYPE_CHOICES,
        "hoststat_list": hoststat_list,  # HOST_STAT_CHOICES,
        "business_list": business_list,
        "ostype_list": ostype_list,
        "paginator": paginator,
        "page": curr_page,
        "per_page": per_page,
    }
    return render(request, 'host_osuser_list.html', context)


def osuser_async_check(request):
    """
    在这里增加 异步执行任务的操作
    (1) 获取所有待验证的osuser_list列表
    (2) 发起异步任务, 返回task_id,
        任务里要把所有待验证的osuser_list列表,逐一登录验证OS用户密码，验证结果记录到指定的model中
    (3) 返回到前端页面，把osuser_list展示出来，并且每5秒刷新展示页面，一旦后台检索任务执行完毕，就停止页面的刷新
        刷新方法为执行url检索本次任务的操作结果
    """
    # ==========================================
    # 1 获取OS_USER_PSWD 列表
    # ==========================================

    # 1.1 排除ostype_id=91[windows], hosttype=40[RDS], 以及aliyun的mysql主机
    list1 = Host.objects.all().filter(~Q(ostype__id=91) & ~Q(hosttype=40) &
                                      ~(Q(machroom__id=5) & Q(ipaddr__icontains='mysql.rds.aliyuncs.com'))
                                      ).values('id', 'ipaddr', 'sshport', 'rootpswd').order_by('ipaddr')
    # 1.2 排除ostype_id=91[windows], hosttype=40[RDS]的主机记录, 并且排除norm_username=NULL，并且排除norm_username=空白字符''
    list2 = Host.objects.all().filter(
        ~Q(ostype__id=91) & ~Q(hosttype=40) & ~Q(norm_username='') & ~Q(norm_username__isnull=True)).values('id',
                                                                                                            'ipaddr',
                                                                                                            'sshport',
                                                                                                            'norm_username',
                                                                                                            'norm_userpswd').order_by(
        'ipaddr')
    # 1.3 排除ostype_id=91[windows], hosttype=40[RDS]的主机记录下的 OSUSER记录
    list3 = HostOsUser.objects.all().filter(~Q(host__ostype=91) & ~Q(host__hosttype=40)).order_by('host__ipaddr', 'id')

    task_check_list = []
    for item in list1:
        task_check_list.append(
            {'ipaddr': item['ipaddr'], 'sshport': item['sshport'], 'username': 'root', 'password': item['rootpswd'],
             'type': '1-root', 'check_result': '待验证'})
    for item in list2:
        task_check_list.append(
            {'ipaddr': item['ipaddr'], 'sshport': item['sshport'], 'username': item['norm_username'],
             'password': item['norm_userpswd'], 'type': '2-normuser', 'check_result': '待验证'})
    for item in list3:
        task_check_list.append({'ipaddr': item.host.ipaddr, 'sshport': item.host.sshport, 'username': item.username,
                                'password': item.password, 'type': '3-osuser', 'check_result': '待验证'})
    # ==========================================
    # 2 发起异步任务, 返回task_id
    # ==========================================
    # timestr = datetime.datetime.now().strftime("%m%d%H%M%S")  # "%Y%m%d_%H%M%S.%f"
    # timestr = time.strftime("%y%m%d-%H%M%S", time.localtime())

    task_uuid = uuid.uuid4().__str__()
    task_key_result = "task_result_" + task_uuid
    task_key_detail = "task_detail_" + task_uuid
    cache.set(task_key_detail, task_check_list, 3600)
    task_result_dict = {"status": "running", "start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        "end_time": ""}
    cache.set(task_key_result, task_result_dict, 3600)
    async_task(
        "hostmgr.hostmgr_tasks.task_check_osuser_pswd",
        task_key_result,
        task_key_detail,
        task_check_list,
        timeout=3600,
    )
    # ==========================================
    # 3 返回到前端页面，把osuser_list展示出来，并且每5秒刷新展示页面，一旦后台检索任务执行完毕，就停止页面的刷新
    # ==========================================
    return HttpResponseRedirect(reverse("hostmgr:async_check_detail", args=(task_uuid,)))


def osuser_async_check_detail(request, task_uuid):
    """
    在这里增加 异步执行任务的操作
    (1) 获取所有待验证的osuser_list列表
    (2) 发起异步任务, 返回task_id,
        任务里要把所有待验证的osuser_list列表,逐一登录验证OS用户密码，验证结果记录到指定的model中
    (3) 返回到前端页面，把osuser_list展示出来，并且每5秒刷新展示页面，一旦后台检索任务执行完毕，就停止页面的刷新
        刷新方法为执行url
    """
    task_key_result = 'task_result_' + task_uuid
    task_key_detail = 'task_detail_' + task_uuid
    cache_task_result = cache.get(task_key_result)
    cache_task_detail = cache.get(task_key_detail)
    cache_task_detail.sort(key=lambda chk_item: (chk_item['check_result'], chk_item['ipaddr'], chk_item['username']))
    context = {
        "task_uuid": task_uuid,
        "cache_task_result": cache_task_result,
        "cache_task_detail": cache_task_detail,
    }
    return render(request, 'host_osuser_async_check_result.html', context)


def osuser_check(request):
    # 1.排除ostype_id=91[windows], hosttype=40[RDS]的主机记录
    list1 = Host.objects.all().filter(
        ~Q(ostype__id=91) & ~Q(hosttype=40) &
        ~(Q(machroom__id=5) & Q(ipaddr__icontains='mysql.rds.aliyuncs.com'))
    ).values('id', 'ipaddr', 'sshport', 'rootpswd').order_by('ipaddr')

    # 2.排除ostype_id=91[windows], hosttype=40[RDS]的主机记录, 并且排除norm_username=NULL，并且排除norm_username=空白字符''
    list2 = Host.objects.all().filter(
        ~Q(ostype__id=91) & ~Q(hosttype=40) &
        ~Q(norm_username='') & ~Q(norm_username__isnull=True)
    ).values('id', 'ipaddr', 'sshport', 'norm_username', 'norm_userpswd').order_by(
        'ipaddr')

    # 3.排除ostype_id=91[windows], hosttype=40[RDS]的主机记录下的 OSUSER记录
    list3 = HostOsUser.objects.all().filter(
        ~Q(host__ostype=91) & ~Q(host__hosttype=40)
    ).order_by('host__ipaddr', 'id')

    target_list = []
    check_result_list = []
    for item in list1:
        target_list.append(
            {'ipaddr': item['ipaddr'], 'sshport': item['sshport'], 'username': 'root', 'password': item['rootpswd'],
             'type': '1-root', 'check_result': ''})
    for item in list2:
        target_list.append(
            {'ipaddr': item['ipaddr'], 'sshport': item['sshport'], 'username': item['norm_username'],
             'password': item['norm_userpswd'], 'type': '2-normuser', 'check_result': ''})
    for item in list3:
        target_list.append({'ipaddr': item.host.ipaddr, 'sshport': item.host.sshport, 'username': item.username,
                            'password': item.password, 'type': '3-osuser', 'check_result': ''})

    # {'ipaddr': '12.18.0.16', 'sshport': 22, 'username': 'root', 'password': 'sAXlUaT&kZ3vpGF$', 'type': '1-root'}
    # {'ipaddr': '10.31.0.19', 'sshport': 22, 'username': 'centos', 'password': 'ghs@123', 'type': '2-normuser'}
    # {'ipaddr': '12.18.0.16', 'sshport': 22, 'username': 'oracle', 'password': 'oracle', 'type': '3-osuser'}

    # timeout  banner_timeout  auth_timeout
    # 1. timeout:        tcp连接超时
    # 2. banner_timeout: ssh守护进程响应时间的超时，默认是15秒
    # 3. auth_timeout:   验证授权超时

    sshclient = paramiko.SSHClient()
    sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    cnt = 0
    # 依次检查登陆状况
    for item in target_list:
        # print(item)
        cnt += 1
        print("开始登陆验证:", cnt, "-", item['ipaddr'])
        begin_dat = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        try:
            sshclient.connect(hostname=item['ipaddr'], port=item['sshport'], username=item['username'],
                              password=item['password'],
                              timeout=15.0,
                              banner_timeout=6, auth_timeout=15)
            item['check_result'] = '登陆成功，校验通过!'
            logger.info('登陆成功，校验通过! {} {} {}'.format(item['ipaddr'], item['sshport'], item['username']))
        except socket.timeout:
            logger.info(item['ipaddr'] + " exception ==> socket.timeout")
            item['check_result'] = '校验失败! IP或端口不通！'
        except paramiko.ssh_exception.AuthenticationException:
            logger.info(item['ipaddr'] + "exception ====> paramiko.ssh_exception.AuthenticationException")
            item['check_result'] = '校验失败! 用户密码不匹配！'

        end_dat = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        logger.info(
            "结束登陆验证. {} {} {} FR:{} TO:{}".format(item['ipaddr'], item['sshport'], item['username'], begin_dat,
                                                        end_dat))
        if item['check_result'] == '登陆成功，校验通过!':
            check_result_list.append(item)
        else:
            check_result_list.insert(0, item)
        if sshclient:
            sshclient.close()
    context = {"check_result_list": check_result_list}
    return render(request, 'host_osuser_check_result.html', context)


def host_save(request):
    """
        保存修改
    :param request:
    :return:
    """
    osuser = request.POST.get("osuser", "")
    host_id = int(request.POST.get("host_id"))
    display = request.POST.get("display", "")
    hostname = request.POST.get("hostname", "")
    sshport = request.POST.get("sshport", "")
    ipaddr = request.POST.get("ipaddr", "")
    rootpswd = request.POST.get("rootpswd", "")
    remark = request.POST.get("remark", "")
    vip = request.POST.get("vip", "")
    otherip = request.POST.get("otherip", "")
    norm_username = request.POST.get("norm_username", "")
    norm_userpswd = request.POST.get("norm_userpswd", "")
    hosttype = request.POST.get("hosttype")
    hoststat = request.POST.get("hoststat")
    ostype = request.POST.get("ostype")
    hostspec = request.POST.get("hostspec")
    business = request.POST.get("business")
    machroom = request.POST.get("machroom")
    contact = request.POST.get("contact")
    osuser_target_list = []

    if osuser:
        for item in osuser.split("|"):
            if item and len(item) > 0:
                osuser_target_list.append(item.split("/"))
    try:
        host = Host.objects.get(id=host_id)
        host.display = display
        host.hostname = hostname
        host.ipaddr = ipaddr
        host.sshport = sshport
        host.rootpswd = rootpswd
        host.norm_username = norm_username.strip()
        host.norm_userpswd = norm_userpswd.strip()
        host.remark = remark.strip()
        host.vip = vip.strip()
        host.otherip = otherip.strip()
        if hosttype and len(hosttype) > 0:
            host.hosttype_id = int(hosttype)
        if hoststat and len(hoststat) > 0:
            host.hoststat_id = int(hoststat)
        if ostype and len(ostype) > 0:
            host.ostype_id = int(ostype)
        if hostspec and len(hostspec) > 0:
            host.hostspec_id = int(hostspec)
        if business and len(business) > 0:
            host.business_id = int(business)
        if machroom and len(machroom) > 0:
            host.machroom_id = int(machroom)
        if contact and len(contact) > 0:
            host.contact_id = int(contact)
        host.save()
        for item in osuser_target_list:
            if item[0] == "0":
                # create osuser
                HostOsUser.objects.create(username=item[1], password=item[2], remark=item[3], host_id=host_id)
            else:
                # 还需判断, 是删除还是修改
                if item[1].strip() == "" and item[1].strip() == "" and item[1].strip() == "":
                    # delete osuser
                    HostOsUser.objects.filter(pk=int(item[0])).delete()
                else:
                    # update osuser
                    HostOsUser.objects.filter(pk=int(item[0])).update(username=item[1], password=item[2],
                                                                      remark=item[3],
                                                                      host_id=host_id)
    except Exception as msg:
        result = {'status': 1, 'msg': f'{msg}', 'rows': []}
        return HttpResponse(json.dumps(result), content_type='application/json')

    result = {'status': 0, 'msg': '主机%s修改成功！' % hostname}
    return HttpResponse(json.dumps(result), content_type='application/json')


def dbinst_list(request):
    dbtype_id = request.POST.get("dbtype_id", "")  # 账号类型, 1:root,2:login_user,3:other_users
    search = request.POST.get('search', '')  # 搜索关键字

    filter_dict = dict()
    filter_dict['dbtype_id'] = dbtype_id
    dbinst_records = HostDBInst.objects.all()

    if dbtype_id and len(dbtype_id.strip()) > 0:
        dbinst_records = dbinst_records.filter(**filter_dict)

    # 过滤搜索项，模糊检索项包括主机名、Display、主机ip、备注
    if search and len(search.strip()) > 0:
        dbinst_records = dbinst_records.filter(
            Q(host__ipaddr__contains=search)
        )
    count = dbinst_records.count()

    if request.POST.get('page') and len(request.POST.get('page')) > 0:
        curr_page = int(request.POST.get('page'))
    else:
        curr_page = 1
    per_page = int(request.POST.get('per_page', 15))

    offset = (curr_page - 1) * per_page
    limit = offset + per_page
    host_records = dbinst_records.order_by("id")[offset:limit]
    paginator = Page(host_records, count, per_page=per_page, number=curr_page)

    dbtype_list = DBType.objects.all().values('id', 'name')
    context = {
        "filter_dict": filter_dict,
        "paginator": paginator,
        "page": curr_page,
        "per_page": per_page,
        "dbtype_id": dbtype_id,
        "dbtype_list": dbtype_list,
    }
    return render(request, 'dbinst_list.html', context)


def dbinst_preadd(request):
    """
        增加DB实例
    :param request:
    :return:
    """
    dbtype_list = DBType.objects.all().values('id', 'name')
    _host_list = Host.objects.all().values('id', 'hostname', 'ipaddr').order_by("ipaddr")
    context = {
        "dbtype_list": dbtype_list,
        "host_list": _host_list,
    }
    return render(request, "dbinst_add.html", context)


def dbinst_create(request):
    """
        新增并返回
    :param request:
    :return:
    """
    dbtype_id = request.POST.get("dbtype_id", "")
    host_id = request.POST.get("host_id", "")
    serv_port = request.POST.get("serv_port", "").strip()
    inst_name = request.POST.get("inst_name", "").strip()
    serv_name = request.POST.get("serv_name", "").strip()
    other_serv_name = request.POST.get("other_serv_name", "").strip()
    cluster_scanip = request.POST.get("cluster_scanip", "").strip()
    cluster_port = request.POST.get("cluster_port", "").strip()
    dba_acct_name = request.POST.get("dba_acct_name", "").strip()
    dba_acct_pswd = request.POST.get("dba_acct_pswd", "").strip()
    mon_acct_name = request.POST.get("mon_acct_name", "").strip()
    mon_acct_pswd = request.POST.get("mon_acct_pswd", "").strip()
    sys_pswd = request.POST.get("sys_pswd", "").strip()
    system_pswd = request.POST.get("system_pswd", "").strip()
    root_pswd = request.POST.get("root_pswd", "").strip()
    dbuser = request.POST.get("dbuser", "").strip()

    dbuser_target_list = []
    for _dbuser in dbuser.split("|"):
        if _dbuser and len(_dbuser) > 0:
            dbuser_target_list.append(_dbuser.split("/"))
    try:
        dbinst = HostDBInst.objects.create(
            dbtype_id=dbtype_id, host_id=host_id, serv_port=serv_port,
            inst_name=inst_name, serv_name=serv_name, other_serv_name=other_serv_name,
            cluster_scanip=cluster_scanip, cluster_port=cluster_port,
            dba_acct_name=dba_acct_name, mon_acct_name=mon_acct_name
        )

        if dba_acct_pswd and len(dba_acct_pswd) > 0:
            dbinst.dba_acct_pswd = dba_acct_pswd
        if mon_acct_pswd and len(mon_acct_pswd) > 0:
            mon_acct_pswd = mon_acct_pswd
        if mon_acct_pswd and len(mon_acct_pswd) > 0:
            dbinst.sys_pswd = sys_pswd
        if mon_acct_pswd and len(mon_acct_pswd) > 0:
            dbinst.system_pswd = system_pswd
        if mon_acct_pswd and len(mon_acct_pswd) > 0:
            dbinst.root_pswd = root_pswd

        dbinst.save()

        for item in dbuser_target_list:
            if item[0].lower() == dba_acct_name:
                dbinst.dba_acct_pswd = item[1].strip()
                dbinst.save()
            elif item[0].lower() == mon_acct_name:
                dbinst.mon_acct_pswd = item[1].strip()
                dbinst.save()
            elif item[0].lower() == "sys":
                dbinst.sys_pswd = item[1].strip()
                dbinst.save()
            elif item[0].lower() == "system":
                dbinst.system_pswd = item[1].strip()
                dbinst.save()
            elif item[0].lower() == "root":
                dbinst.root_pswd = item[1].strip()
                dbinst.save()
            _dbuser = HostDBUser.objects.create(username=item[0].strip(), password=item[1].strip(),
                                                remark=item[2].strip(), instance_id=dbinst.id)
            # _dbuser.save()
    except Exception as msg:
        result = {'status': 1, 'msg': f'{msg}', 'rows': []}
        return HttpResponse(json.dumps(result), content_type='application/json')

    result = {'status': 0, 'msg': 'DB实例创建成功！实例id=%s' % dbinst.id}
    return HttpResponse(json.dumps(result), content_type='application/json')


def dbinst_add(request):
    """
        保存并添加另一个
    :param request:
    :return:
    """
    return dbinst_create(request)


def dbinst_save(request):
    """
        保存并返回
    :param request:
    :return:
    """

    dbinst_id = int(request.POST.get("dbinst_id"))
    dbtype_id = request.POST.get("dbtype_id", "")
    serv_port = request.POST.get("serv_port", "").strip()
    inst_name = request.POST.get("inst_name", "").strip()
    serv_name = request.POST.get("serv_name", "").strip()
    other_serv_name = request.POST.get("other_serv_name", "").strip()
    cluster_scanip = request.POST.get("cluster_scanip", "").strip()
    cluster_port = request.POST.get("cluster_port", "").strip()
    dba_acct_name = request.POST.get("dba_acct_name", "").strip().lower()
    dba_acct_pswd = request.POST.get("dba_acct_pswd", "").strip()
    mon_acct_name = request.POST.get("mon_acct_name", "").strip().lower()
    mon_acct_pswd = request.POST.get("mon_acct_pswd", "").strip()
    sys_pswd = request.POST.get("sys_pswd", "").strip()
    system_pswd = request.POST.get("system_pswd", "").strip()
    root_pswd = request.POST.get("root_pswd", "").strip()

    dbuser = request.POST.get("dbuser", "").strip()
    dbuser_target_list = []

    if dbuser:
        for item in dbuser.split("|"):
            if item and len(item) > 0:
                dbuser_target_list.append(item.split("/"))
    try:
        dbinst = HostDBInst.objects.get(pk=dbinst_id)
        dbinst.dbtype_id = dbtype_id
        dbinst.serv_port = serv_port
        dbinst.inst_name = inst_name
        dbinst.serv_name = serv_name
        dbinst.other_serv_name = other_serv_name
        dbinst.cluster_scanip = cluster_scanip
        dbinst.cluster_port = cluster_port
        dbinst.dba_acct_name = dba_acct_name
        dbinst.mon_acct_name = mon_acct_name

        if dba_acct_pswd and len(dba_acct_pswd) > 0:
            dbinst.dba_acct_pswd = dba_acct_pswd
        if mon_acct_pswd and len(mon_acct_pswd) > 0:
            dbinst.mon_acct_pswd = mon_acct_pswd
        if sys_pswd and len(sys_pswd) > 0:
            dbinst.sys_pswd = sys_pswd
        if system_pswd and len(system_pswd) > 0:
            dbinst.system_pswd = system_pswd
        if root_pswd and len(root_pswd) > 0:
            dbinst.root_pswd = root_pswd
        dbinst.save()

        for item in dbuser_target_list:
            if item[0] == "0":
                if item[1].lower() == "sys":
                    dbinst.sys_pswd = item[2].strip()
                    dbinst.save()
                elif item[1].lower() == "system":
                    dbinst.syste_pswd = item[2].strip()
                    dbinst.save()
                elif item[1].lower() == "root":
                    dbinst.root_pswd = item[2].strip()
                    dbinst.save()
                elif item[1].lower() == dba_acct_name.lower():
                    dbinst.dba_acct_pswd = item[2].strip()
                    dbinst.save()
                elif item[1].lower() == mon_acct_name.lower():
                    dbinst.mon_acct_pswd = item[2].strip()
                    dbinst.save()
                else:
                    # create dbuser
                    HostDBUser.objects.create(username=item[1], password=item[2], remark=item[3], instance_id=dbinst_id)
            else:
                # 还需判断, 是删除还是修改
                if item[1].strip() == "" and item[2].strip() == "" and item[3].strip() == "":
                    # delete dbuser
                    HostDBUser.objects.filter(pk=int(item[0])).delete()
                else:
                    # update dbuser
                    # HostDBUser.objects.filter(pk=int(item[0]))
                    HostDBUser.objects.filter(pk=int(item[0])).update(username=item[1], password=item[2],
                                                                      remark=item[3])

    except Exception as msg:
        print(msg)
        result = {'status': 1, 'msg': f'{msg}', 'rows': []}
        return HttpResponse(json.dumps(result), content_type='application/json')

    result = {'status': 0, 'msg': 'DB实例%s修改成功！' % (dbinst.host.ipaddr + ":" + dbinst.serv_port)}
    return HttpResponse(json.dumps(result), content_type='application/json')


def dbinst_detail(request, instance_id):
    dbinst = HostDBInst.objects.get(pk=instance_id)
    _dbuser_list = dbinst.hostdbuser_set.all()
    dbtype_list = DBType.objects.all().values('id', 'name')
    context = {"dbinst": dbinst, "dbuser_list": _dbuser_list, "dbtype_list": dbtype_list, }
    return render(request, 'dbinst_detail.html', context)


def dbuser_list(request):
    dbtype_id = request.POST.get("dbtype_id", "")  # 实例类型
    dbuser_type_id = request.POST.get("dbuser_type_id", "")  # 账号类型
    search = request.POST.get('search', '')  # 搜索关键字

    filter_dict = dict()
    if dbtype_id and len(dbtype_id) > 0:
        filter_dict['dbtype_id'] = dbtype_id

    param_dict = dict()
    param_dict['dbtype_id'] = dbtype_id
    param_dict['dbuser_type_id'] = dbuser_type_id

    dbinst_records = HostDBInst.objects.all().filter(**filter_dict)
    if search and len(search.strip()) > 0:
        dbinst_records = dbinst_records.filter(
            Q(host__ipaddr__contains=search)
            | Q(inst_name__contains=search)
            | Q(serv_name__contains=search)
            | Q(other_serv_name__contains=search)
            | Q(dba_acct_name__contains=search)
            | Q(mon_acct_name__contains=search)
        )

    # HOST_DBUSER_TYPE_DICT = {'1': 'SYS', '2': 'SYSTEM', '3': 'ROOT', '4': 'DBA', '5': '监控', '6': '其它'}
    result_list = []
    if dbuser_type_id == "1" or dbuser_type_id == '':
        ## sys
        for item in dbinst_records:
            if item.sys_pswd and len(item.sys_pswd) > 0:
                result_list.append(
                    {'dbinst_id': item.id,
                     'dbtype_name': item.dbtype.name,
                     'ipaddr': item.host.ipaddr,
                     'serv_port': item.serv_port,
                     'serv_name': item.serv_name,
                     'other_serv_name': item.other_serv_name,
                     'dbuser_type': HOST_DBUSER_TYPE_DICT['1'],
                     'username': 'sys',
                     'password': item.sys_pswd,
                     })

    if dbuser_type_id == "2" or dbuser_type_id == '':
        ## system
        for item in dbinst_records:
            if item.system_pswd and len(item.system_pswd) > 0:
                result_list.append(
                    {'dbinst_id': item.id,
                     'dbtype_name': item.dbtype.name,
                     'ipaddr': item.host.ipaddr,
                     'serv_port': item.serv_port,
                     'serv_name': item.serv_name,
                     'other_serv_name': item.other_serv_name,
                     'dbuser_type': HOST_DBUSER_TYPE_DICT['2'],
                     'username': 'system',
                     'password': item.system_pswd,
                     })

    if dbuser_type_id == "3" or dbuser_type_id == '':
        ## root
        for item in dbinst_records:
            if item.root_pswd and len(item.root_pswd) > 0:
                result_list.append(
                    {'dbinst_id': item.id,
                     'dbtype_name': item.dbtype.name,
                     'ipaddr': item.host.ipaddr,
                     'serv_port': item.serv_port,
                     'serv_name': item.serv_name,
                     'other_serv_name': item.other_serv_name,
                     'dbuser_type': HOST_DBUSER_TYPE_DICT['3'],
                     'username': 'system',
                     'password': item.root_pswd,
                     })

    if dbuser_type_id == "4" or dbuser_type_id == '':
        ## dba account
        for item in dbinst_records:
            if item.dba_acct_name and item.dba_acct_pswd \
                    and len(item.dba_acct_name) > 0 and len(item.dba_acct_pswd) > 0:
                result_list.append(
                    {'dbinst_id': item.id,
                     'dbtype_name': item.dbtype.name,
                     'ipaddr': item.host.ipaddr,
                     'serv_port': item.serv_port,
                     'serv_name': item.serv_name,
                     'other_serv_name': item.other_serv_name,
                     'dbuser_type': HOST_DBUSER_TYPE_DICT['4'],
                     'username': item.dba_acct_name,
                     'password': item.dba_acct_pswd
                     })

    if dbuser_type_id == "5" or dbuser_type_id == '':
        ## monitor account
        for item in dbinst_records:
            if item.mon_acct_name and item.mon_acct_pswd \
                    and len(item.mon_acct_name) > 0 and len(item.mon_acct_pswd) > 0:
                result_list.append(
                    {'dbinst_id': item.id,
                     'dbtype_name': item.dbtype.name,
                     'ipaddr': item.host.ipaddr,
                     'serv_port': item.serv_port,
                     'serv_name': item.serv_name,
                     'other_serv_name': item.other_serv_name,
                     'dbuser_type': HOST_DBUSER_TYPE_DICT['5'],
                     'username': item.mon_acct_name,
                     'password': item.mon_acct_pswd
                     })

    if dbuser_type_id == "6" or dbuser_type_id == '':
        ## root
        for item in dbinst_records:
            if item.hostdbuser_set:
                for dbu in item.hostdbuser_set.all():
                    result_list.append(
                        {'dbinst_id': item.id,
                         'dbtype_name': item.dbtype.name,
                         'ipaddr': item.host.ipaddr,
                         'serv_port': item.serv_port,
                         'serv_name': item.serv_name,
                         'other_serv_name': item.other_serv_name,
                         'dbuser_type': HOST_DBUSER_TYPE_DICT['6'],
                         'username': dbu.username,
                         'password': dbu.password
                         })

    count = len(result_list)
    if request.POST.get('page') and len(request.POST.get('page')) > 0:
        curr_page = int(request.POST.get('page'))
    else:
        curr_page = 1
    per_page = int(request.POST.get('per_page', 15))

    offset = (curr_page - 1) * per_page
    limit = offset + per_page
    paginator = Page(result_list[offset:limit], count, per_page=per_page, number=curr_page)

    dbtype_list = DBType.objects.all().values('id', 'name')
    context = {
        "param_dict": param_dict,
        "filter_dict": filter_dict,
        "dbuser_type_list": HOST_DBUSER_TYPE_CHOICES,
        "dbtype_list": dbtype_list,
        "paginator": paginator,
        "page": curr_page,
        "per_page": per_page,
    }
    return render(request, 'host_dbuser_list.html', context)

# def task_check_osuser_pswd():
#     # print("task_name:", task_name)
#     print("in task detail, befroe sleep!")
#     time.sleep(10)
#     print("in task detail, after sleep 10s!")
