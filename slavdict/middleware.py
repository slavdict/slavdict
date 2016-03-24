# -*- coding: utf-8 -*-
from django import http

class InvalidCookieError(RuntimeError):
    pass

class ValidCookieMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, InvalidCookieError):
            response = http.HttpResponseRedirect(request.path)
            for cookie in request.COOKIES:
                response.delete_cookie(cookie)
                response.delete_cookie(cookie, path=request.path)
            return response
        else:
            return None
