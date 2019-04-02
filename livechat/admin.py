from django.contrib import admin
from .models import (
    ChannelType,
    Room,
    ChatDetail,
    ChannelTypeUserRel
)

class ChannelTypeUserRelInline(admin.TabularInline):
    model = ChannelTypeUserRel
    extra = 1

# Register your models here.
@admin.register(ChannelType)
class ChannelTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'des']
    search_fields = ['name',]
    ordering = ['-id', ]
    inlines = (ChannelTypeUserRelInline,)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'channel_type', 'key_hash', 'created']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ('key_hash', 'created')
    list_filter = ['channel_type', ]
    ordering = ['-id', ]

    # remove button add level
    def has_add_permission(self, request):
        return False

    # remove button delete level
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(ChatDetail)
class ChatDetailAdmin(admin.ModelAdmin):
    list_display = ['chatter', 'message', 'room', 'is_backend', 'created']
    search_fields = ['chatter', 'message']
    readonly_fields = ('chatter', 'message', 'room', 'is_backend', 'created')
    ordering = ['-id', ]

    change_list_template = "livechat/admin/chat_backend.html"

    # remove button add level
    def has_add_permission(self, request):
        return False

    # remove button delete level
    def has_delete_permission(self, request, obj=None):
        return False