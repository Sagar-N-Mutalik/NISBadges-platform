from django.db import models

class IEEEMember(models.Model):
    ieee_number    = models.CharField(max_length=50, unique=True, primary_key=True)
    full_name      = models.CharField(max_length=255)
    gender         = models.CharField(max_length=20, blank=True, null=True)
    birthdate      = models.DateField(blank=True, null=True)
    email          = models.EmailField(unique=True)
    mobile_number  = models.CharField(max_length=20, blank=True, null=True)
    branch         = models.CharField(max_length=100, blank=True, null=True)
    year           = models.CharField(max_length=20, blank=True, null=True)

    # Leaderboard & Tracking Fields
    total_points       = models.IntegerField(default=0)
    referral_count     = models.IntegerField(default=0)
    last_score_update  = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------
    # Snapshot original DB values the moment a row is loaded from the DB.
    # We use this in save() to compute deltas without an extra DB query.
    # ------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store the values as they exist in the DB right now
        self._original_referral_count = self.referral_count
        self._original_total_points   = self.total_points

    # ------------------------------------------------------------------
    # Integrity rule: referral_count × 50 must always be reflected in
    # total_points. Fires on EVERY save() regardless of the call site
    # (admin list-editable, admin detail form, shell, views, signals…).
    #
    # Rule 1 — Only referral_count changed:
    #   Automatically adjust total_points by (delta × 50).
    #
    # Rule 2 — Both changed (admin explicitly set total_points too):
    #   Respect the admin's explicit total_points value; just save both.
    #
    # Rule 3 — New object (no pk yet) or nothing changed:
    #   Save as-is.
    # ------------------------------------------------------------------
    def save(self, *args, **kwargs):
        if self.pk:  # only for existing records
            referral_changed = self.referral_count != self._original_referral_count
            points_changed   = self.total_points   != self._original_total_points

            if referral_changed and not points_changed:
                # Auto-compute the adjustment
                delta = self.referral_count - self._original_referral_count
                self.total_points = self._original_total_points + delta * 50
                # Never let points go negative
                if self.total_points < 0:
                    self.total_points = 0

        # Commit to DB
        super().save(*args, **kwargs)

        # Refresh snapshot so the next save() on the same instance
        # computes deltas against the just-saved values
        self._original_referral_count = self.referral_count
        self._original_total_points   = self.total_points

    def __str__(self):
        return f"{self.full_name} - {self.ieee_number}"