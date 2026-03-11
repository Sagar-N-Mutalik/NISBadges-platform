import re
import pandas as pd
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


def get_flexible_column(df, possible_names):
    """
    Smart-matches DataFrame columns by normalizing spaces and punctuation.
    Strips '?' and collapses whitespace before comparing, and also accepts
    substring matches — so 'Your IEEE Membership Number ' matches 'membership number'.
    Guards against cross-contamination between IEEE-number and IEEE-member columns.
    """
    for col in df.columns:
        normalized_col = re.sub(r'\s+', ' ', str(col).lower().replace('?', '')).strip()
        for name in possible_names:
            normalized_name = re.sub(r'\s+', ' ', name.lower().replace('?', '')).strip()
            if normalized_col == normalized_name or normalized_name in normalized_col:
                # Guard: don't let 'ieee member' match 'ieee membership number'
                if 'number' in normalized_col and 'number' not in normalized_name:
                    continue
                if 'id' in normalized_col and 'id' not in normalized_name:
                    continue
                return col
    return None


from core_accounts.decorators import main_admin_required, allowed_roles
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def dashboard_home(request):
    return render(request, 'members/dashboard_home.html')


@login_required(login_url='login')
@allowed_roles(allowed_roles=['main_admin', 'co_admin'])
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

            # ── Flexible column detection ───────────────────────────────────
            email_col  = get_flexible_column(df, ['email', 'mail'])
            ieee_col   = get_flexible_column(df, ['ieee number', 'membership number', 'ieee id', 'ieee no'])
            fname_col  = get_flexible_column(df, ['first name', 'full name', 'name'])
            lname_col  = get_flexible_column(df, ['last name', 'surname'])
            phone_col  = get_flexible_column(df, ['mobile', 'phone', 'contact'])
            gender_col = get_flexible_column(df, ['gender', 'sex'])
            branch_col = get_flexible_column(df, ['branch', 'department', 'dept'])
            year_col   = get_flexible_column(df, ['year', 'year of study', 'sem', 'semester'])

            # Warn if critical columns are completely missing
            if not email_col and not ieee_col:
                messages.error(request, 'Could not detect required columns (Email or IEEE Number). Please check your file headers.')
                return redirect('upload_members')

            success_count = 0
            duplicate_count = 0
            pending_count = 0

            # ── Row-by-row processing ───────────────────────────────────────
            for index, row in df.iterrows():

                # ── Email ───────────────────────────────────────────────────
                email = str(row.get(email_col, '') if email_col else '').strip()
                if not email or email.lower() == 'nan':
                    email = f"row{index}@placeholder.com"

                # ── IEEE Number ─────────────────────────────────────────────
                ieee_num = str(row.get(ieee_col, '') if ieee_col else '').strip()
                # Pandas reads integer columns with NaN gaps as float64,
                # producing strings like '101659510.0' — strip the decimal.
                if ieee_num.endswith('.0'):
                    ieee_num = ieee_num[:-2]
                if not ieee_num or ieee_num.lower() == 'nan':
                    # Don't skip — generate a pending placeholder from email
                    ieee_num = f"PENDING-{email}"
                    pending_count += 1

                # ── Name ────────────────────────────────────────────────────
                if fname_col and lname_col:
                    raw_name = f"{row.get(fname_col, '')} {row.get(lname_col, '')}".strip()
                elif fname_col:
                    raw_name = str(row.get(fname_col, '')).strip()
                else:
                    raw_name = ''
                cleaned_name = clean_name(raw_name)

                # ── Helper for optional fields ──────────────────────────────
                def safe_get(col):
                    if not col:
                        return ''
                    val = row.get(col)
                    return str(val) if pd.notna(val) else ''

                # ── Insert or skip duplicate ────────────────────────────────
                member, created = IEEEMember.objects.get_or_create(
                    ieee_number=ieee_num,
                    defaults={
                        'full_name': cleaned_name,
                        'gender':        safe_get(gender_col),
                        'email':         email,
                        'mobile_number': safe_get(phone_col),
                        'branch':        safe_get(branch_col),
                        'year':          safe_get(year_col),
                    }
                )

                if created:
                    success_count += 1
                else:
                    duplicate_count += 1

            # ── Summary message ─────────────────────────────────────────────
            summary = (
                f"Import complete — {success_count} new members added"
                + (f", {pending_count} without IEEE numbers (marked PENDING)" if pending_count else "")
                + (f", {duplicate_count} duplicates skipped." if duplicate_count else ".")
            )
            messages.success(request, summary)

        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')

        return redirect('upload_members')

    return render(request, 'members/upload.html')