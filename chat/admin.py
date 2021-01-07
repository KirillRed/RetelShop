from django.contrib import admin


from .models import Room, RoomMessage, BlackList

class RoomMessage(admin.TabularInline):
    model = RoomMessage

class RoomAdmin(admin.ModelAdmin):
    inlines = [RoomMessage]
    class Meta:
        model = Room 

class BlackListAdmin(admin.ModelAdmin):
    list_display = ['owner', 'get_blocked_clients_names', 'pk']
    list_display_links = ['owner']
    search_fields = ['owner']


admin.site.register(Room, RoomAdmin)

admin.site.register(BlackList, BlackListAdmin)