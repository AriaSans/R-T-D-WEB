from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class CheckCookie(MiddlewareMixin):
    def process_request(self, request):
        if request.path_info == '/user/login/' or request.path_info == '/user/register/':
            return

        info_dict = request.session.get('info')
        print(info_dict)
        if not info_dict:
            return redirect('/user/login/')
        elif request.get_full_path() == '/':
            return redirect('/yolo/main/')
        return

    def process_response(self, request, response):
        return response
