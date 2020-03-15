# -*- coding: UTF-8 -*-
""" 
@author: hhyo
@license: Apache Licence
@file: sql_utils.py
@time: 2019/03/13
"""
import re
import xml
import mybatis_mapper2sql
import sqlparse

from sql.engines.models import SqlItem
from sql.utils.extract_tables import extract_tables as extract_tables_by_sql_parse

__author__ = 'hhyo'


def get_syntax_type(sql, parser=True, db_type='mysql'):
    """
    返回SQL语句类型，仅判断DDL和DML
    :param sql:
    :param parser: 是否使用sqlparse解析
    :param db_type: 不使用sqlparse解析时需要提供该参数
    :return:
    """
    sql = remove_comments(sql=sql, db_type=db_type)
    if parser:
        try:
            statement = sqlparse.parse(sql)[0]
            syntax_type = statement.token_first(skip_cm=True).ttype.__str__()
            if syntax_type == 'Token.Keyword.DDL':
                syntax_type = 'DDL'
            elif syntax_type == 'Token.Keyword.DML':
                syntax_type = 'DML'
        except Exception:
            syntax_type = None
    else:
        if db_type == 'mysql':
            ddl_re = r"^alter|^create|^drop|^rename|^truncate"
            dml_re = r"^call|^delete|^do|^handler|^insert|^load\s+data|^load\s+xml|^replace|^select|^update"
        else:
            # TODO 其他数据库的解析正则
            return None
        if re.match(ddl_re, sql, re.I):
            syntax_type = 'DDL'
        elif re.match(dml_re, sql, re.I):
            syntax_type = 'DML'
        else:
            syntax_type = None
    return syntax_type


def remove_comments(sql, db_type='mysql'):
    """
    去除SQL语句中的注释信息
    来源:https://stackoverflow.com/questions/35647841/parse-sql-file-with-comments-into-sqlite-with-python
    :param sql:
    :param db_type:
    :return:
    """
    sql_comments_re = {
        'oracle':
            [r'(?:--)[^\n]*\n', r'(?:\W|^)(?:remark|rem)\s+[^\n]*\n'],
        'mysql':
            [r'(?:#|--\s)[^\n]*\n']
    }
    specific_comment_re = sql_comments_re[db_type]
    additional_patterns = "|"
    if isinstance(specific_comment_re, str):
        additional_patterns += specific_comment_re
    elif isinstance(specific_comment_re, list):
        additional_patterns += "|".join(specific_comment_re)
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/{})".format(additional_patterns)
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

    def _replacer(match):
        if match.group(2):
            return ""
        else:
            return match.group(1)

    return regex.sub(_replacer, sql).strip()


def extract_tables(sql):
    """
    获取sql语句中的库、表名
    :param sql:
    :return:
    """
    tables = list()
    for i in extract_tables_by_sql_parse(sql):
        tables.append({
            "schema": i.schema,
            "name": i.name,
        })
    return tables


def generate_sql(text):
    """
    从SQL文本、MyBatis3 Mapper XML file文件中解析出sql 列表
    :param text:
    :return: [{"sql_id": key, "sql": soar.compress(value)}]
    """
    # 尝试XML解析
    try:
        mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml_raw_text=text)
        statements = mybatis_mapper2sql.get_statement(mapper, result_type='list')
        rows = []
        # 压缩SQL语句，方便展示
        for statement in statements:
            for key, value in statement.items():
                row = {"sql_id": key, "sql": value}
                rows.append(row)
    except xml.etree.ElementTree.ParseError:
        # 删除注释语句
        text = sqlparse.format(text, strip_comments=True)
        statements = sqlparse.split(text)
        rows = []
        num = 0
        for statement in statements:
            num = num + 1
            row = {"sql_id": num, "sql": statement}
            rows.append(row)
    return rows


def get_base_sqlitem_list(sql_strings):
    """功能描述: 把参数sql_strings转变为SqlItem列表
    :param sql_strings: sql字符串,每个SQL以分号(;)间隔。不包含plsql执行块和plsql对象定义块
    :return: SqlItem对象列表
    """
    list = []
    for statement in sqlparse.split(sql_strings):
        statement = sqlparse.format(statement, strip_comments=True)
        if len(statement) <= 0:
            continue
        item = SqlItem(statement=statement)
        list.append(item)
    return list


def get_full_sqlitem_list(full_sql, db_name):
    ''' 获取Sql对应的SqlItem列表, 包括PLSQL部分
        PLSQL语句块由delimiter $$作为开始间隔符，以$$作为结束间隔符
    :param full_sql: 全部sql内容
    :return: SqlItem 列表
    '''
    itemList = []
    # 检查plsql语句块的正则表达式pattern
    # 注意：
    # 如果把package置于package body之前，则永远不会匹配上package body
    plsql_delimiter_regex = r'delimiter\s+\$\$'
    plsql_objdefine_regex = r'create\s+or\s+replace\s+(function|procedure|trigger|package\s+body|package)\s+("?\w+"?\.)?"?\w+"?[\s+|\(]'

    # 对象命名，两端有双引号
    nm_regex = r'^".+"$'

    content_split_list = re.split(pattern=plsql_delimiter_regex, string=full_sql, flags=re.I)
    for content in content_split_list:
        # 截去首尾空格和多余空字符
        content = content.strip()

        # 如果字符串长度为0,则跳过该字符串
        if len(content) <= 0:
            continue

        # 查找是否存在delimiter $$的结束符--> $$
        pos = content.find("$$")
        length = len(content)

        if pos > -1:
            # 该content包含多行结束符$$

            # 处理PLSQL语句块, 这里需要先去判定语句块的类型
            plsql_area = content[0:pos].strip()
            # 如果plsql_area字符串最后一个字符为/,则把/给去掉
            while True:
                if plsql_area[-1:] == '/':
                    plsql_area = plsql_area[:-1].strip()
                else:
                    break

            plsql_check_result = re.search(plsql_objdefine_regex, plsql_area, flags=re.I)

            #  情况1：plsql block for execute
            #  情况2：plsql block for object define
            if plsql_check_result:
                # 此时plsql_area为 object define plsql block
                str_match = plsql_check_result.group()
                str_plsql_type = plsql_check_result.groups()[0]

                idx = str_match.index(str_plsql_type)
                nm_str = str_match[idx + len(str_plsql_type):].strip()

                if nm_str[-1:] == '(':
                    nm_str = nm_str[:-1]
                nm_list = nm_str.split('.')

                if len(nm_list) > 1:
                    # 带有属主的对象名, 形如object_owner.object_name

                    # 获取object_owner
                    if re.match(nm_regex, nm_list[0]):
                        # object_owner两端带有双引号
                        object_owner = nm_list[0].strip().strip('"')
                    else:
                        # object_owner两端不带有双引号
                        object_owner = nm_list[0].upper().strip().strip("'")

                    # 获取object_name
                    if re.match(nm_regex, nm_list[1]):
                        # object_name两端带有双引号
                        object_name = nm_list[1].strip().strip('"')
                    else:
                        # object_name两端不带有双引号
                        object_name = nm_list[1].upper().strip()
                else:
                    # 不带属主
                    object_owner = db_name.upper()
                    if re.match(nm_regex, nm_list[0]):
                        # object_name两端带有双引号
                        object_name = nm_list[0].strip().strip('"')
                    else:
                        # object_name两端不带有双引号
                        object_name = nm_list[0].upper().strip()

                item = SqlItem(statement=plsql_area, stmt_type='PLSQL', object_owner=object_owner,
                               object_name=object_name)
                itemList.append(item)
            else:
                # 此时plsql_area为 executable plsql block, it's ANONYMOUS
                item = SqlItem(statement=plsql_area.strip(), stmt_type='PLSQL', object_owner=db_name.upper(),
                               object_name='ANONYMOUS')
                itemList.append(item)

            if length > pos + 2:
                # 以$$结尾的语句，将止步于此;  只处理$$后续的那些语句
                # 处理第二块SQL
                # 此时SQL为单条可执行SQL集合
                sql_area = content[pos + 2:].strip()
                if len(sql_area) > 0:
                    tmp_list = get_base_sqlitem_list(sql_area)
                    itemList.extend(tmp_list)
        else:
            # 不存在多行结束符$$
            tmp_list = get_base_sqlitem_list(content)
            itemList.extend(tmp_list)
    return itemList


def get_exec_sqlitem_list(reviewResult, db_name):
    """ 根据审核结果生成新的SQL列表
    :param reviewResult: SQL审核结果列表
    :param db_name:
    :return:
    """
    list = []
    list.append(SqlItem(statement=f"ALTER SESSION SET CURRENT_SCHEMA = {db_name}"))

    for item in reviewResult:
        list.append(SqlItem(statement=item['sql'], stmt_type=item['stmt_type'], object_owner=item['object_owner'],
                            object_name=item['object_name']))
    return list
