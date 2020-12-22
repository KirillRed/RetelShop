from django.http.request import HttpRequest
from django.http.response import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps

def verified_email(view_func):
    @wraps(view_func)
    def wrapper_func(request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('registration:login')
        print(request.user)
        if request.user.groups.all()[0].name == 'verified_email':
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden(
                    'You must verify your email to go to this page')

    return wrapper_func
