from django.contrib import admin
from .models import Event, Attendance

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'event_date', 'final_points', 'created_by')
    list_filter = ('event_type', 'event_date')
    search_fields = ('name',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('member', 'event', 'points_awarded', 'timestamp')
    list_filter = ('event',)
    search_fields = ('member__ieee_number', 'member__full_name', 'event__name')