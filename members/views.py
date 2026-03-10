import pandas as pd
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import IEEEMember

def clean_name(name):
    """
    Cleans the name field based on predefined rules.
    """
    if pd.isna(name):
        return ""
    name = str(name)
    
    # Remove titles (Mr., Ms., Dr., etc.)
    name = re.sub(r'^(Mr\.|Ms\.|Mrs\.|Dr\.)\s*', '', name, flags=re.IGNORECASE)
    
    # Remove text in brackets e.g., "Sneha Sharma (Volunteer)" -> "Sneha Sharma "
    name = re.sub(r'\(.*?\)', '', name)
    
    # Remove text after "-" e.g., "Arjun Patel - IEEE Member" -> "Arjun Patel "
    name = name.split('-')[0]
    
    # Trim spaces
    return name.strip()

from core_accounts.decorators import main_admin_required
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def dashboard_home(request):
    return render(request, 'members/dashboard_home.html')

@main_admin_required
def upload_members(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        
        if not file:
            messages.error(request, 'Please select a file to upload.')
            return redirect('upload_members')
            
        try:
            # Detect file type and read using pandas
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                df = pd.read_excel(file)
            else:
                messages.error(request, 'Unsupported file format. Please upload CSV or Excel.')
                return redirect('upload_members')

            success_count = 0
            duplicate_count = 0

            # Process row by row
            for index, row in df.iterrows():
                # Flexible column mapping could be added here later, for now we assume standard columns
                ieee_num = str(row.get('IEEE Number', '')).strip()
                
                # Skip if no IEEE number
                if not ieee_num or ieee_num.lower() == 'nan':
                    continue
                    
                raw_name = row.get('Full Name', '')
                cleaned_name = clean_name(raw_name)
                
                email = str(row.get('Email', '')).strip()
                if not email or email.lower() == 'nan':
                    email = f"{ieee_num}@placeholder.com" # Ensure unique email constraint doesn't fail
                
                # Insert or skip duplicate
                # get_or_create checks if the ieee_number already exists. 
                # If it does, created = False and it skips overriding points.
                member, created = IEEEMember.objects.get_or_create(
                    ieee_number=ieee_num,
                    defaults={
                        'full_name': cleaned_name,
                        'gender': row.get('Gender', None) if pd.notna(row.get('Gender')) else '',
                        'email': email,
                        'mobile_number': str(row.get('Mobile', '')) if pd.notna(row.get('Mobile')) else '',
                        'branch': str(row.get('Branch', '')) if pd.notna(row.get('Branch')) else '',
                        'year': str(row.get('Year', '')) if pd.notna(row.get('Year')) else '',
                    }
                )
                
                if created:
                    success_count += 1
                else:
                    duplicate_count += 1

            messages.success(request, f'Successfully imported {success_count} new members. Skipped {duplicate_count} duplicates.')
            
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            
        return redirect('upload_members')

    return render(request, 'members/upload.html')