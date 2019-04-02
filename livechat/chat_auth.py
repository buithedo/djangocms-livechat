
from .models import Room

def get_chat_auth(request):
    if (request.session.get_expiry_age() > 0):
        if request.session.has_key('livechat'):
            sec_livechat = request.session['livechat']
            if (sec_livechat.get('id', False) is not False):
                if len(Room.objects.filter(id=sec_livechat.get('id'))) > 0:
                    obj_room = Room.objects.get(id=sec_livechat.get('id'))
                    if obj_room.status == 'open':
                        return obj_room
                    else:
                        return False
    return False