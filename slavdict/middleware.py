from django import http

class InvalidCookieError(RuntimeError):
    pass

class ValidCookieMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, InvalidCookieError):
            response = http.HttpResponseRedirect(request.path)
            for cookie in request.COOKIES:
                response.delete_cookie(cookie)
                response.delete_cookie(cookie, path=request.path)
            return response
        else:
            return None
