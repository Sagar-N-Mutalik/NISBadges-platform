from django.db import models
from core_accounts.models import CoreUser
from members.models import IEEEMember

class Event(models.Model):
    # Predefined event types
    EVENT_TYPES = (
        ('offline_tech', 'Offline Technical Event / RP Talk'),
        ('offline_non_tech', 'Offline Non-Technical Event'),
        ('online_rp', 'Online RP Talk'),
        ('industrial_visit', 'Industrial Visit / Academic Visit'),
        ('volunteering', 'Volunteering'),
    )

    # Dictionary mapping types to default points
    DEFAULT_POINTS = {
        'offline_tech': 20,
        'offline_non_tech': 10,
        'online_rp': 10,
        'industrial_visit': 30,
        'volunteering': 10,
    }

    name = models.CharField(max_length=255)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_date = models.DateField()
    
    # Optional override points
    override_points = models.IntegerField(blank=True, null=True, help_text="Leave blank to use default points") 
    
    # Linked to the core member who created it
    created_by = models.ForeignKey(CoreUser, on_delete=models.SET_NULL, null=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def final_points(self):
        """
        Logic: If override_points exists -> use override
        Else -> use default_points
        """
        if self.override_points is not None:
            return self.override_points
        return self.DEFAULT_POINTS.get(self.event_type, 0)

    def __str__(self):
        return f"{self.name} ({self.get_event_type_display()})"


class Attendance(models.Model):
    # Links the verified member to the event
    member = models.ForeignKey(IEEEMember, on_delete=models.CASCADE, related_name='attendances')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
    
    points_awarded = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Duplicate Protection: A member must not receive points twice for the same event.
        # This forces the database to reject duplicate member/event combinations.
        unique_together = ('member', 'event')

    def __str__(self):
        return f"{self.member.full_name} attended {self.event.name}"