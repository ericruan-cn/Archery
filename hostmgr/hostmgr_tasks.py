# -*- coding: UTF-8 -*-

from django_q.models import Task
from django.core.cache import cache

import sys
import socket
import paramiko
import datetime, time
import logging

logger = logging.getLogger()


def init_logger():
    logger.setLevel(level=logging.INFO)
    logger_format = logging.Formatter("[%(asctime)s]-[%(levelname)s]: %(message)s")  # output format
    sh = logging.StreamHandler(stream=sys.stdout)  # output to standard output
    sh.setFormatter(logger_format)
    logger.addHandler(sh)


def async_task_info(name):
    """ 获取异步任务详情 """
    try:
        task_obj = Task.objects.get(name=name)
        return task_obj
    except Task.DoesNotExist:
        pass


def task_check_osuser_pswd(task_key_result, task_key_detail, task_check_list):
    ## {'ipaddr': '10.1.1.50', 'sshport': 22, 'username': 'root', 'password': '123456', 'type': '1-root', 'check_result': ''},
    ## timeout  banner_timeout  auth_timeout
    ## 1. timeout:        tcp连接超时
    ## 2. banner_timeout: ssh守护进程显示banner响应时间的超时，默认是15秒
    ## 3. auth_timeout:   验证授权超时

    ## sshclient.connect(hostname='12.18.0.160', port=22, username='root', password='sAXlUaT&kZ3vpGF$',
    #                    timeout=15, banner_timeout=6, auth_timeout=15)
    ## 1. 验证失败,创建不了socket连接,IP或端口不通 ==> socket.timeout: timed out
    ## 2. 验证失败,用户密码不匹配或者验证超时       ==> paramiko.ssh_exception.AuthenticationException:

    logger.info("=============================================================================")
    logger.info("=  异步任务 hostmgr.hostmgr_tasks.task_check_osuser_pswd 开始执行 ...")
    logger.info("=  任务UUID: %s" % task_key_result[11:])
    logger.info("=  开始时间:  %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    logger.info("=============================================================================")
    logger.info("")

    sshclient = paramiko.SSHClient()
    sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    task_result_dict = cache.get(task_key_result)
    total_cnt = len(task_check_list)
    cnt = 0

    # 依次检查登陆状况
    for item in task_check_list:
        cnt += 1
        logger.info("开始登录验证 cnt=%2d, 时间:%s, ipaddr=%s." % (cnt, datetime.datetime.now(), item['ipaddr']))
        try:
            sshclient.connect(hostname=item['ipaddr'], port=item['sshport'], username=item['username'],
                              password=item['password'],
                              timeout=15.0, banner_timeout=6.0, auth_timeout=15.0)
            # stdin, stdout, stderr = sshclient.exec_command('date')  # out, err = stdout.read(), stderr.read()
            item['check_result'] = '登陆成功，校验通过!'
            logger.info('登陆成功, 校验通过！{} {} {}'.format(item['ipaddr'], item['sshport'], item['username']))
        except socket.timeout as e:
            # traceback.print_exc(e)
            item['check_result'] = '登录异常，创建socket连接超时!'
            logger.info(e)
            logger.info(item['ipaddr'] + " exception ===> socket.timeout")
        except paramiko.ssh_exception.AuthenticationException as e:
            # traceback.print_exc(e)
            item['check_result'] = '登录异常，用户密码不匹配或验证超时!'
            logger.info(e)
            logger.info(item['ipaddr'] + "exception ===> paramiko.ssh_exception.AuthenticationException")
        except Exception as e:
            item['check_result'] = '登录异常，发生其它异常!'
            logger.info(e)
            logger.info(item['ipaddr'] + "exception ===> 发生其它异常！")
        logger.info("结束登陆验证. {} {} {} {}, 结束时间:{}".format(item['ipaddr'], item['sshport'], item['username'],
                                                                    item['check_result'], datetime.datetime.now()))
        logger.info("")
        cache.set(task_key_detail, task_check_list, 3600)
        if cnt == total_cnt:
            task_result_dict['status'] = "finish"
            task_result_dict['end_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cache.set(task_key_result, task_result_dict, 3600)
        if sshclient:
            sshclient.close()

    logger.info("=============================================================================")
    logger.info("=  异步任务 hostmgr.hostmgr_tasks.task_check_osuser_pswd 执行完毕.")
    logger.info("=  任务UUID: %s" % task_key_result[11:])
    logger.info("=  完成时间:  %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    logger.info("=============================================================================")
    logger.info("")