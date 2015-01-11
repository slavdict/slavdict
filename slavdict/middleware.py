# -*- coding: utf-8 -*-
from django import http

class CookieVersionMiddleware(object):
    def process_request(self, request):
        current_version = '1'
        cookie_version = request.COOKIES.get('cookieversion')
        if cookie_version and cookie_version == current_version:
            return None
        else:
            response = http.HttpResponseRedirect(request.path)
            response.set_cookie('cookieversion', current_version,
                    max_age=60 * 60 * 24 * 30)
            for cookie in request.COOKIES:
                response.delete_cookie(cookie)
                response.delete_cookie(cookie, path=request.path)
            return response
