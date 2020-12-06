from django.http.response import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from webpush import send_user_notification
from django.http.request import HttpRequest
import json

@require_POST
@csrf_exempt
def send_push(request: HttpRequest):
    try:
        data = json.loads(request.body)


        if 'head' not in data or 'body' not in data or 'id' not in data:
            return HttpResponseBadRequest('Invalid data format')

        user_id = data['id']
        user = get_object_or_404(User, pk=user_id)
        payload = {'head': data['head'], 'body': data['body']}
        send_user_notification(user=user, payload=payload, ttl=1000)

        return JsonResponse({'message': 'Notification has been sent succesful'})
    except TypeError:
        return HttpResponseBadRequest('Oops... Something went wrong')