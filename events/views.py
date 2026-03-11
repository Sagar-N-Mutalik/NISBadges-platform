import re
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Event, Attendance
from members.models import IEEEMember
from .forms import EventForm

def get_flexible_column(df, possible_names):
    """
    Smart-matches DataFrame columns by normalizing spaces and punctuation.
    Strips '?' and collapses whitespace before comparing, and also accepts
    substring matches — so 'Are you IEEE member ?' matches 'are you ieee member'.
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

from core_accounts.decorators import allowed_roles

@login_required(login_url='/admin/login/')
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})

@login_required(login_url='/admin/login/')
def event_list(request):
    events = Event.objects.all().order_by('-event_date')
    return render(request, 'events/event_list.html', {'events': events})

@login_required(login_url='/admin/login/')
def upload_attendance(request):
    events = Event.objects.all().order_by('-event_date')

    if request.method == 'POST':
        event_id = request.POST.get('event')
        file = request.FILES.get('file')

        if not event_id or not file:
            messages.error(request, "Please select an event and upload a file.")
            return redirect('upload_attendance')

        try:
            event = Event.objects.get(id=event_id)

            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            else:
                messages.error(request, "Unsupported file format. Please upload CSV or Excel.")
                return redirect('upload_attendance')

            # ── Flexible Column Detection ───────────────────────────────────
            ieee_num_col = get_flexible_column(df, [
                'ieee number', 'membership number', 'ieee id', 'ieee no'
            ])
            ieee_member_col = get_flexible_column(df, [
                'are you ieee member', 'ieee member', 'is ieee member', 'are you an ieee member'
            ])
            checkbox_col = get_flexible_column(df, [
                'attended', 'present', 'verified', 'checkbox', 'status', 'column 11', 'unnamed: 0'
            ])

            # Only ieee_num_col is strictly required
            if not ieee_num_col:
                messages.error(request, "Could not detect an IEEE Number column in the uploaded file. "
                               "Please ensure your sheet has a column named 'IEEE Number' or 'Membership Number'.")
                return redirect('upload_attendance')

            # ── Stats tracker ───────────────────────────────────────────────
            stats = {
                'total_rows':        len(df),
                'valid_members':     0,
                'invalid_ieee':      0,
                'non_ieee':          0,
                'unchecked_skipped': 0,
                'duplicates':        0,
                'points_assigned':   0,
            }

            # ── Row-by-row processing ───────────────────────────────────────
            for index, row in df.iterrows():

                # Extract & clean IEEE number
                ieee_num = str(row.get(ieee_num_col, '')).strip()

                # Skip blank, nan, or zero-only values
                if not ieee_num or ieee_num.lower() == 'nan' or ieee_num == '0':
                    continue

                # ── Checkbox / presence verification ───────────────────────
                # If a checkbox column exists, skip anyone whose box is unchecked.
                # Pandas reads native checkboxes as boolean True/False.
                if checkbox_col:
                    val = str(row.get(checkbox_col, '')).strip().lower()
                    if val in ['false', '0', '', 'nan', 'no']:
                        stats['unchecked_skipped'] += 1
                        continue

                # If the IEEE-member confirmation column exists, honour a 'no' answer
                if ieee_member_col:
                    is_ieee = str(row.get(ieee_member_col, '')).strip().lower()
                    if is_ieee in ['no', 'n', 'false']:
                        stats['non_ieee'] += 1
                        continue
                # If the column is absent, assume everyone in the sheet wants points — proceed

                try:
                    # Verify against the source-of-truth member database
                    member = IEEEMember.objects.get(ieee_number=ieee_num)

                    # Duplicate check — same member + same event
                    if Attendance.objects.filter(member=member, event=event).exists():
                        stats['duplicates'] += 1
                    else:
                        points_to_award = event.final_points

                        Attendance.objects.create(
                            member=member,
                            event=event,
                            points_awarded=points_to_award
                        )

                        # Accumulate points on the member profile
                        member.total_points += points_to_award
                        member.save()

                        stats['valid_members']  += 1
                        stats['points_assigned'] += 1

                except IEEEMember.DoesNotExist:
                    stats['invalid_ieee'] += 1

            # ── Summary report ──────────────────────────────────────────────
            report = (
                f"Processing Complete. Total Rows: {stats['total_rows']} | "
                f"Valid Members: {stats['valid_members']} | "
                f"Invalid IEEE Numbers: {stats['invalid_ieee']} | "
                f"Non-IEEE Skipped: {stats['non_ieee']} | "
                f"Unchecked/Absent Skipped: {stats['unchecked_skipped']} | "
                f"Duplicates Skipped: {stats['duplicates']} | "
                f"Points Assigned: {stats['points_assigned']}"
            )
            messages.success(request, report)

        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")

        return redirect('upload_attendance')

    return render(request, 'events/upload_attendance.html', {'events': events})


@login_required(login_url='/admin/login/')
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    messages.success(request, 'Event deleted successfully.')
    return redirect('event_list')