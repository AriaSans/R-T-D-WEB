from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class CheckCookie(MiddlewareMixin):
    def process_request(self, request):
        if request.path_info == '/user/login/':
            return

        if request.path_info == '/user/register/':
            return

        info_dict = request.session.get('info')
        print(info_dict)
        if not info_dict:
            return redirect('/user/login/')
        return

    def process_response(self, request, response):
        return response
