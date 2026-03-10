import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from members.models import IEEEMember

def get_flexible_column(df, possible_names):
    """Matches dataframe columns against a list of possible variations."""
    for col in df.columns:
        if str(col).strip().lower() in possible_names:
            return col
    return None

from core_accounts.decorators import allowed_roles, co_admin_or_higher_required
from django.contrib.auth.decorators import login_required

@login_required(login_url='/admin/login/')
@allowed_roles(allowed_roles=['main_admin', 'co_admin'])
def process_referrals(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        
        if not file:
            messages.error(request, "Please upload a file.")
            return redirect('process_referrals')
            
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            else:
                messages.error(request, "Unsupported file format.")
                return redirect('process_referrals')

            # Find the referral column flexibly
            referral_col = get_flexible_column(df, [
                "referral ieee", "referral ieee number", "referred by", "referred by (ieee number)"
            ])

            if not referral_col:
                messages.error(request, "Could not detect a 'Referral IEEE' column in the uploaded file.")
                return redirect('process_referrals')

            stats = {
                'total_rows': len(df),
                'successful_referrals': 0,
                'invalid_referrals': 0,
            }

            for index, row in df.iterrows():
                referrer_ieee = str(row.get(referral_col, '')).strip()
                
                # Skip empty referral cells
                if not referrer_ieee or referrer_ieee.lower() == 'nan':
                    continue
                
                try:
                    # Look up the member who made the referral
                    referrer = IEEEMember.objects.get(ieee_number=referrer_ieee)
                    
                    # Award 50 points and increment referral count
                    referrer.total_points += 50
                    referrer.referral_count += 1
                    referrer.save()
                    
                    stats['successful_referrals'] += 1
                    
                except IEEEMember.DoesNotExist:
                    # The referral number provided doesn't belong to a verified member
                    stats['invalid_referrals'] += 1

            report = (f"Referral Processing Complete. Total Rows: {stats['total_rows']} | "
                      f"Successful Referrals (+50 pts each): {stats['successful_referrals']} | "
                      f"Invalid/Unverified Referrals Skipped: {stats['invalid_referrals']}")
            
            messages.success(request, report)
            
        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")
            
        return redirect('process_referrals')

    return render(request, 'leaderboard/process_referrals.html')
# ... (keep your existing process_referrals function at the top) ...

def view_leaderboard(request):
    """
    Ranks members based on points.
    Tie-Breaker 1: Higher referral count wins.
    Tie-Breaker 2: Whoever reached the score first (last_score_update ASC) ranks higher.
    """
    leaderboard_data = IEEEMember.objects.all().order_by(
        '-total_points', 
        '-referral_count', 
        'last_score_update'
    )
    
    return render(request, 'leaderboard/leaderboard.html', {'leaderboard': leaderboard_data})


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

@co_admin_or_higher_required
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