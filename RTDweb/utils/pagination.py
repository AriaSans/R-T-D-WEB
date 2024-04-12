"""
    自定义分页组件
    用法：
"views"中：
def pretty_list(request):
# 1.找到要进行分页的列表，获得全部数据的queryset
    queryset = models.PrettyNum.objects.filter(**search_dict).order_by('-level')

# 2.实例化对象，输入request，queryset
        其中隐藏的为： （1）page_size - 一页显示多少行
                    （2）page_param - 在GET请求中代表页数的命名
                    （2）plus - 本页的左/右分别沿伸几页
    paginator_object = Pagination(request, queryset)

# 3.写入context，并传入render
    context ={
        "pretty_list": paginator_object.queryset_list,
        "page_code": paginator_object.html()
    }
    return render(request, 'prtty_list.html', context)

HTML中：
# 4.HTML中，贴入组件
{% for obj in pretty_list %}
    {{ obj.xx }}
{% endfor %}

<nav aria-label="Page navigation example">
    <ul class="pagination justify-content-center">
        {{ page_code }}
    </ul>
</nav>
"""
from django.utils.safestring import mark_safe


class Pagination:

    def __init__(self, request, queryset, page_size=10, page_param="page", plus=3):
        """
        :param request: 请求的对象
        :param queryset: 符号条件的数据（根据这个数据给他进行分页处理）
        :param page_size: 每页显示多少条数据
        :param page_param: 在URL中传递的获取分页的参数，例如：/etty/list/?page=12
        :param plus: 显示当前页的 前或后 几页（页码）
        """

        import copy
        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable = True
        self.query_dict = query_dict

        self.page_param = page_param
        self.total_count = queryset.count()
        page = request.GET.get(page_param, "1")
        if page.isdecimal():
            page = int(page)
        else:
            page = 1
        self.page = page

        self.page_size = page_size
        self.page_start = (page - 1) * self.page_size
        self.page_end = min(page * self.page_size, self.total_count)
        self.page_total, div = divmod(self.total_count, self.page_size)
        if div:
            self.page_total += 1
        self.queryset_list = queryset[self.page_start:self.page_end]

        # 分页的左右值
        self.plus = plus
        if self.page_total < 2 * self.plus + 1:
            self.page_min = 1
            self.page_max = self.page_total
        elif self.page < self.plus + 1:
            self.page_min = 1
            self.page_max = 2 * self.plus + 1
        elif self.page > self.page_total - self.plus - 1:
            self.page_min = self.page_total - 2 * self.plus - 1
            self.page_max = self.page_total
        else:
            self.page_min = self.page - self.plus
            self.page_max = self.page + self.plus

    def html(self):
        page_list = []

        if self.page == 1:
            self.query_dict.setlist(self.page_param, [1])
            first_coding = ("<li class='page-item'><a class='page-link disabled' href='?{}' aria-label='Previous'>"
                            "<span aria-hidden='true'>&laquo;</span></a></li>".format(self.query_dict.urlencode()))
            self.query_dict.setlist(self.page_param, [self.page - 1])
            pre_coding = "<li class='page-item'><a class='page-link disabled' href='?{}'><</a></li>".format(
                self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_param, [1])
            first_coding = ("<li class='page-item'><a class='page-link' href='?{}' aria-label='Previous'><span "
                            "aria-hidden='true'>&laquo;</span></a></li>".format(self.query_dict.urlencode()))
            self.query_dict.setlist(self.page_param, [self.page - 1])
            pre_coding = "<li class='page-item'><a class='page-link' href='?page={}'><</a></li>".format(
                self.query_dict.urlencode())
        page_list.append(first_coding)
        page_list.append(pre_coding)
        for n in range(self.page_min, self.page_max + 1):
            self.query_dict.setlist(self.page_param, [n])
            if n == self.page:
                coding = "<li class='page-item'><a class='page-link active' href='?{}'>{}</a></li>".format(
                    self.query_dict.urlencode(), n)
            else:
                coding = "<li class='page-item'><a class='page-link' href='?{}'>{}</a></li>".format(
                    self.query_dict.urlencode(), n)
            page_list.append(coding)
        if self.page == self.page_total:
            self.query_dict.setlist(self.page_param, [self.page_total])
            end_coding = ("<li class='page-item'><a class='page-link disabled' href='?{}' aria-label='Previous'>"
                          "<span aria-hidden='true'>&raquo;</span></a></li>").format(self.query_dict.urlencode())
            self.query_dict.setlist(self.page_param, [self.page + 1])
            next_coding = "<li class='page-item'><a class='page-link disabled' href='?{}'>></a></li>".format(
                self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_param, [self.page_total])
            end_coding = ("<li class='page-item'><a class='page-link' href='?{}' aria-label='Previous'>"
                          "<span aria-hidden='true'>&raquo;</span></a></li>").format(self.query_dict.urlencode())
            self.query_dict.setlist(self.page_param, [self.page + 1])
            next_coding = "<li class='page-item'><a class='page-link' href='?{}'>></a></li>".format(
                self.query_dict.urlencode())
        page_list.append(next_coding)
        page_list.append(end_coding)
        page_code = mark_safe("".join(page_list))
        return page_code
