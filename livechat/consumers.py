# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import datetime
from django.conf import settings
import json
from . import chat_auth
from .models import Room, ChatDetail

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        print("\nUser: %s"%self.user)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        user = str(self.scope['user'])
        #room_key = self.scope['url_route']['kwargs']['room_name']
        #room_obj = False
        #room_filter = Room.objects.filter(key_hash=room_key)
        # if len(room_filter) > 0:
        #     room_obj = Room.objects.get(key_hash=room_key)
        #
        # if user == "AnonymousUser":
        #     if room_obj != False:
        #         user = room_obj.full_name
        #
        # if room_obj != False:
        #     ChatDetail.objects.create(room=room_obj,
        #                               chatter=user,
        #                               is_backend = bool(user == "AnonymousUser"),
        #                               message=message)

        now_time = datetime.datetime.now().strftime(settings.DATETIME_FORMAT)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user,
                'now_time': now_time
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        now_time = event['now_time']
        user = event['user']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user': user,
            'now_time': now_time,
        }))