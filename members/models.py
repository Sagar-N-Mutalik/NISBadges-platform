from django.db import models

class IEEEMember(models.Model):
    ieee_number = models.CharField(max_length=50, unique=True, primary_key=True) # Unique identifier
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=20, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    year = models.CharField(max_length=20, blank=True, null=True)
    
    # Leaderboard & Tracking Fields
    total_points = models.IntegerField(default=0)
    referral_count = models.IntegerField(default=0)
    last_score_update = models.DateTimeField(auto_now=True) # Auto-updates timestamp on save

    def __str__(self):
        return f"{self.full_name} - {self.ieee_number}"