from django.http.response import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponse

class MyHttpResponseNotFound(HttpResponse, BaseException):
    status_code = 404