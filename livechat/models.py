from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import models as django_auth_model
from cms.models.pluginmodel import CMSPlugin

# Create your models here.
class ChannelType(models.Model):
    name = models.CharField(default="", blank=False, null=False, max_length=1024, verbose_name=_("Channel type name"))
    des = models.TextField(verbose_name=_("Desciption"))
    users = models.ManyToManyField(django_auth_model.User,through='ChannelTypeUserRel', verbose_name=_("Users"))

    class Meta:
        verbose_name = u"kênh chat"
        verbose_name_plural = u"kênh chat"

    def __str__(self):
        return self.name


class ChannelTypeUserRel(models.Model):
    user = models.ForeignKey(django_auth_model.User, on_delete=models.CASCADE, blank=False, null=False,
                              verbose_name=_('User'))
    channel_type = models.ForeignKey(ChannelType, on_delete=models.CASCADE, blank=False, null=False,
                              verbose_name=_('Channel type'))

    class Meta:
        verbose_name = u"chuyên gia hỗ trợ cho kênh"
        verbose_name_plural = u"Các chuyên gia hỗ trợ cho kênh"


class Room(models.Model):
    channel_type = models.ForeignKey(ChannelType, on_delete=models.CASCADE, blank=False, null=False, verbose_name=_('Channel type'))
    key_hash = models.CharField(default="", max_length=1024, blank=False, null=False, unique=True,verbose_name=_("Key hash"))
    full_name = models.CharField(max_length=225, blank=False, null=False, verbose_name=_("Full name"))
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name=_("Email"))
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name=_("Phone"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Created time'))
    check_his = models.BooleanField(default=False,verbose_name=_("Check history"))
    status = models.CharField(default="open", max_length=50, blank=False, null=False, choices=(('open',_("Open")),('closed',_("Closed"))), verbose_name=_("Status"))

    def __str__(self):
        return "%s: %s"%(self.channel_type.__str__(), self.full_name)

    class Meta:
        verbose_name = u"phòng chat"
        verbose_name_plural = u"phòng chat"

    def get_all_message(self):
        message_filter = ChatDetail.objects.filter(room=self)
        arr = []
        if len(message_filter) > 0:
            for item in message_filter:
                arr.append(ChatDetail.objects.get(id=item.id))
        return arr

    def get_all_message_backend_not_viewed(self, user):
        message_filter = ChatDetail.objects.filter(room=self)
        arr = []
        if len(message_filter) > 0:
            for item in message_filter:
                chat = ChatDetail.objects.get(id=item.id)
                if len(BackendViewed.objects.filter(user=user,chat_detail=chat)) == 0:
                    arr.append(chat)
        return arr


class ChatDetail(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, blank=False, null=False,
                             verbose_name=_('Room'))
    chatter = models.CharField(default="", max_length=225, verbose_name=_("Chatter"))
    is_backend = models.BooleanField(default=False, verbose_name=_("Is Backend"))
    message = models.TextField(default="", blank=True, null=True, verbose_name=_("Message"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Created time'))

    class Meta:
        verbose_name = u"chat"
        verbose_name_plural = u"chat"

class LiveChatPopup(CMSPlugin):
    title = models.CharField(max_length=255, blank=False, verbose_name=_("Title"))

    def __str__(self):
        return self.title

class BackendViewed(models.Model):
    user = models.ForeignKey(django_auth_model.User, on_delete=models.CASCADE, blank=False, null=False,
                             verbose_name=_('User'))
    chat_detail = models.ForeignKey(ChatDetail, on_delete=models.CASCADE, blank=False, null=False,
                             verbose_name=_('Chat detail'))