from django.http.request import HttpRequest
from django.http.response import HttpResponseForbidden

def verified_email(view_func):
    def wrapper_func(request: HttpRequest, *args, **kwargs):
        if request.user.groups.all()[0].name == 'verified_email':
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden(
                    'You must verify your email to go to this page')
                    
    return wrapper_func
