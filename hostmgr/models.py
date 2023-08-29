from django.db import models
from mirage import fields

# pip install django-import-export
#
# Installing collected packages: xlwt, markuppy, xlrd, tablib, et-xmlfile, \
#            diff-match-patch, defusedxml, openpyxl, odfpy, django-import-export
#
# Successfully installed defusedxml-0.7.1 diff-match-patch-20230430 django-import-export-3.2.0
#                        et-xmlfile-1.1.0 markuppy-1.14 odfpy-1.4.1 openpyxl-3.1.2
#                        tablib-3.5.0 xlrd-2.0.1 xlwt-1.3.0


# HOST_STAT_DICT = { '10': '初创建', '20': '已上线', '30': '已下线', '40': '已回收' }
# HOST_STAT_CHOICES = [ (10, '初创建'), (20, '已上线'), (30, '已下线'), (40, '已回收') ]
# HOST_TYPE_DICT = { '10': 'PHY','20': 'VM','30': 'ECS','40': 'RDS' }
# HOST_TYPE_CHOICES = [ (10, 'PHY'), (20, 'VM'), (30, 'ECS'), (40, 'RDS') ]
# DB_INSTNACE_TYPE_DICT = {'10': 'Oracle', '20': 'MySQL', '30': 'Postgresql', '40': 'MsSQL', '50': 'TiDB'}
# DB_INSTNACE_TYPE_CHOICES = [(10, 'Oracle'), (20, 'MySQL'), (30, 'Postgresql'), (40, 'MsSQL'), (50, 'TiDB')]


HOST_OSUSER_TYPE_DICT = {'1': '管理账号', '2': '登录账号', '3': '其它账号'}
HOST_OSUSER_TYPE_CHOICES = [(1, '管理账号'), (2, '登录账号'), (3, '其它账号')]

HOST_DBUSER_TYPE_DICT = {'1': 'SYS', '2': 'SYSTEM', '3': 'ROOT', '4': 'DBA', '5': '监控', '6': '其它'}
HOST_DBUSER_TYPE_CHOICES = [(1, 'SYS'), (2, 'SYSTEM'), (3, 'ROOT'), (4, 'DBA'), (5, '监控'), (6, '其它')]


class OsType(models.Model):
    """
    主机-基础设置-1-OS类型设置
    比如:
    insert into host_conf_ostype(id, osname, osdesc) values
    (11, 'RedHat6', 'RedHat Enterprise Linux 6 x86 64bit'),
    (12, 'RedHat7', 'RedHat Enterprise Linux 7 x86 64bit'),
    (13, 'RedHat8', 'RedHat Enterprise Linux 8 x86 64bit'),
    (21, 'CentOS6', 'CentOS Enterprise Linux 6 x86 64bit'),
    (22, 'CentOS7', 'CentOS Enterprise Linux 7 x86 64bit'),
    (23, 'CentOS8', 'CentOS Enterprise Linux 8 x86 64bit'),
    (31, 'Ubuntu16','Ubuntu16 Server LTS x86 64bit'),
    (32, 'Ubuntu18','Ubuntu18 Server LTS x86 64bit'),
    (33, 'Ubuntu20','Ubuntu20 Server LTS x86 64bit'),
    (34, 'Ubuntu22','Ubuntu20 Server LTS x86 64bit');
    """
    osname = models.CharField(verbose_name='OS名称', max_length=20, unique=True)
    osdesc = models.CharField(verbose_name='OS详述', max_length=60)

    def __str__(self):
        return self.osname

    class Meta:
        managed = True
        db_table = 'host_conf_ostype'
        verbose_name = 'OS类型'
        verbose_name_plural = 'OS类型设置'


class Contact(models.Model):
    """
    主机-基础设置-2-联系人设置
    """
    name = models.CharField(verbose_name='姓名', max_length=30, unique=True)
    mobile = models.CharField(verbose_name='电话', max_length=30)
    job = models.CharField(verbose_name='职务', max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'host_conf_contact'
        verbose_name = '联系人'
        verbose_name_plural = '1.联系人设置'


class MachRoom(models.Model):
    """
    主机-基础设置-3-机房设置
    比如:
    insert into host_conf_machroom(id, name, remark) values
    ( 1, '老楼机房', '聚鲨环球精选-老楼机房'),
    ( 2, '新楼机房', '聚鲨环球精选-新楼机房'),
    ( 3, '世纪互联M5', '世纪互联M5机房'),
    ( 4, '世纪互联M6', '世纪互联M6机房'),
    ( 5, '阿里云Cloud', '阿里云Cloud'),
    ( 6, 'AzureCloud', 'AzureCloud');
    """
    name = models.CharField(verbose_name='机房名称', max_length=30)
    contact = models.ForeignKey(Contact, verbose_name='负责人', on_delete=models.CASCADE, null=True)
    remark = models.CharField(verbose_name='备注', blank=True, max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'host_conf_machroom'
        verbose_name = '机房'
        verbose_name_plural = '2.机房设置'


class Business(models.Model):
    """
    主机-基础设置-4-业务设置
    insert into host_conf_business(id, name) values
    ( 1, '环球云-生产'), ( 2, '云商城-生产'), ( 3, '悦家繁荣-生产'),
    ( 4, '环球云-测试'), ( 5, '云商城-测试'), ( 6, '悦家繁荣-测试');
    """
    name = models.CharField(verbose_name='业务名称', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'host_conf_business'
        verbose_name = '业务'
        verbose_name_plural = '3.业务设置'


class HostType(models.Model):
    """
    主机-基础设置-主机类型设置
    insert into host_conf_hosttype(id, name) values (10, 'PHY'),(20, 'VM'),(30, 'ECS'),(40, 'RDS');
    """
    name = models.CharField(verbose_name='主机类型', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'host_conf_hosttype'
        verbose_name = '主机类型'
        verbose_name_plural = '主机类型设置'


class HostStat(models.Model):
    """
    主机-基础设置-主机状态设置
    insert into host_conf_hoststat(id, name) values (10, '初创建'),(20, '已上线'),(30, '已下线'),(40, '已回收');
    """
    name = models.CharField(verbose_name='主机状态', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'host_conf_hoststat'
        verbose_name = '主机状态'
        verbose_name_plural = '主机状态设置'


class HostSpec(models.Model):
    """
    主机-基础设置-主机规格设置
    insert into host_conf_hostspec(id, name) values
    (11, '2C / 4G / 300G' ),
    (21, '4C / 8G / 300G' ),
    (22, '4C / 8G / 500G' ),
    (23, '4C / 8G /1000G' ),
    (31, '8C /16G / 500G' ),
    (32, '8C /16G /1000G' ),
    (41, '16C/32G / 500G' ),
    (42, '16C/32G /1000G' ),
    (51, '16C/64G / 500G' ),
    (52, '16C/64G /1000G' ),
    (61, '32C/64G / 500G' ),
    (62, '32C/64G /1000G' ),
    (63, '32C/64G /1500G' );
    """
    name = models.CharField(verbose_name='主机规格', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'host_conf_hostspec'
        verbose_name = '主机规格'
        verbose_name_plural = '主机规格设置'


class Host(models.Model):
    """
      null=True : 字段允许为空
      blank=True: admin维护界面允许该字段为空, 无论是text输入域或者下拉框选择域
      max_length=64: 允许varchar字段最大可容纳多少字节长度
    """

    display = models.CharField(verbose_name='显示名', max_length=64, null=True, blank=False)
    hostname = models.CharField(verbose_name='主机名', max_length=64, null=True, blank=False)
    ipaddr = models.CharField(verbose_name='主机IP', max_length=64, null=False)
    sshport = models.IntegerField(verbose_name='SSH端口', default=22, null=True, blank=False)
    rootpswd = fields.EncryptedCharField(verbose_name='ROOT密码', max_length=255, null=False)

    norm_username = models.CharField(verbose_name='普通用户', max_length=64, null=True, blank=True)
    norm_userpswd = fields.EncryptedCharField(verbose_name='用户密码', max_length=64, null=True, blank=True)
    ostype = models.ForeignKey(OsType, verbose_name='OS类型', on_delete=models.CASCADE, null=True, blank=True)
    machroom = models.ForeignKey(MachRoom, verbose_name='所属机房', on_delete=models.CASCADE, null=True, blank=True)
    business = models.ForeignKey(Business, verbose_name='所属业务', on_delete=models.CASCADE, null=True, blank=True)

    hosttype = models.ForeignKey(HostType, verbose_name='主机类型', on_delete=models.CASCADE, null=True, blank=True)
    hoststat = models.ForeignKey(HostStat, verbose_name='主机状态', on_delete=models.CASCADE, null=True, blank=True)
    # hosttype_id = models.IntegerField(verbose_name='主机类型', choices=HOST_TYPE_CHOICES, null=True, blank=True)
    # hoststat_id = models.IntegerField(verbose_name='主机状态', choices=HOST_STAT_CHOICES, null=True, blank=True)

    hostspec = models.ForeignKey(HostSpec, verbose_name='所属主机规格', on_delete=models.CASCADE, null=True, blank=True)
    contact = models.ForeignKey(Contact, verbose_name='联系人', on_delete=models.CASCADE, null=True, blank=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    modify_time = models.DateTimeField(verbose_name='修改时间', auto_now_add=True)
    remark = models.CharField(verbose_name='备注信息', max_length=500, null=True, blank=True)  # blank=True
    vip = models.CharField(verbose_name='VIP', max_length=15, null=True, blank=True)  # blank=True
    otherip = models.CharField(verbose_name='其它IP', max_length=128, null=True, blank=True)  # blank=True

    def __str__(self):
        return self.display

    class Meta:
        managed = True
        db_table = 'host_record'
        verbose_name = '主机'
        verbose_name_plural = '4.主机设置'


class HostOsUser(models.Model):
    host = models.ForeignKey(Host, verbose_name='主机', on_delete=models.CASCADE)
    username = models.CharField(verbose_name='用户名', max_length=64, blank=False)
    password = fields.EncryptedCharField(verbose_name='密码', max_length=64, blank=False)
    remark = models.CharField(verbose_name='备注', null=True, blank=True, max_length=200)

    def __str__(self):
        return self.username

    class Meta:
        managed = True
        db_table = 'host_osuser'
        verbose_name = '主机OS用户'
        verbose_name_plural = '5.OS用户设置'


class DBType(models.Model):
    """
    主机-基础设置-DB类型设置
    insert into host_conf_dbtype(id, name) values (10, 'oracle'),(20, 'mysql'),(30, 'postgresql'),(40, 'tidb'),(50, 'mssql');
    """
    name = models.CharField(verbose_name='DB类型', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'host_conf_dbtype'
        verbose_name = 'DB类型'
        verbose_name_plural = 'DB类型设置'


class HostDBInst(models.Model):
    # display = models.CharField(verbose_name='实例显示名', max_length=64, null=False, blank=False)

    dbtype = models.ForeignKey(DBType, verbose_name='DB类型', on_delete=models.CASCADE, null=False, blank=False)
    host = models.ForeignKey(Host, verbose_name='主机', on_delete=models.CASCADE, null=False, blank=False)
    serv_port = models.CharField(verbose_name='服务端口', max_length=8, null=False, blank=False)
    serv_name = models.CharField(verbose_name='服务名称', max_length=64, default='', null=True, blank=True)  # oracle实例
    inst_name = models.CharField(verbose_name='实例名', max_length=64, default='', null=True, blank=True)  # oracle实例
    other_serv_name = models.CharField(verbose_name='其它服务名', max_length=64, default='', null=True, blank=True)

    cluster_scanip = models.CharField(verbose_name='集群ScanIP', max_length=64, default='', null=True,
                                      blank=True)  # oracle实例
    cluster_port = models.CharField(verbose_name='集群服务端口', max_length=8, default='', null=True,
                                    blank=True)  # oracle实例

    sys_pswd = fields.EncryptedCharField(verbose_name='SYS密码', max_length=64, default='', null=True,
                                         blank=True)  # oracle实例
    system_pswd = fields.EncryptedCharField(verbose_name='SYSTEM密码', max_length=64, default='', null=True,
                                            blank=True)  # oracle实例
    root_pswd = fields.EncryptedCharField(verbose_name='root账号密码', max_length=64, default='', null=True,
                                          blank=True)  # mysql实例

    dba_acct_name = models.CharField(verbose_name='DBA账号名称', max_length=64, default='', null=True,
                                     blank=True)  # oracle实例
    dba_acct_pswd = fields.EncryptedCharField(verbose_name='DBA账号密码', max_length=64, default='', null=True,
                                              blank=True)
    mon_acct_name = models.CharField(verbose_name='监控账号名称', max_length=64, default='', null=True,
                                     blank=True)  # oracle实例
    mon_acct_pswd = fields.EncryptedCharField(verbose_name='监控账号密码', max_length=64, default='', null=True,
                                              blank=True)

    # adm_acct_name = models.CharField(verbose_name='管理员账号名称', max_length=64, null=True, blank=True)          # mysql库需要登记
    # adm_acct_pswd = fields.EncryptedCharField(verbose_name='管理员账号密码', max_length=64, null=True, blank=True) # mysql库需要登记

    def __str__(self):
        # DBTYPE:  (10, 'oracle'), (20, 'mysql'), (30, 'postgresql'), (40, 'tidb'), (50, 'mssql')
        if self.dbtype_id == 10:
            return self.host.ipaddr + ":" + self.serv_port + "/" + self.serv_name
        else:
            return self.host.ipaddr + ":" + self.serv_port

    class Meta:
        managed = True
        unique_together = [["host", "serv_port", "inst_name"]]
        db_table = 'host_dbinst'
        verbose_name = 'DB实例'
        verbose_name_plural = '6.DB实例设置'


class HostDBUser(models.Model):
    instance = models.ForeignKey(HostDBInst, verbose_name='HostDB实例', on_delete=models.CASCADE, null=False,
                                 blank=False)
    username = models.CharField(verbose_name='用户名', max_length=64, default='', null=False, blank=False)
    password = fields.EncryptedCharField(verbose_name='密码', max_length=64, default='', null=False, blank=False)
    remark = models.CharField(verbose_name='备注', max_length=200, default='', null=False, blank=True)

    def __str__(self):
        return self.instance.__str__() + " --> dbuser = " + self.username

    class Meta:
        managed = True
        db_table = 'host_dbuser'
        verbose_name = 'DB账号'
        verbose_name_plural = '7.DB账号设置'
