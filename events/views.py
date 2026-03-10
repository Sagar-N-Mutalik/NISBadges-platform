import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Event, Attendance
from members.models import IEEEMember
from .forms import EventForm

def get_flexible_column(df, possible_names):
    """Matches dataframe columns against a list of possible variations."""
    for col in df.columns:
        if str(col).strip().lower() in possible_names:
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
                messages.error(request, "Unsupported file format.")
                return redirect('upload_attendance')

            # Flexible Column Detection
            ieee_member_col = get_flexible_column(df, ["are you ieee member?", "ieee member", "is ieee member"])
            ieee_num_col = get_flexible_column(df, ["membership number", "ieee number", "membership_number"])

            if not ieee_member_col or not ieee_num_col:
                messages.error(request, "Could not detect required columns (IEEE Member status or Membership Number).")
                return redirect('upload_attendance')

            # Tracking statistics for the final report
            stats = {
                'total_rows': len(df),
                'valid_members': 0,
                'invalid_ieee': 0,
                'non_ieee': 0,
                'duplicates': 0,
                'points_assigned': 0
            }

            for index, row in df.iterrows():
                is_ieee = str(row.get(ieee_member_col, '')).strip().lower()
                
                # Check if they claimed to be an IEEE member
                if is_ieee not in ['yes', 'y', 'true']:
                    stats['non_ieee'] += 1
                    continue
                
                ieee_num = str(row.get(ieee_num_col, '')).strip()
                
                try:
                    # Verify against the source of truth database
                    member = IEEEMember.objects.get(ieee_number=ieee_num)
                    
                    # Check for duplicates using Django's filter
                    if Attendance.objects.filter(member=member, event=event).exists():
                        stats['duplicates'] += 1
                    else:
                        # Award points and create attendance record
                        points_to_award = event.final_points
                        
                        Attendance.objects.create(
                            member=member,
                            event=event,
                            points_awarded=points_to_award
                        )
                        
                        # Accumulate points on the member profile
                        member.total_points += points_to_award
                        member.save()
                        
                        stats['valid_members'] += 1
                        stats['points_assigned'] += 1
                        
                except IEEEMember.DoesNotExist:
                    stats['invalid_ieee'] += 1

            # Generate the Error Report summary
            report = (f"Processing Complete. Total Rows: {stats['total_rows']} | "
                      f"Valid Members: {stats['valid_members']} | "
                      f"Invalid IEEE Numbers: {stats['invalid_ieee']} | "
                      f"Non-IEEE Participants: {stats['non_ieee']} | "
                      f"Duplicates Skipped: {stats['duplicates']} | "
                      f"Points Assigned: {stats['points_assigned']}")
            
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