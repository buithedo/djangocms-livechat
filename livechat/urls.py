from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<room_name>[^/]+)/$', views.room, name='room'),

    # API
    url(r'^api/register_chatroom$', views.register_chatroom, name="register_chatroom"),
    url(r'^api/get_all_conversation$', views.get_all_conversation, name="get_all_conversation"),
    url(r'^api/get_room_conversation$', views.get_room_conversation, name="get_room_conversation"),
    url(r'^api/frontend_message$', views.frontend_message, name="frontend_message"),
    url(r'^api/backend_message$', views.backend_message, name="backend_message")
]