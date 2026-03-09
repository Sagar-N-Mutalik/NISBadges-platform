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