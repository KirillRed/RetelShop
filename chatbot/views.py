import json

from django.views.generic import View
from django.http import JsonResponse
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

from chatterbot.ext.django_chatterbot import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

chatterbot = ChatBot(settings.CHATTERBOT)

chatterbot.name = 'Rexel bot'

trainer = ListTrainer(chatterbot)


@csrf_exempt
@login_required
def send_message(request):
    """
    Return a response to the statement in the posted data.
    * The JSON data should contain a 'text' attribute.
    """
    input_data = json.loads(request.body.decode('utf-8'))

    if 'text' not in input_data:
        return JsonResponse({
            'text': [
                'The attribute "text" is required.'
            ]
        }, status=400)

    print(input_data['text'])

    response = chatterbot.get_response(statement=input_data)

    response_data = response.serialize()

    return JsonResponse(response_data, status=200)

