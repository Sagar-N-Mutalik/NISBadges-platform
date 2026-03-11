from django.contrib import admin
from .models import IEEEMember


@admin.register(IEEEMember)
class IEEEMemberAdmin(admin.ModelAdmin):
    list_display       = ('ieee_number', 'full_name', 'total_points', 'referral_count', 'branch')
    list_display_links = ('ieee_number', 'full_name')   # clicking these opens the detail form
    list_editable      = ('total_points', 'referral_count')  # inline-editable in the list view
    search_fields      = ('ieee_number', 'full_name', 'email')
    list_filter        = ('branch',)
    ordering           = ('-total_points', '-referral_count')
    actions            = ['reset_referrals', 'reset_total_points']

    class Media:
        """
        Django's official per-ModelAdmin static file mechanism.
        These are injected into the admin <head> automatically —
        much more reliable than JAZZMIN's custom_js/custom_css hooks.
        """
        css = {'all': ('admin/css/admin_custom.css',)}
        js  = ('admin/js/admin_custom.js',)

    # ------------------------------------------------------------------
    # Action 1: Undo referral points only
    # ------------------------------------------------------------------
    @admin.action(description='Undo/Reset all referral points for selected members')
    def reset_referrals(self, request, queryset):
        updated_count = 0
        for member in queryset:
            if member.referral_count > 0:
                points_to_remove = member.referral_count * 50
                member.total_points -= points_to_remove
                member.referral_count = 0
                member.save()
                updated_count += 1
        self.message_user(request, f"Successfully reset referrals for {updated_count} members.")

    # ------------------------------------------------------------------
    # Action 2: Wipe total_points completely (semester reset / corruption fix)
    # Uses queryset.update() — one SQL UPDATE, no per-row Python loop.
    # ------------------------------------------------------------------
    @admin.action(description='⚠️ DANGER: Reset Total Points to 0 for selected members')
    def reset_total_points(self, request, queryset):
        updated = queryset.update(total_points=0)
        self.message_user(
            request,
            f"Reset total_points to 0 for {updated} member{'s' if updated != 1 else ''}.",
            level='WARNING',
        )