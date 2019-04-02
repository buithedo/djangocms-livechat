from scdi_bvtl.config import MODULE_NAME
from taggit.models import Tag
from django.conf import settings
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _
from .models import (
    Room,
    LiveChatPopup,
    ChannelType
)
from . import chat_auth

@plugin_pool.register_plugin
class LiveChatPopupPlugin(CMSPluginBase):
    module = MODULE_NAME
    model = LiveChatPopup
    name = _("Livechat popup plugin")
    render_template = "livechat/frontend/livechat_client_popup.html"
    cache = False
    allow_children = False

    def render(self, context, instance, placeholder):
        request = context.get('request')
        obj_room = chat_auth.get_chat_auth(request)
        instance.obj_room = obj_room
        instance.obj_channels = ChannelType.objects.all()

        context = super(LiveChatPopupPlugin, self).render(context, instance, placeholder)
        return context