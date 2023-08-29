# -*- coding:utf8 -*-
# Author: RuanCT

# from django.utils.translation import gettext_lazy as _
# from django.core.paginator import InvalidPage, PageNotAnInteger, EmptyPage

import math


class Page(object):

    def __init__(self, object_list, count, per_page=10, number=1, allow_empty_first_page=True):

        self.page_bar_size_max = 10
        # self.page_bar_size = 7

        # 当前页数据列表
        self.object_list = object_list
        # 总记录数
        self.count = count
        # 每页记录数
        self.per_page = per_page
        # 是否允许空首页
        self.allow_empty_first_page = allow_empty_first_page

        self.num_pages = math.ceil(count / per_page)
        self.page_range = range(1, self.num_pages + 1)

        # 验证当前页码
        self.number = self.validate_number(number)

        # 计算以下值
        self.start_index = (number - 1) * per_page + 1
        if self.number == self.num_pages:
            self.end_index = count
        else:
            self.end_index = number * per_page

    def validate_number(self, number):
        """Validate the given 1-based page number."""
        try:
            # if isinstance(number, float) and not number.is_integer():
            if isinstance(number, float):
                # raise ValueError
                return 1
            number = int(number)
        except (TypeError, ValueError):
            # raise PageNotAnInteger(_('That page number is not an integer'))
            return 1

        if number < 1:
            # raise EmptyPage(_('That page number is less than 1'))
            return 1
        if number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                pass
            else:
                # raise EmptyPage(_('That page contains no results'))
                number = self.num_pages
        return number

    def has_next(self):
        return self.number < self.num_pages

    def has_previous(self):
        return self.number > 1

    def has_other_pages(self):
        return self.has_previous() or self.has_next()

    def next_page_number(self):
        return self.validate_number(self.number + 1)

    def previous_page_number(self):
        return self.validate_number(self.number - 1)

    def page_bar_html(self):

        if self.count == 0:
            return "共 0 行记录"

        page_bar_html_list = []

        # {{ paginator.start_index}} ~ {{ paginator.end_index }} 行，共 {{ paginator.count }}
        html = """
            <div class="pull-left">
                <div class="form-group form-inline">
                    显示第 {0} ~ {1} 行，共 {2} 行记录，
                    每页 <select id="per_page" name="per_page" class="form-control" onchange="changePerPage(this.form, this.value)" >
                    <option>10</option>
                    <option>15</option>
                    <option>20</option>
                    <option>50</option>
                    <option>80</option>
                </select> 行
                </div>
            </div>
        """.format(self.start_index, self.end_index, self.count)
        page_bar_html_list.append(html)
        html = '<div class=" box-tools pull-right"> <ul id="page-bar" class="pagination" >'
        page_bar_html_list.append(html)

        # html = '<li><a href="?page=1&per_page=%d">首页</a></li>' % self.per_page
        html = '<li><a href="javascript:void(0);" onclick="gotoPage(%d)">首页</a></li>' % 1
        page_bar_html_list.append(html)

        if self.number <= 1:
            # html = '<li class="disabled"><a href="#">上一页</a></li>'
            html = '<li class="disabled"><a href="javascript:void(0);">上一页</a></li>'
        else:
            # html = '<li><a href="?page=%d&per_page=%d">上一页</a></li>' % (self.number - 1, self.per_page)
            html = '<li><a href="javascript:void(0);" onclick="gotoPage(%d)">上一页</a></li>' % (self.number - 1)
        page_bar_html_list.append(html)

        page_bar_size_half = math.floor(self.page_bar_size_max / 2)
        if self.num_pages <= self.page_bar_size_max:
            for i in range(1, (self.num_pages + 1)):
                if i == self.number:
                    # html = '<li class="active"><a href="#">%d</a></li>' % i
                    html = '<li class="active"><a href="javascript:void(0);">%d</a></li>' % i
                else:
                    # html = '<li><a href="?page=%d&per_page=%d">%d</a></li>' % (i, self.per_page, i)
                    html = '<li><a href="javascript:void(0);" onclick="gotoPage(%d)">%d</a></li>' % (i, i)
                page_bar_html_list.append(html)
        else:
            if self.number <= page_bar_size_half:
                for i in range(1, (page_bar_size_half + 1 + 1)):
                    if i == self.number:
                        # html = '<li class="active"><a href="#">%d</a></li>' % i
                        html = '<li class="active"><a href="javascript:void(0);">%d</a></li>' % i
                    else:
                        # html = '<li><a href="?page=%d&per_page=%d">%d</a></li>' % (i, self.per_page, i)
                        html = '<li><a href="javascript:void(0);" onclick="gotoPage(%d)">%d</a></li>' % (i, i)
                    page_bar_html_list.append(html)
                # html = '<li class="disabled"><a href="#">..</a></li>'
                html = '<li class="disabled"><a href="javascript:void(0);">..</a></li>'
                page_bar_html_list.append(html)
                # html = '<li><a href="?page=%d&per_page=%d">%d</a></li>' % (self.num_pages, self.per_page, self.num_pages)
                html = '<li><a href="javascript:void(0);" onclick="gotoPage(%d)">%d</a></li>' % (
                    self.num_pages, self.num_pages)
                page_bar_html_list.append(html)

            elif self.number > self.num_pages - page_bar_size_half:

                # html = '<li><a href="?page=1">1</a></li>'
                html = '<li><a href="javascript:void(0);" onclick="gotoPage(%d)">%d</a></li>' % (1, 1)
                page_bar_html_list.append(html)
                # html = '<li class="disabled"><a href="#">..</a></li>'
                html = '<li class="disabled"><a href="javascript:void(0);">..</a></li>'
                page_bar_html_list.append(html)
                for i in range(self.num_pages - page_bar_size_half, self.num_pages + 1):
                    if i == self.number:
                        # html = '<li class="active"><a href="#">%d</a></li>' % i
                        html = '<li class="active"><a href="javascript:void(0);">%d</a></li>' % i
                    else:
                        # html = '<li><a href="?page=%d&per_page=%d">%d</a></li>' % (i, self.per_page, i)
                        html = '<li><a href="javascript:void(0);" onclick="gotoPage(%d)">%d</a></li>' % (i, i)
                    page_bar_html_list.append(html)
            else:

                # html = '<li><a href="?page=1">1</a></li>'
                html = '<li><a href="javascript:void(0);" onclick="gotoPage(%d)">%d</a></li>' % (1, 1)
                page_bar_html_list.append(html)
                # html = '<li class="disabled"><a href="#">..</a></li>'
                html = '<li class="disabled"><a href="javascript:void(0);">..</a></li>'
                page_bar_html_list.append(html)
                for i in range(self.number - 1, (self.number + 1 + 1)):
                    if i == self.number:
                        # html = '<li class="active"><a href="#">%d</a></li>' % i
                        html = '<li class="active"><a href="javascript:void(0);">%d</a></li>' % i
                    else:
                        # html = '<li><a href="?page=%d&per_page=%d">%d</a></li>' % (i, self.per_page, i)
                        html = '<li><a href="javascript:void(0);" onclick="gotoPage(%d)">%d</a></li>' % (i, i)
                    page_bar_html_list.append(html)
                # html = '<li class="disabled"><a href="#">..</a></li>'
                html = '<li class="disabled"><a href="javascript:void(0);">..</a></li>'
                page_bar_html_list.append(html)
                # html = '<li><a href="?page=%d&per_page=%d">%d</a></li>' % (self.num_pages, self.per_page, self.num_pages)
                html = '<li><a href="javascript:void(0);" onclick="gotoPage(%d)">%d</a></li>' % (
                    self.num_pages, self.num_pages)
                page_bar_html_list.append(html)

        if self.number >= self.num_pages:
            # html = '<li class="disabled"><a href="#">下一页</a></li>'
            html = '<li class="disabled"><a href="javascript:void(0);">下一页</a></li>'
        else:
            # html = '<li><a href="?page=%d&per_page=%d">下一页</a></li>' % (self.number + 1, self.per_page)
            html = '<li><a href="javascript:void(0);" onclick="gotoPage(%d)">下一页</a></li>' % (self.number + 1)
        page_bar_html_list.append(html)

        # html = '<li><a href="?page=%d&per_page=%d">尾页</a></li>' % (self.num_pages, self.per_page)
        html = '<li><a href="javascript:void(0);" onclick="gotoPage(%d)">尾页</a></li>' % self.num_pages
        page_bar_html_list.append(html)

        html = "</ul></div>"
        page_bar_html_list.append(html)

        return ''.join(page_bar_html_list)
