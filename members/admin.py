from django.contrib import admin
from .models import IEEEMember

@admin.register(IEEEMember)
class IEEEMemberAdmin(admin.ModelAdmin):
    list_display = ('ieee_number', 'full_name', 'branch', 'total_points', 'referral_count')
    search_fields = ('ieee_number', 'full_name', 'email')
    ordering = ('-total_points', '-referral_count')