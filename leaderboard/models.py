from django.db import models
from members.models import IEEEMember

class BadgeAward(models.Model):
    # Tier Badge Definitions
    BADGE_CHOICES = (
        ('Pro', 'Tier 3 - Pro Badge'),
        ('Elite', 'Tier 2 - Elite Badge'),
        ('Prime', 'Tier 1 - Prime Badge'),
    )
    
    member = models.ForeignKey(IEEEMember, on_delete=models.CASCADE, related_name='badges')
    badge_type = models.CharField(max_length=20, choices=BADGE_CHOICES)
    event_name = models.CharField(max_length=100, help_text="e.g., Inspiro, Illume, Rubix")
    award_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.full_name} - {self.badge_type} ({self.event_name})"