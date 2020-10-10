from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin, ReadOnlyTabularInlineModelAdmin
from .models import Chat, Message


class MessageInlineAdmin(ReadOnlyTabularInlineModelAdmin):
    model = Message


admin.site.register(Chat, ReadOnlyModelAdmin)
admin.site.register(Message, ReadOnlyModelAdmin)


