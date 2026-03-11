import re
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from members.models import IEEEMember





def get_flexible_column(df, possible_names):
    """
    Smart-matches DataFrame columns by normalizing spaces and punctuation.
    Strips '?' and collapses whitespace before comparing. Accepts substring
    matches and guards against cross-contamination between number/id columns.
    """
    for col in df.columns:
        normalized_col = re.sub(r'\s+', ' ', str(col).lower().replace('?', '')).strip()
        for name in possible_names:
            normalized_name = re.sub(r'\s+', ' ', name.lower().replace('?', '')).strip()
            if normalized_col == normalized_name or normalized_name in normalized_col:
                if 'number' in normalized_col and 'number' not in normalized_name:
                    continue
                if 'id' in normalized_col and 'id' not in normalized_name:
                    continue
                return col
    return None

from core_accounts.decorators import allowed_roles, co_admin_or_higher_required
from django.contrib.auth.decorators import login_required

@login_required(login_url='/admin/login/')
@allowed_roles(allowed_roles=['main_admin', 'co_admin'])
def update_manual_referral(request, ieee_number):
    """
    POST-only view. Sets a member's referral count to the submitted value and
    adjusts total_points by the difference:
      difference = new_count - old_count
      points_adjustment = difference * 50   (positive = add, negative = subtract)
    """
    if request.method == 'POST':
        member = get_object_or_404(IEEEMember, ieee_number=ieee_number)
        try:
            new_count = int(request.POST.get('new_count', 0))
            if new_count < 0:
                new_count = 0
        except (ValueError, TypeError):
            new_count = 0

        difference = new_count - member.referral_count
        points_adjustment = difference * 50

        member.total_points += points_adjustment
        member.referral_count = new_count
        member.save()

        if points_adjustment > 0:
            adj_str = f"+{points_adjustment}"
        elif points_adjustment < 0:
            adj_str = str(points_adjustment)
        else:
            adj_str = "0 (no change)"

        messages.success(
            request,
            f"Updated referrals for {member.full_name} → {new_count} referral"
            f"{'s' if new_count != 1 else ''}. Points adjusted by {adj_str}."
        )
    return redirect('view_leaderboard')


def view_leaderboard(request):
    """
    Ranks members based on points.
    Tie-Breaker 1: Higher referral count wins.
    Tie-Breaker 2: Whoever reached the score first (last_score_update ASC) ranks higher.

    Absolute ranks are assigned in Python before any search filter is applied,
    so a searched subset always shows the correct global position.
    """
    all_members = IEEEMember.objects.all().order_by(
        '-total_points',
        '-referral_count',
        'last_score_update'
    )

    # Assign absolute rank to each member object in memory
    ranked_members = []
    for index, member in enumerate(all_members, start=1):
        member.absolute_rank = index
        ranked_members.append(member)

    # Search — filters the pre-ranked list so ranks are preserved
    search_query = request.GET.get('q', '').strip().lower()
    if search_query:
        ranked_members = [
            m for m in ranked_members
            if search_query in m.full_name.lower()
            or search_query in m.ieee_number.lower()
        ]

    return render(request, 'leaderboard/leaderboard.html', {
        'leaderboard': ranked_members,
        'search_query': search_query,
    })


from django.contrib.auth.decorators import login_required
from .models import BadgeAward

def badge_eligibility(request):
    """
    Dashboard automatically displays top members for upcoming badge distribution.
    """
    leaderboard_data = IEEEMember.objects.all().order_by(
        '-total_points', 
        '-referral_count', 
        'last_score_update'
    )
    
    # Slice the querysets for the specific tiers
    context = {
        'prime_eligible': leaderboard_data[:5],   # Top 5
        'elite_eligible': leaderboard_data[:10],  # Top 10
        'pro_eligible': leaderboard_data[:20],    # Top 20
    }
    
    return render(request, 'leaderboard/badge_eligibility.html', context)

@login_required(login_url='/admin/login/')
@allowed_roles(allowed_roles=['main_admin', 'co_admin'])
def assign_badges(request):
    if request.method == 'POST':
        event_name = request.POST.get('event_name')
        badge_type = request.POST.get('badge_type')
        
        if not event_name or not badge_type:
            messages.error(request, "Please provide an event name and select a badge type.")
            return redirect('assign_badges')
            
        leaderboard = IEEEMember.objects.all().order_by(
            '-total_points', 
            '-referral_count', 
            'last_score_update'
        )
        
        if badge_type == 'Pro':
            eligible_members = leaderboard[:20]
        elif badge_type == 'Elite':
            eligible_members = leaderboard[:10]
        elif badge_type == 'Prime':
            eligible_members = leaderboard[:5]
        else:
            messages.error(request, "Invalid badge type selected.")
            return redirect('assign_badges')
            
        awarded_count = 0
        for member in eligible_members:
            _, created = BadgeAward.objects.get_or_create(
                member=member,
                badge_type=badge_type,
                event_name=event_name
            )
            if created:
                awarded_count += 1
                
        messages.success(request, f"Successfully awarded {awarded_count} '{badge_type}' badges for '{event_name}'.")
        return redirect('assign_badges')
        
    return render(request, 'leaderboard/assign_badges.html')

import csv
from django.http import HttpResponse

@login_required(login_url='/admin/login/')
@allowed_roles(allowed_roles=['main_admin', 'co_admin'])
def export_badges_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="nisbadges_winners.csv"'

    writer = csv.writer(response)
    writer.writerow(['Member Name', 'IEEE Number', 'Branch', 'Badge Type', 'Event Name', 'Award Date'])

    badge_awards = BadgeAward.objects.select_related('member').all()
    
    for award in badge_awards:
        writer.writerow([
            award.member.full_name,
            award.member.ieee_number,
            award.member.branch,
            award.badge_type,
            award.event_name,
            award.award_date
        ])

    return response