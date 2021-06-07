import binascii

from django import http

COOKIE_VERSION_NAME = 'cookieVersion'
COOKIE_VERSION_VALUE = '3'

class InvalidCookieError(RuntimeError):
    pass

class ValidCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.COOKIES.get(COOKIE_VERSION_NAME) != COOKIE_VERSION_VALUE:
            msg = '%s is stale or absent' + COOKIE_VERSION_NAME
            exception = InvalidCookieError(msg)
            return self.process_exception(request, exception)
        return self.get_response(request)

    def process_exception(self, request, exception):
        is_cookie_error = isinstance(exception, InvalidCookieError)
        is_base64_error = isinstance(exception, binascii.Error)

        if is_cookie_error or is_base64_error:
            if is_base64_error:
                print('[[[ binascii.Error ]]] %s' % exception)
            response = http.HttpResponseRedirect(request.path)

            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            # для http 1.1

            response['Pragma'] = 'no-cache'  # для http 1.0
            response['Expires'] = '0'  # для прокси

            response.set_cookie(COOKIE_VERSION_NAME, COOKIE_VERSION_VALUE)

            for cookie in request.COOKIES:
                if cookie in ('sessionid', 'csrftoken', COOKIE_VERSION_NAME):
                    continue
                response.delete_cookie(cookie)
                response.delete_cookie(cookie, path=request.path)
            return response
        else:
            raise exception
