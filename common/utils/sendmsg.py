# -*- coding: UTF-8 -*-

import json
import email
import smtplib
import requests
import logging
import traceback
from email import encoders
from email.header import Header
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart

from common.config import SysConfig
from sql.utils.ding_api import get_access_token
from sql.utils.wx_api import get_wx_access_token, get_wx_headers

logger = logging.getLogger('default')


class MsgSender(object):

    def __init__(self, **kwargs):
        if kwargs:
            self.MAIL_REVIEW_SMTP_SERVER = kwargs.get('server')
            self.MAIL_REVIEW_SMTP_PORT = kwargs.get('port', 0)
            self.MAIL_REVIEW_FROM_ADDR = kwargs.get('user')
            self.MAIL_REVIEW_FROM_PASSWORD = kwargs.get('password')
            self.MAIL_SSL = kwargs.get('ssl')
        else:
            sys_config = SysConfig()
            # email信息
            self.MAIL_REVIEW_SMTP_SERVER = sys_config.get('mail_smtp_server')
            self.MAIL_REVIEW_SMTP_PORT = sys_config.get('mail_smtp_port', 0)
            self.MAIL_SSL = sys_config.get('mail_ssl')
            self.MAIL_REVIEW_FROM_ADDR = sys_config.get('mail_smtp_user')
            self.MAIL_REVIEW_FROM_PASSWORD = sys_config.get('mail_smtp_password')
            # 钉钉信息
            self.ding_agent_id = sys_config.get('ding_agent_id')
            # 企业微信信息
            self.wx_agent_id = sys_config.get('wx_agent_id')

        if self.MAIL_REVIEW_SMTP_PORT:
            self.MAIL_REVIEW_SMTP_PORT = int(self.MAIL_REVIEW_SMTP_PORT)
        elif self.MAIL_SSL:
            self.MAIL_REVIEW_SMTP_PORT = 465
        else:
            self.MAIL_REVIEW_SMTP_PORT = 25

    @staticmethod
    def _add_attachment(filename):
        """
        添加附件
        :param filename:
        :return:
        """
        file_msg = email.mime.base.MIMEBase('application', 'octet-stream')
        file_msg.set_payload(open(filename, 'rb').read())
        # 附件如果有中文会出现乱码问题，加入gbk
        file_msg.add_header('Content-Disposition', 'attachment', filename=('gbk', '',
                                                                           filename.split('/')[-1]))
        encoders.encode_base64(file_msg)

        return file_msg

    def send_email(self, subject, body, to, **kwargs):
        """
        发送邮件
        :param subject:
        :param body:
        :param to:
        :param kwargs:
        :return: str: 成功为 'success'
                      有异常为 traceback信息
        """

        try:
            if not to:
                logger.warning('收件人为空，无法发送邮件')
                return
            if not isinstance(to, list):
                raise TypeError('收件人需要为列表')
            list_cc = kwargs.get('list_cc_addr', [])
            if not isinstance(list_cc, list):
                raise TypeError('抄送人需要为列表')

            # 构造MIMEMultipart对象做为根容器
            main_msg = email.mime.multipart.MIMEMultipart()

            # 添加文本内容
            text_msg = email.mime.text.MIMEText(body, 'plain', 'utf-8')
            main_msg.attach(text_msg)

            # 添加附件
            filename_list = kwargs.get('filename_list')
            if filename_list:
                for filename in kwargs['filename_list']:
                    file_msg = self._add_attachment(filename)
                    main_msg.attach(file_msg)

            # 消息内容:
            main_msg['Subject'] = Header(subject, "utf-8").encode()
            #main_msg['From'] = formataddr(["Archery 通知", self.MAIL_REVIEW_FROM_ADDR])
            main_msg['From'] = formataddr(["SQL审核通知", self.MAIL_REVIEW_FROM_ADDR])
            main_msg['To'] = ','.join(list(set(to)))
            main_msg['Cc'] = ', '.join(str(cc) for cc in list(set(list_cc)))
            main_msg['Date'] = email.utils.formatdate()

            #if self.MAIL_SSL:
            #    server = smtplib.SMTP_SSL(self.MAIL_REVIEW_SMTP_SERVER, self.MAIL_REVIEW_SMTP_PORT)  # 默认SSL端口是465
            #else:
            #    server = smtplib.SMTP(self.MAIL_REVIEW_SMTP_SERVER, self.MAIL_REVIEW_SMTP_PORT)  # 默认端口是25

            ## 如果提供的密码为空，则不需要登录
            #if self.MAIL_REVIEW_FROM_PASSWORD:
            #    server.login(self.MAIL_REVIEW_FROM_ADDR, self.MAIL_REVIEW_FROM_PASSWORD)
            
            server = smtplib.SMTP('localhost') 
             
            server.sendmail(self.MAIL_REVIEW_FROM_ADDR, to + list_cc, main_msg.as_string())
            server.quit()
            logger.debug(f'邮件推送成功\n消息标题:{subject}\n通知对象：{to + list_cc}\n消息内容：{body}')
            return 'success'
        except Exception:
            errmsg = '邮件推送失败\n{}'.format(traceback.format_exc())
            logger.error(errmsg)
            return errmsg

    @staticmethod
    def send_ding(url, content):
        """
        发送钉钉Webhook消息
        :param url:
        :param content:
        :return:
        """
        data = {
            "msgtype": "text",
            "text": {
                "content": "{}".format(content)
            },
        }
        r = requests.post(url=url, json=data)
        r_json = r.json()
        if r_json['errcode'] == 0:
            logger.debug(f'钉钉Webhook推送成功\n通知对象：{url}\n消息内容：{content}')
        else:
            logger.error("""钉钉Webhook推送失败
错误码:{}
返回错误信息:{}
请求url:{}
请求data:{}""".format(r_json['errcode'], r_json['errmsg'], url, data))

    def send_ding2user(self, userid_list, content):
        """
        发送钉钉消息到个人
        :param userid_list:
        :param content:
        :return:
        """
        access_token = get_access_token()
        data = {
            "userid_list": ','.join(list(set(userid_list))),
            "agent_id": self.ding_agent_id,
            "msg": {"msgtype": "text", "text": {"content": f"{content}"}},
        }
        r = requests.post(
            url=f"https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token={access_token}",
            json=data)
        r_json = r.json()
        if r_json['errcode'] == 0:
            logger.debug(f'钉钉推送成功\n通知对象：{userid_list}\n消息内容：{content}')
        else:
            logger.error("""钉钉推送失败
错误码:{}
返回错误信息:{}
请求url:{}
请求data:{}""".format(r_json['errcode'], r_json['errmsg'], userid_list, data))

    def send_wx2user(self, msg, user_list):
        to_user = '|'.join(list(set(user_list)))
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s' % get_wx_access_token()
        dict_data = {
            "touser": to_user,
            "msgtype": "markdown",
            "agentid": self.wx_agent_id,
            "markdown": {
                "content": msg
            },
        }
        res = requests.post(send_url, json=dict_data, headers=get_wx_headers(), timeout=5, verify=True)
        r_json = res.json()
        if r_json['errcode'] == 0:
            logger.debug(f'企业微信推送成功\n通知对象：{to_user}')
        else:
            logger.error("""企业微信推送失败
                            错误码:{}
                            返回错误信息:{}
                            """.format(r_json['errcode'], json.dumps(r_json)))
