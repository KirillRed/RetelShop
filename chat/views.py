import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

@login_required
@csrf_exempt
def room(request: HttpRequest):
    room_name = request.GET.get('room_name', '')
    if room_name == '':
        return HttpResponseBadRequest('Oops... Something went wrong')
    data = json.loads(request.body)
    message = data['message']
    return JsonResponse({'room_name': room_name, 'message': message})