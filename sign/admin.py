from django.contrib import admin
from sign.models import Event, Guset


class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'address', 'start_time']
    search_fields = ['name', 'status']
    list_filter = ['status']


class GuestAdmin(admin.ModelAdmin):
    list_display = ['realname', 'phone', 'email', 'sign', 'create_time', 'event']
    search_fields = ['phone', 'realname']
    list_filter = ['sign']


admin.site.register(Event, EventAdmin)
admin.site.register(Guset, GuestAdmin)
