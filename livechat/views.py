# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.conf import settings
import json
from ipware import get_client_ip
import time
import hashlib
from datetime import timezone, datetime, timedelta, time as datetime_time
from django.utils.dateformat import format as date_format
from .models import (
    Room,
    ChannelType,
    ChatDetail,
    BackendViewed
)

# Create your views here.
def index(request):
    return render(request, 'livechat/index.html', {})

def room(request, room_name):
    return render(request, 'livechat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })

def register_chatroom(request):
    data = {
        'error': True,
        'message': "Có lỗi trong quá trình xử lý"
    }
    if (request.method == 'POST'):
        chat_name = request.POST.get('chat_name','Guest')
        chat_email = request.POST.get('chat_email', '')
        chat_phone = request.POST.get('chat_phone', '')
        check_his = request.POST.get('check_his', False)
        chat_type = request.POST.get('chat_type', False)

        obj_chat_type = False
        if chat_type == False:
            return JsonResponse(data)
        else:
            types = ChannelType.objects.filter(id=chat_type)
            if len(types) == 0:
                return JsonResponse(data)
            else:
                obj_chat_type = ChannelType.objects.get(id=types[0].id)

        if check_his == 'true':
            check_his = True

        if check_his == 'false':
            check_his = False

        ip, is_routable = get_client_ip(request)
        current = int(time.time())
        key_hash = "%s%d%s"%(ip,current,settings.PRIVATE_SERCURITY_LIVECHAT)
        hash_md5 = hashlib.md5()
        hash_md5.update(key_hash.encode('utf-8'))
        key_hash = hash_md5.hexdigest()

        if obj_chat_type != False:
            obj_room = Room.objects.create(
                channel_type = obj_chat_type,
                key_hash = key_hash,
                full_name = chat_name,
                email = chat_email,
                phone = chat_phone,
                check_his = check_his
            )
            data['error'] = False
            data['message'] = "Tạo chat room thành công!"
            data['key_hash'] = key_hash
            data['user'] = chat_name

            if (request.session.get_expiry_age() > 0):
                if request.session.has_key('livechat'):
                    del request.session['livechat']

            request.session['livechat'] = {
                'name': obj_room.full_name,
                'id': obj_room.id,
                'key_hash': key_hash,
                'check_his': check_his,
            }
            request.session.set_expiry(float(settings.EXPIRSE_CHAT_SESSION))

            return JsonResponse(data)

    return JsonResponse(data)

# BACKEND ==============================================================================================================
def get_all_conversation(request):

    data = {
        'error': True,
        'message': "Có lỗi trong quá trình xử lý"
    }

    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse(data)

    if (request.method == 'POST'):
        start = request.POST.get('start','')
        if (start == ""):
            start = 0;
        filter = request.POST.get('filter','all')
        str_search = request.POST.get('str_search','')

        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        today_start = datetime.combine(today, datetime_time())
        today_end = datetime.combine(tomorrow, datetime_time())

        if filter == 'open':
            room_lists = Room.objects.filter(status="open", full_name__contains=str_search).order_by('-id')[start:10]
        elif filter == 'closed':
            room_lists = Room.objects.filter(status="closed", full_name__contains=str_search).order_by('-id')[start:10]
        elif filter == 'today':
            room_lists = Room.objects.filter(created__lte=today_end, created__gte=today_start, full_name__contains=str_search).order_by('-id')[start:10]
        else:
            room_lists = Room.objects.filter(full_name__contains=str_search).order_by('-id')[start:10]

        data['error'] = False
        if len(room_lists) > 0:
            arr = []
            for item in room_lists:

                item = Room.objects.get(id=item.id)

                email = item.email
                hash_email = ""
                if email != "":
                    hash_md5 = hashlib.md5()
                    hash_md5.update(email.encode('utf-8'))
                    hash_email = hash_md5.hexdigest()

                arr.append({
                    'id': item.id,
                    'channel_type': item.channel_type.name,
                    'key_hash': item.key_hash,
                    'full_name': item.full_name,
                    'email': item.email,
                    'phone': item.phone,
                    'hash_email': hash_email,
                    'created': item.created.strftime(settings.DATETIME_FORMAT),
                    'not_viewed': len(item.get_all_message_backend_not_viewed(request.user))
                })

            data['message']= u'Thành công'
            data['room_list'] = arr

    return JsonResponse(data)

def get_room_conversation(request):
    data = {
        'error': True,
        'message': "Có lỗi trong quá trình xử lý"
    }

    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse(data)

    if (request.method == 'POST'):
        id_room = request.POST.get('id_room','')
        if id_room == '':
            return JsonResponse(data)

        room_filter = Room.objects.filter(id=id_room)

        if len(room_filter) > 0:
            room_obj = Room.objects.get(id=id_room)
            data["error"] = False

            email = room_obj.email
            hash_email = ""
            if email != "":
                hash_md5 = hashlib.md5()
                hash_md5.update(email.encode('utf-8'))
                hash_email = hash_md5.hexdigest()

            data.update({
                'id': room_obj.id,
                'channel_type': room_obj.channel_type.name,
                'key_hash': room_obj.key_hash,
                'full_name': room_obj.full_name,
                'email': room_obj.email,
                'phone': room_obj.phone,
                'hash_email': hash_email,
                'created': room_obj.created.strftime(settings.DATETIME_FORMAT)
            })

            chat_details = room_obj.get_all_message()
            arr_chat = []
            for item in chat_details:
                if request.user.is_staff or request.user.is_superuser:
                    BackendViewed.objects.create(
                        user=request.user,
                        chat_detail=item
                    )
                arr_chat.append({
                    'chatter': item.chatter,
                    'is_backend': item.is_backend,
                    'message': item.message,
                    'created': item.created.strftime(settings.DATETIME_FORMAT)
                })

            data['chat'] = arr_chat
            data['message'] = u"Thành công"
            return JsonResponse(data)

    return JsonResponse(data)

def frontend_message(request):
    data = {
        'error': True,
        'message': u"Có lỗi trong quá trình xử lý"
    }

    if (request.method == 'POST'):
        id_room = request.POST.get('id_room','')
        message = request.POST.get('message','')
        if id_room == '':
            return JsonResponse(data)

        room_filter = Room.objects.filter(key_hash=id_room)
        if len(room_filter) > 0:
            room_obj = Room.objects.get(id=room_filter[0].id)
            ChatDetail.objects.create(room=room_obj,
                                      chatter=room_obj.full_name,
                                      is_backend = False,
                                      message=message)
            data["error"] = False
            data["message"] = u"Thành công!"
            return JsonResponse(data)

    return JsonResponse(data)



def backend_message(request):
    data = {
        'error': True,
        'message': u"Có lỗi trong quá trình xử lý"
    }

    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse(data)

    if (request.method == 'POST'):
        id_room = request.POST.get('id_room','')
        message = request.POST.get('message','')
        if id_room == '':
            return JsonResponse(data)

        room_filter = Room.objects.filter(key_hash=id_room)
        if len(room_filter) > 0:
            room_obj = Room.objects.get(id=room_filter[0].id)
            chat_item = ChatDetail.objects.create(room=room_obj,
                                      chatter=request.user.username,
                                      is_backend = True,
                                      message=message)
            BackendViewed.objects.create(
                user=request.user,
                chat_detail=chat_item
            )
            data["error"] = False
            data["message"] = u"Thành công!"
            return JsonResponse(data)

    return JsonResponse(data)