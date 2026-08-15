import json
import os
import pusher
import resend
from datetime import date, timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect

pusher_client = pusher.Pusher(
    app_id=os.environ.get('PUSHER_APP_ID', '2184711'),
    key=os.environ.get('PUSHER_KEY', '308cbea8f43adedfd722'),
    secret=os.environ.get('PUSHER_SECRET', '630467b420710c74b362'),
    cluster=os.environ.get('PUSHER_CLUSTER', 'ap1'),
    ssl=True
)


from datetime import date, timedelta, datetime

def safe_format_date(val, fmt='%d %b %Y'):
    """Safely format a date/datetime object or date string."""
    if not val:
        return ''
    if hasattr(val, 'strftime'):
        return val.strftime(fmt)
    if isinstance(val, str):
        try:
            dt = datetime.strptime(val.split('T')[0], '%Y-%m-%d')
            return dt.strftime(fmt)
        except Exception:
            return val
    return str(val)


def send_verification_email(request, user):
    """Generate token and send email verification via Resend or Django mailer."""
    profile, _ = UserProfile.objects.get_or_create(user=user)
    token = profile.generate_verification_token()

    verify_path = reverse('verify_email', kwargs={'token': token})
    if request:
        verify_url = request.build_absolute_uri(verify_path)
    else:
        verify_url = f"http://127.0.0.1:8000{verify_path}"

    display_name = profile.full_name or user.username
    subject = "Verify your email address for Team Vatana Jira"

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 580px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; background-color: #ffffff;">
        <div style="background-color: #0052cc; color: #ffffff; padding: 22px 24px;">
            <h2 style="margin: 0; font-size: 20px; font-weight: 700;">Team Vatana Jira</h2>
        </div>
        <div style="padding: 28px 24px; color: #172b4d; line-height: 1.6;">
            <p style="font-size: 15px; margin-top: 0;">Hi <strong>{display_name}</strong>,</p>
            <p style="font-size: 14px;">Welcome to <strong>Team Vatana Jira</strong>! Please verify your email address to complete your registration and start receiving ticket notifications.</p>
            
            <div style="text-align: center; margin: 26px 0;">
                <a href="{verify_url}" style="background-color: #0052cc; color: #ffffff; text-decoration: none; padding: 12px 28px; font-weight: bold; font-size: 14px; border-radius: 4px; display: inline-block;" target="_blank">Verify Email Address</a>
            </div>

            <p style="font-size: 13px; color: #6b778c; margin-bottom: 6px;">If the button above does not work, copy and paste this link into your browser:</p>
            <div style="background: #f4f5f7; padding: 10px; border-radius: 4px; font-size: 12px; color: #0052cc; word-break: break-all; border: 1px solid #e0e0e0;">{verify_url}</div>
        </div>
        <div style="background-color: #fafbfc; border-top: 1px solid #ebecf0; padding: 16px 24px; text-align: center; font-size: 12px; color: #6b778c;">
            &copy; 2026 Team Vatana Jira. All rights reserved.
        </div>
    </div>
    """

    resend_key = os.environ.get('RESEND_API_KEY', '')
    sent_resend = False
    if resend_key and user.email:
        try:
            resend.api_key = resend_key
            sender_email = os.environ.get('RESEND_FROM_EMAIL', 'onboarding@resend.dev')
            resend.Emails.send({
                "from": sender_email,
                "to": user.email,
                "subject": subject,
                "html": html_content
            })
            sent_resend = True
        except Exception as r_err:
            print(f"[Resend] Error sending verification email: {r_err}")

    if not sent_resend and user.email:
        try:
            from django.core.mail import send_mail
            send_mail(
                subject=subject,
                message=f"Hi {display_name},\n\nPlease verify your email address:\n{verify_url}\n\nTeam Vatana Jira",
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'Team Vatana Jira <noreply@vatana-jira.com>'),
                recipient_list=[user.email],
                html_message=html_content,
                fail_silently=True
            )
        except Exception as d_err:
            print(f"[Django Mail] Error: {d_err}")

    print(f"\n[EMAIL VERIFICATION LINK] User '{user.email}' -> {verify_url}\n")
    return verify_url


def send_assignment_email(ticket, assigned_user):
    """Send email notification via Resend when a ticket is assigned to a user."""
    if not assigned_user or not assigned_user.email:
        return

    profile = getattr(assigned_user, 'profile', None)
    if profile and not profile.is_email_verified:
        print(f"[Notification] Skipping assignment email for {assigned_user.email} (Email not verified yet).")
        return

    resend_key = os.environ.get('RESEND_API_KEY', '')
    if not resend_key:
        return

    resend.api_key = resend_key
    sender_email = os.environ.get('RESEND_FROM_EMAIL', 'onboarding@resend.dev')

    subject = f"[Ticket Assigned] {ticket.ticket_code}: {ticket.subject}"
    assigned_by = ticket.user.username if ticket.user else "System"

    start_date_str = safe_format_date(ticket.start_date, '%d %b %Y') or 'N/A'
    due_date_str = safe_format_date(ticket.due_date, '%d %b %Y') or 'N/A'
    prio_name = ticket.priority.priority_name if ticket.priority else 'Medium'
    status_name = ticket.status.status_name if ticket.status else 'Open'


    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; background-color: #ffffff;">
        <div style="background-color: #0052cc; color: #ffffff; padding: 20px 24px;">
            <h2 style="margin: 0; font-size: 20px; font-weight: 700;">🎫 Ticket Assigned to You</h2>
        </div>
        <div style="padding: 24px; color: #172b4d;">
            <p style="font-size: 15px; margin-top: 0;">Hi <strong>{assigned_user.username}</strong>,</p>
            <p style="font-size: 14px;">You have been assigned to ticket <strong>{ticket.ticket_code}</strong> by {assigned_by}.</p>
            
            <div style="background-color: #f4f5f7; border-left: 4px solid #0052cc; padding: 16px; border-radius: 4px; margin: 20px 0;">
                <p style="margin: 0 0 8px 0; font-size: 14px;"><strong>Subject:</strong> {ticket.subject}</p>
                <p style="margin: 0 0 8px 0; font-size: 14px;"><strong>Priority:</strong> {prio_name}</p>
                <p style="margin: 0 0 8px 0; font-size: 14px;"><strong>Status:</strong> {status_name}</p>
                <p style="margin: 0; font-size: 14px;"><strong>Start Date:</strong> {start_date_str} | <strong>Due Date:</strong> {due_date_str}</p>
            </div>
            
            <p style="font-size: 13px; color: #626f86;">Log into Team Vatana Jira system to review and manage this ticket.</p>
        </div>
    </div>
    """
    try:
        resend.Emails.send({
            "from": sender_email,
            "to": [assigned_user.email],
            "subject": subject,
            "html": html_content
        })
        print(f"Successfully sent assignment notification email to {assigned_user.email} for ticket {ticket.ticket_code}")
    except Exception as e:
        print(f"Resend notification error: {e}")

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.conf import settings
from django.core.files.storage import default_storage, FileSystemStorage
from django.urls import reverse
from .models import (
    Ticket, TicketStatus, Priority, TicketCategory, TicketComment,
    TicketLog, TicketAssignment, UserProfile, ServiceRating, SLARule,
    TicketAttachment, Role
)

def save_file_to_storage(file_obj, subfolder, custom_filename=None):
    """
    Saves an uploaded file using Django's default storage 
    (Cloudflare R2 / S3 if credentials configured, or FileSystemStorage locally).
    Returns the public URL of the saved file.
    """
    filename = custom_filename or file_obj.name
    save_path = f"{subfolder}/{filename}"
    saved_name = default_storage.save(save_path, file_obj)
    return default_storage.url(saved_name)



def login_view(request):
    """Handle user login via Username or Email."""
    if request.user.is_authenticated:
        return redirect('board')

    next_url = request.GET.get('next', '') or request.POST.get('next', '')

    if request.method == 'POST':
        identifier = request.POST.get('username_or_email', '').strip()
        password = request.POST.get('password', '').strip()

        if not identifier or not password:
            return render(request, 'login.html', {
                'error': 'Please provide both username/email and password.',
                'username_or_email': identifier,
                'next_url': next_url,
            })

        # Search for user by email first (case-insensitive), then username
        target_user = User.objects.filter(email__iexact=identifier).first()
        if not target_user:
            target_user = User.objects.filter(username__iexact=identifier).first()

        username_to_auth = target_user.username if target_user else identifier

        user = authenticate(request, username=username_to_auth, password=password)

        if user is not None:
            profile = getattr(user, 'profile', None)
            if profile and not profile.is_email_verified and not user.is_superuser:
                return render(request, 'login.html', {
                    'error': f'Your email address ({user.email}) has not been verified yet.',
                    'unverified_email': user.email,
                    'username_or_email': identifier,
                    'next_url': next_url,
                })

            login(request, user)
            if next_url and next_url != '/login/' and next_url != 'login':
                return redirect(next_url)
            return redirect('board')
        else:
            return render(request, 'login.html', {
                'error': 'Invalid email/username or password. Please try again.',
                'username_or_email': identifier,
                'next_url': next_url,
            })

    return render(request, 'login.html', {'next_url': next_url})


def signup_view(request):
    """Handle new user self-registration with Email Verification."""
    if request.user.is_authenticated:
        return redirect('board')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        username = request.POST.get('username', '').strip().lower()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not username or not email or not password:
            return render(request, 'login.html', {
                'active_tab': 'signup',
                'error': 'Username, email, and password are required.',
                'full_name': full_name,
                'signup_username': username,
                'signup_email': email,
            })

        if password != confirm_password:
            return render(request, 'login.html', {
                'active_tab': 'signup',
                'error': 'Passwords do not match.',
                'full_name': full_name,
                'signup_username': username,
                'signup_email': email,
            })

        if len(password) < 6:
            return render(request, 'login.html', {
                'active_tab': 'signup',
                'error': 'Password must be at least 6 characters long.',
                'full_name': full_name,
                'signup_username': username,
                'signup_email': email,
            })

        if User.objects.filter(username__iexact=username).exists():
            return render(request, 'login.html', {
                'active_tab': 'signup',
                'error': 'Username is already taken.',
                'full_name': full_name,
                'signup_username': username,
                'signup_email': email,
            })

        if User.objects.filter(email__iexact=email).exists():
            return render(request, 'login.html', {
                'active_tab': 'signup',
                'error': 'An account with this email address already exists.',
                'full_name': full_name,
                'signup_username': username,
                'signup_email': email,
            })

        # Create User
        user = User.objects.create_user(username=username, email=email, password=password)
        if full_name:
            name_parts = full_name.split()
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = " ".join(name_parts[1:])
            user.save()

        # Get or Create default 'Viewer' (Guest) Role for new registered accounts
        guest_role, _ = Role.objects.get_or_create(role_name='Viewer', defaults={'description': 'Guest / Viewer (Read Only)'})
        profile = UserProfile.objects.create(
            user=user,
            role=guest_role,
            full_name=full_name or username,
            status='Active',
            is_email_verified=False
        )

        # Send verification email
        verify_url = send_verification_email(request, user)

        return render(request, 'login.html', {
            'active_tab': 'verification_sent',
            'verification_email': email,
            'verification_url': verify_url,
        })

    return redirect('login')


def verify_email_view(request, token):
    """Verify user's email address using token."""
    profile = UserProfile.objects.filter(email_verification_token=token).first()
    if profile:
        profile.is_email_verified = True
        profile.email_verification_token = None
        profile.save(update_fields=['is_email_verified', 'email_verification_token'])

        # Auto login user upon successful email verification
        login(request, profile.user)

        return render(request, 'tickets/email_verified.html', {
            'success': True,
            'user_name': profile.full_name or profile.user.username,
            'email': profile.user.email
        })
    else:
        return render(request, 'tickets/email_verified.html', {
            'success': False,
            'error': 'This email verification link is invalid or has already been used.'
        })


def resend_verification_view(request):
    """Resend email verification link."""
    email = request.POST.get('email', '').strip().lower() or request.GET.get('email', '').strip().lower()
    if not email:
        return render(request, 'login.html', {
            'error': 'Please enter your registered email address.'
        })

    target_user = User.objects.filter(email__iexact=email).first()
    if not target_user:
        return render(request, 'login.html', {
            'error': 'No account found with this email address.'
        })

    profile = getattr(target_user, 'profile', None)
    if profile and profile.is_email_verified:
        return render(request, 'login.html', {
            'error': 'Your email address is already verified! You can log in directly.',
            'username_or_email': email
        })

    verify_url = send_verification_email(request, target_user)

    return render(request, 'login.html', {
        'active_tab': 'verification_sent',
        'verification_email': target_user.email,
        'verification_url': verify_url,
    })


def logout_view(request):
    """Log out current user and redirect to login page."""
    logout(request)
    return redirect('login')


def normalize_role_name(role_str):
    """Normalize role string to canonical names (Administrator, Member, Support Agent, Viewer)."""
    if not role_str:
        return 'Member'
    r = str(role_str).strip()
    if r in ['Admin', 'Administrator', 'admin', 'administrator']:
        return 'Administrator'
    if r in ['User', 'Member', 'user', 'member']:
        return 'Member'
    if r in ['Support Agent', 'Agent', 'support agent', 'agent']:
        return 'Support Agent'
    if r in ['Viewer', 'Guest', 'viewer', 'guest', 'guest - collaborator']:
        return 'Viewer'
    return r


def can_user_edit_ticket(user):
    """Check if user role has permission to edit tickets (Admins/Members can edit; Viewers cannot)."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    profile = getattr(user, 'profile', None)
    if profile and profile.role:
        role_name = normalize_role_name(profile.role.role_name)
        if role_name in ['Administrator', 'Member', 'Support Agent']:
            return True
        if role_name == 'Viewer':
            return False
    return True


@login_required
@require_POST
def api_create_user(request):
    """Admin-only API endpoint to add new team accounts ("Add people to Team Vatana")."""
    profile = getattr(request.user, 'profile', None)
    is_admin = request.user.is_superuser or (profile and profile.role and profile.role.role_name in ['Admin', 'Administrator'])

    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Permission denied. Only Admins can add new team accounts.'}, status=403)

    try:
        data = json.loads(request.body)
        raw_input = data.get('names_or_emails', '').strip() or data.get('email', '').strip() or data.get('full_name', '').strip()
        role_name_input = data.get('role_name', 'Member').strip()

        if not raw_input:
            return JsonResponse({'success': False, 'error': 'Name or email is required.'}, status=400)

        # Extract email and full name
        if '@' in raw_input:
            email = raw_input.lower()
            username = email.split('@')[0]
            full_name = data.get('full_name', '').strip() or username.capitalize()
        else:
            full_name = raw_input
            username = raw_input.lower().replace(' ', '')
            email = f"{username}@company.com"

        # Check existing username / email
        base_username = username
        counter = 1
        while User.objects.filter(username__iexact=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        if User.objects.filter(email__iexact=email).exists():
            email = f"{username}@company.com"

        password = data.get('password', '').strip() or 'Welcome123!'

        user = User.objects.create_user(username=username, email=email, password=password)
        if full_name:
            name_parts = full_name.split()
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = " ".join(name_parts[1:])
            user.save()

        # Role mapping
        role_obj, _ = Role.objects.get_or_create(role_name=role_name_input)
        if role_name_input in ['Administrator', 'Admin', 'Support Agent']:
            user.is_staff = True
            if role_name_input in ['Administrator', 'Admin']:
                user.is_superuser = True
            user.save()

        UserProfile.objects.create(
            user=user,
            role=role_obj,
            full_name=full_name or username,
            status='Active'
        )

        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': full_name or user.username,
                'role': role_obj.role_name
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

    try:
        data = json.loads(request.body)
        full_name = data.get('full_name', '').strip()
        username = data.get('username', '').strip().lower()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        role_id = data.get('role_id')
        department = data.get('department', '').strip()

        if not username or not email or not password:
            return JsonResponse({'success': False, 'error': 'Username, email, and password are required.'}, status=400)

        if User.objects.filter(username__iexact=username).exists():
            return JsonResponse({'success': False, 'error': 'Username is already taken.'}, status=400)

        if User.objects.filter(email__iexact=email).exists():
            return JsonResponse({'success': False, 'error': 'Email is already in use.'}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        if full_name:
            name_parts = full_name.split()
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = " ".join(name_parts[1:])
            user.save()

        role_id = data.get('role_id')
        role_name = data.get('role_name')
        role_obj = None
        if role_id:
            role_obj = Role.objects.filter(role_id=role_id).first()
        if not role_obj and role_name:
            role_obj = Role.objects.filter(role_name__iexact=role_name).first()

        if role_obj and role_obj.role_name in ['Admin', 'Support Agent']:
            user.is_staff = True
            if role_obj.role_name == 'Admin':
                user.is_superuser = True
            user.save()


        UserProfile.objects.create(
            user=user,
            role=role_obj,
            full_name=full_name or username,
            department=department,
            status='Active'
        )

        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': full_name or user.username,
                'role': role_obj.role_name if role_obj else 'User'
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def board_view(request):

    """Render Jira-inspired Kanban board view."""
    statuses = TicketStatus.objects.all().order_by('order')
    categories = TicketCategory.objects.all()
    priorities = Priority.objects.all()
    users = User.objects.all()

    # Search & Filter Parameters
    q = request.GET.get('q', '')
    cat_filter = request.GET.get('category', '')
    prio_filter = request.GET.get('priority', '')
    assignee_filter = request.GET.get('assignee', '')

    tickets_qs = Ticket.objects.select_related('status', 'priority', 'category', 'user', 'assigned_to').all()

    if q:
        tickets_qs = tickets_qs.filter(Q(subject__icontains=q) | Q(ticket_code__icontains=q) | Q(description__icontains=q))
    if cat_filter:
        tickets_qs = tickets_qs.filter(category_id=cat_filter)
    if prio_filter:
        tickets_qs = tickets_qs.filter(priority_id=prio_filter)
    if assignee_filter:
        tickets_qs = tickets_qs.filter(assigned_to_id=assignee_filter)

    # Group tickets by status
    board_columns = []
    for st in statuses:
        st_tickets = tickets_qs.filter(status=st)
        board_columns.append({
            'status': st,
            'tickets': st_tickets,
            'count': st_tickets.count()
        })

    context = {
        'board_columns': board_columns,
        'statuses': statuses,
        'categories': categories,
        'priorities': priorities,
        'users': users,
        'active_view': 'board',
        'query': q,
        'cat_filter': cat_filter,
        'prio_filter': prio_filter,
        'assignee_filter': assignee_filter,
    }
    return render(request, 'tickets/board.html', context)


@login_required
def for_you_view(request):
    """Render Jira 'For You' dashboard with sub-tabs (Assigned to me, Worked on, Viewed)."""
    active_tab = request.GET.get('tab', 'assigned')
    if active_tab not in ['assigned', 'worked_on', 'viewed']:
        active_tab = 'assigned'
    
    # Query datasets
    assigned_qs = Ticket.objects.filter(assigned_to=request.user).select_related('status', 'priority', 'category', 'user', 'assigned_to').order_by('-created_at')
    worked_on_qs = Ticket.objects.filter(
        Q(user=request.user) | Q(assigned_to=request.user) | Q(comments__user=request.user)
    ).distinct().select_related('status', 'priority', 'category', 'user', 'assigned_to').order_by('-created_at')
    all_tickets_qs = Ticket.objects.select_related('status', 'priority', 'category', 'user', 'assigned_to').order_by('-created_at')

    assigned_count = assigned_qs.count()
    worked_on_count = worked_on_qs.count()
    viewed_count = all_tickets_qs.count()

    def get_time_info(dt):
        if not dt:
            return "In the last week", "Recently"
        now = timezone.now()
        today = now.date()
        item_date = dt.date()
        diff = now - dt

        if item_date == today:
            group_name = "Today"
            seconds = diff.total_seconds()
            if seconds < 60:
                time_str = "Just now"
            elif seconds < 3600:
                mins = max(1, int(seconds // 60))
                time_str = f"{mins} minutes ago"
            else:
                hours = int(seconds // 3600)
                time_str = f"{hours} hours ago"
        elif item_date == (today - timedelta(days=1)):
            group_name = "Yesterday"
            time_str = "Yesterday"
        elif (today - timedelta(days=7)) <= item_date < (today - timedelta(days=1)):
            group_name = "In the last week"
            days_ago = (today - item_date).days
            time_str = f"{days_ago} days ago"
        else:
            group_name = "Older"
            time_str = dt.strftime("%d %b %Y")

        return group_name, time_str

    def get_user_initials(u):
        if not u:
            return "PV"
        profile = getattr(u, 'profile', None)
        full_name = profile.full_name.strip() if profile and profile.full_name else ''
        name = full_name or u.username
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return name[:2].upper()

    time_groups = ["Today", "Yesterday", "In the last week", "Older"]
    grouped_sections = []

    if active_tab == 'assigned':
        statuses = TicketStatus.objects.all().order_by('order')
        for st in statuses:
            st_tickets = [t for t in assigned_qs if t.status_id == st.status_id]
            if st_tickets:
                grouped_sections.append({
                    'group_title': st.status_name,
                    'is_status_group': True,
                    'tickets': st_tickets,
                    'count': len(st_tickets)
                })
    elif active_tab == 'worked_on':
        grouped_dict = {g: [] for g in time_groups}
        for t in worked_on_qs:
            group_name, time_str = get_time_info(t.created_at)
            cat_name = t.category.category_name if t.category else 'Feature'
            issue_type = cat_name if cat_name in ['Feature', 'Subtask', 'Task', 'Bug'] else ('Subtask' if 'sub' in t.subject.lower() else 'Feature')
            grouped_dict[group_name].append({
                'is_space_or_board': False,
                'ticket_id': t.ticket_id,
                'title': t.subject,
                'subtitle': f"{issue_type} · {t.ticket_code} · Team Vatana",
                'time_str': time_str,
                'user_initials': get_user_initials(request.user),
                'issue_type': issue_type
            })

        for g in time_groups:
            if grouped_dict[g]:
                grouped_sections.append({
                    'group_title': g,
                    'is_status_group': False,
                    'items': grouped_dict[g]
                })
    else: # viewed
        viewed_items = []
        viewed_items.append({
            'is_space_or_board': True,
            'title': 'Team Vatana',
            'subtitle': 'Team-managed software',
            'icon_type': 'space',
            'time_str': '15 minutes ago',
            'group_name': 'Today',
            'url': '/board/'
        })
        viewed_items.append({
            'is_space_or_board': True,
            'title': 'KAN board',
            'subtitle': 'Board · Team Vatana',
            'icon_type': 'board',
            'time_str': '15 minutes ago',
            'group_name': 'Today',
            'url': '/board/'
        })

        for t in all_tickets_qs:
            group_name, time_str = get_time_info(t.created_at)
            cat_name = t.category.category_name if t.category else 'Feature'
            issue_type = cat_name if cat_name in ['Feature', 'Subtask', 'Task', 'Bug'] else ('Subtask' if 'sub' in t.subject.lower() else 'Feature')
            viewed_items.append({
                'is_space_or_board': False,
                'ticket_id': t.ticket_id,
                'title': t.subject,
                'subtitle': f"{issue_type} · {t.ticket_code} · Team Vatana",
                'time_str': time_str,
                'group_name': group_name,
                'issue_type': issue_type
            })

        grouped_dict = {g: [] for g in time_groups}
        for item in viewed_items:
            grouped_dict[item['group_name']].append(item)

        for g in time_groups:
            if grouped_dict[g]:
                grouped_sections.append({
                    'group_title': g,
                    'is_status_group': False,
                    'items': grouped_dict[g]
                })

    context = {
        'active_view': 'for_you',
        'active_tab': active_tab,
        'assigned_count': assigned_count,
        'worked_on_count': worked_on_count,
        'viewed_count': viewed_count,
        'grouped_sections': grouped_sections,
    }
    return render(request, 'tickets/for_you.html', context)


@login_required
def list_view(request):
    """Render structured table view of tickets."""
    tickets = Ticket.objects.select_related('status', 'priority', 'category', 'user', 'assigned_to').all().order_by('-created_at')
    priorities = Priority.objects.all().order_by('priority_id')
    categories = TicketCategory.objects.all()
    statuses = TicketStatus.objects.all().order_by('order')
    users = User.objects.all()
    
    # Simple search filtering
    q = request.GET.get('q', '')
    if q:
        tickets = tickets.filter(Q(subject__icontains=q) | Q(ticket_code__icontains=q))

    context = {
        'tickets': tickets,
        'priorities': priorities,
        'categories': categories,
        'statuses': statuses,
        'users': users,
        'active_view': 'list',
        'query': q,
    }
    return render(request, 'tickets/list.html', context)


@login_required
def summary_view(request):

    """Render executive dashboard metrics summary."""
    total_tickets = Ticket.objects.count()
    open_tickets = Ticket.objects.exclude(status__status_name__in=['Done', 'Closed']).count()
    done_tickets = Ticket.objects.filter(status__status_name='Done').count()

    tickets_by_status = TicketStatus.objects.annotate(ticket_count=Count('tickets'))
    tickets_by_priority = Priority.objects.annotate(ticket_count=Count('tickets'))
    tickets_by_category = TicketCategory.objects.annotate(ticket_count=Count('tickets'))

    recent_activities = TicketLog.objects.select_related('ticket', 'user').order_by('-created_at')[:10]

    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'done_tickets': done_tickets,
        'tickets_by_status': tickets_by_status,
        'tickets_by_priority': tickets_by_priority,
        'tickets_by_category': tickets_by_category,
        'recent_activities': recent_activities,
        'active_view': 'summary',
    }
    return render(request, 'tickets/summary.html', context)


@login_required
def teams_view(request):
    """Render Team Vatana member management dashboard."""
    users_qs = User.objects.filter(is_active=True).select_related('profile', 'profile__role').order_by('-date_joined')
    
    current_profile = getattr(request.user, 'profile', None)
    is_admin = request.user.is_superuser or (current_profile and current_profile.role and current_profile.role.role_name in ['Admin', 'Administrator'])

    members_data = []
    total_count = len(users_qs)
    admin_count = 0
    member_count = 0
    viewer_count = 0
    agent_count = 0

    for u in users_qs:
        profile = getattr(u, 'profile', None)
        role_obj = profile.role if profile else None
        raw_role = role_obj.role_name if role_obj else ('Administrator' if u.is_superuser else 'Member')
        role_name = normalize_role_name(raw_role)
        
        r_lower = role_name.lower()
        if 'admin' in r_lower:
            admin_count += 1
        elif 'agent' in r_lower:
            agent_count += 1
        elif 'viewer' in r_lower or 'guest' in r_lower:
            viewer_count += 1
        else:
            member_count += 1

        full_name = profile.full_name.strip() if profile and profile.full_name else ''
        public_name = profile.public_name.strip() if profile and profile.public_name else ''
        display_name = full_name or public_name or (f"{u.first_name} {u.last_name}".strip()) or u.username
        parts = display_name.split()
        initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else display_name[:2].upper()

        members_data.append({
            'id': u.id,
            'username': u.username,
            'email': u.email or '',
            'display_name': display_name,
            'initials': initials,
            'avatar_color': profile.avatar_color if profile and profile.avatar_color else '#0052cc',
            'profile_image': profile.profile_image if profile and profile.profile_image else '',
            'role': role_name,
            'department': (profile.job_title if profile and profile.job_title else (profile.department if profile and profile.department else 'Software Team')),
            'status': profile.status if profile else 'Active',
            'date_joined': u.date_joined.strftime('%b %d, %Y'),
            'is_self': (u.id == request.user.id)
        })

    context = {
        'active_view': 'teams',
        'is_admin': is_admin,
        'members': members_data,
        'total_count': total_count,
        'admin_count': admin_count,
        'member_count': member_count,
        'viewer_count': viewer_count,
        'agent_count': agent_count,
    }
    return render(request, 'tickets/teams.html', context)


# ---------------- API ENDPOINTS FOR AJAX & UI INTERACTION ----------------

import time

GLOBAL_BOARD_VERSION = int(time.time() * 1000)

def bump_board_version():
    """Bump version timestamp whenever board data changes."""
    global GLOBAL_BOARD_VERSION
    GLOBAL_BOARD_VERSION = int(time.time() * 1000)


@require_GET
def api_board_sync(request):
    """
    Lightweight, high-performance real-time sync endpoint.
    Returns { updated: False } if no changes occurred since last version check.
    If changes occurred, returns updated tickets and column counts for live DOM animation.
    """
    try:
        client_ver = request.GET.get('ver', 0)
        try:
            client_ver = int(client_ver)
        except (ValueError, TypeError):
            client_ver = 0

        if client_ver == GLOBAL_BOARD_VERSION:
            return JsonResponse({'updated': False, 'ver': GLOBAL_BOARD_VERSION})

        tickets = Ticket.objects.select_related('status', 'priority', 'assigned_to').all()
        tickets_data = []
        for t in tickets:
            tickets_data.append({
                'ticket_id': t.ticket_id,
                'ticket_code': t.ticket_code,
                'subject': t.subject,
                'status_id': t.status.status_id if t.status else None,
                'status_name': t.status.status_name if t.status else '',
                'priority_id': t.priority.priority_id if t.priority else None,
                'priority_name': t.priority.priority_name if t.priority else '',
                'due_date': safe_format_date(t.due_date, '%Y-%m-%d'),
                'due_date_formatted': safe_format_date(t.due_date, '%d %b %Y'),

                'is_due_soon': t.is_due_soon,
                'assignee': t.assigned_to.username if t.assigned_to else '',
                'assignee_initials': (t.assigned_to.username[:2].upper()) if t.assigned_to else '',
            })

        statuses = TicketStatus.objects.all()
        counts = {}
        for st in statuses:
            counts[st.status_id] = Ticket.objects.filter(status=st).count()

        return JsonResponse({
            'updated': True,
            'ver': GLOBAL_BOARD_VERSION,
            'tickets': tickets_data,
            'column_counts': counts
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def api_update_status(request, ticket_id):
    """Update ticket status via AJAX (Drag and drop or inline change)."""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    if not can_user_edit_ticket(request.user):
        return JsonResponse({'success': False, 'error': 'Permission denied. Your role only has View access and cannot edit tickets.'}, status=403)
    try:
        data = json.loads(request.body)
        new_status_id = data.get('status_id')
        new_status = get_object_or_404(TicketStatus, status_id=new_status_id)

        old_status_name = ticket.status.status_name if ticket.status else "None"
        ticket.status = new_status
        ticket.save()
        bump_board_version()

        # Log change
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else User.objects.first()
        TicketLog.objects.create(
            ticket=ticket,
            user=user,
            action_type="Status Change",
            old_value=old_status_name,
            new_value=new_status.status_name
        )

        return JsonResponse({'success': True, 'ticket_code': ticket.ticket_code, 'new_status': new_status.status_name})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)



@csrf_exempt
@require_POST
def api_update_priority(request, ticket_id):
    """Update ticket priority via AJAX (Inline table change)."""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    if not can_user_edit_ticket(request.user):
        return JsonResponse({'success': False, 'error': 'Permission denied. Your role only has View access and cannot edit tickets.'}, status=403)
    try:
        data = json.loads(request.body)
        new_priority_id = data.get('priority_id')
        new_priority = get_object_or_404(Priority, priority_id=new_priority_id)

        old_priority_name = ticket.priority.priority_name if ticket.priority else "None"
        ticket.priority = new_priority
        ticket.save()
        bump_board_version()

        # Log change
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else User.objects.first()
        TicketLog.objects.create(
            ticket=ticket,
            user=user,
            action_type="Priority Change",
            old_value=old_priority_name,
            new_value=new_priority.priority_name
        )

        return JsonResponse({
            'success': True,
            'ticket_code': ticket.ticket_code,
            'new_priority': new_priority.priority_name,
            'priority_id': new_priority.priority_id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def api_create_status(request):
    """Create a new ticket status dynamically for the Kanban board."""
    try:
        data = json.loads(request.body)
        status_name = data.get('status_name', '').strip()
        if not status_name:
            return JsonResponse({'success': False, 'error': 'Status name is required.'}, status=400)

        last_status = TicketStatus.objects.order_by('-order').first()
        next_order = (last_status.order + 1) if last_status else 1

        status, created = TicketStatus.objects.get_or_create(
            status_name=status_name,
            defaults={'order': next_order, 'description': f'Status: {status_name}'}
        )
        bump_board_version()

        return JsonResponse({
            'success': True,
            'status_id': status.status_id,
            'status_name': status.status_name
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def api_move_status(request, status_id):
    """Move status column left or right by swapping order with adjacent status."""
    status = get_object_or_404(TicketStatus, status_id=status_id)
    try:
        data = json.loads(request.body)
        direction = data.get('direction', '')

        all_statuses = list(TicketStatus.objects.all().order_by('order', 'status_id'))
        idx = None
        for i, s in enumerate(all_statuses):
            if s.status_id == status.status_id:
                idx = i
                break

        if idx is None:
            return JsonResponse({'success': False, 'error': 'Status not found.'}, status=404)

        if direction == 'left' and idx > 0:
            swap_target = all_statuses[idx - 1]
            status.order, swap_target.order = swap_target.order, status.order
            status.save()
            swap_target.save()
        elif direction == 'right' and idx < (len(all_statuses) - 1):
            swap_target = all_statuses[idx + 1]
            status.order, swap_target.order = swap_target.order, status.order
            status.save()
            swap_target.save()

        bump_board_version()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def api_delete_status(request, status_id):
    """Delete a ticket status column and reassign existing tickets to default status."""
    status = get_object_or_404(TicketStatus, status_id=status_id)
    try:
        fallback_status = TicketStatus.objects.exclude(status_id=status_id).order_by('order').first()
        if fallback_status:
            Ticket.objects.filter(status=status).update(status=fallback_status)
        status.delete()
        bump_board_version()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



@csrf_exempt
@require_POST
def api_create_category(request):


    """Create a new ticket category dynamically."""
    try:
        data = json.loads(request.body)
        category_name = data.get('category_name', '').strip()
        if not category_name:
            return JsonResponse({'success': False, 'error': 'Category name is required.'}, status=400)

        category, created = TicketCategory.objects.get_or_create(
            category_name=category_name,
            defaults={'status': 'Active'}
        )
        return JsonResponse({
            'success': True,
            'category_id': category.category_id,
            'category_name': category.category_name
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def api_create_ticket(request):
    """Create a new ticket from modal form (supports JSON & multipart/form-data with attachments)."""
    try:
        if request.content_type and 'multipart/form-data' in request.content_type:
            subject = request.POST.get('subject')
            description = request.POST.get('description', '')
            category_id = request.POST.get('category_id')
            priority_id = request.POST.get('priority_id')
            status_id = request.POST.get('status_id')
            assigned_to_id = request.POST.get('assigned_to_id')
            start_date = request.POST.get('start_date') or None
            due_date = request.POST.get('due_date') or None
        else:
            data = json.loads(request.body)
            subject = data.get('subject')
            description = data.get('description', '')
            category_id = data.get('category_id')
            priority_id = data.get('priority_id')
            status_id = data.get('status_id')
            assigned_to_id = data.get('assigned_to_id')
            start_date = data.get('start_date') or None
            due_date = data.get('due_date') or None

        if not subject:
            return JsonResponse({'success': False, 'error': 'Subject is required.'}, status=400)

        # Generate ticket code (e.g. KAN-12)
        last_ticket = Ticket.objects.order_by('-ticket_id').first()
        next_num = (last_ticket.ticket_id + 1) if last_ticket else 1
        ticket_code = f"KAN-{next_num}"

        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else User.objects.first()

        category = TicketCategory.objects.filter(pk=category_id).first() if category_id else None
        priority = Priority.objects.filter(pk=priority_id).first() if priority_id else Priority.objects.filter(priority_name='Medium').first()
        status = TicketStatus.objects.filter(pk=status_id).first() if status_id else TicketStatus.objects.first()
        assigned_to = User.objects.filter(pk=assigned_to_id).first() if assigned_to_id else None

        ticket = Ticket.objects.create(
            ticket_code=ticket_code,
            subject=subject,
            description=description,
            user=user,
            category=category,
            priority=priority,
            status=status,
            assigned_to=assigned_to,
            start_date=start_date,
            due_date=due_date
        )

        # Send email notification to assigned user via Resend if assigned
        if assigned_to:
            send_assignment_email(ticket, assigned_to)

        # Handle uploaded attachments
        if request.FILES:
            for file_obj in request.FILES.getlist('attachments'):
                file_url = save_file_to_storage(file_obj, 'attachments')
                TicketAttachment.objects.create(
                    ticket=ticket,
                    uploaded_by=user,
                    file_name=file_obj.name,
                    file_path=file_url,
                    file_type=file_obj.content_type or ''
                )

        TicketLog.objects.create(
            ticket=ticket,
            user=user,
            action_type="Create",
            new_value=f"Created {ticket.ticket_code}"
        )

        return JsonResponse({'success': True, 'ticket_id': ticket.ticket_id, 'ticket_code': ticket.ticket_code})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)



@require_GET
def api_ticket_details(request, ticket_id):
    """Retrieve full details of a ticket, comments, activity log, and attachments."""
    ticket = get_object_or_404(
        Ticket.objects.select_related('status', 'priority', 'category', 'user', 'assigned_to'),
        ticket_id=ticket_id
    )

    comments = ticket.comments.select_related('user').order_by('created_at')
    logs = ticket.logs.select_related('user').order_by('-created_at')
    attachments = ticket.attachments.select_related('uploaded_by').order_by('-uploaded_at')

    comments_data = []
    for c in comments:
        c_prof = getattr(c.user, 'profile', None)
        c_full = c_prof.full_name.strip() if c_prof and c_prof.full_name else ''
        c_pub = c_prof.public_name.strip() if c_prof and c_prof.public_name else ''
        c_disp = c_full or c_pub or c.user.username
        c_parts = c_disp.split()
        c_init = (c_parts[0][0] + c_parts[-1][0]).upper() if len(c_parts) >= 2 else c_disp[:2].upper()
        comments_data.append({
            'id': c.comment_id,
            'parent_id': c.parent_comment.comment_id if c.parent_comment else None,
            'user': c_disp,
            'user_initials': c_init,
            'user_avatar_color': c_prof.avatar_color if c_prof and c_prof.avatar_color else '#0052cc',
            'user_profile_image': c_prof.profile_image if c_prof and c_prof.profile_image else '',
            'text': c.comment_text,
            'is_internal': c.is_internal,
            'created_at': c.created_at.strftime('%d %b %Y, %H:%M')
        })


    logs_data = [{
        'user': l.user.username,
        'action': l.action_type,
        'old_value': l.old_value or '',
        'new_value': l.new_value or '',
        'created_at': l.created_at.strftime('%d %b %Y, %H:%M')
    } for l in logs]

    attachments_data = []
    for a in attachments:
        size_str = '0 KB'
        if a.file_path:
            rel_path = a.file_path.lstrip('/')
            full_path = settings.BASE_DIR / rel_path
            if os.path.exists(full_path):
                bytes_size = os.path.getsize(full_path)
                if bytes_size >= 1024 * 1024:
                    size_str = f"{round(bytes_size / (1024 * 1024), 1)} MB"
                else:
                    size_str = f"{round(bytes_size / 1024, 1)} KB"

        file_name_lower = a.file_name.lower()
        is_image = (a.file_type and a.file_type.startswith('image/')) or file_name_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'))
        
        cat_type = 'other'
        if is_image:
            cat_type = 'images'
        elif file_name_lower.endswith(('.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.csv', '.ppt', '.pptx', '.zip', '.rar')):
            cat_type = 'documents'
        elif file_name_lower.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
            cat_type = 'videos'

        attachments_data.append({
            'id': a.attachment_id,
            'file_name': a.file_name,
            'file_url': a.file_path,
            'file_type': a.file_type or '',
            'category_type': cat_type,
            'is_image': is_image,
            'file_size': size_str,
            'uploaded_by': a.uploaded_by.username if a.uploaded_by else 'Unknown',
            'uploaded_at': a.uploaded_at.strftime('%b %d, %Y')
        })

    def get_user_dict(u, default_name='Unassigned'):
        if not u:
            return {
                'name': default_name, 'initials': '', 'email': '',
                'color': '#626f86', 'image': ''
            }
        profile = getattr(u, 'profile', None)
        full_name = profile.full_name.strip() if profile and profile.full_name else ''
        public_name = profile.public_name.strip() if profile and profile.public_name else ''
        display_name = full_name or public_name or (f"{u.first_name} {u.last_name}".strip()) or u.username or default_name
        parts = display_name.split()
        initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else display_name[:2].upper()
        return {
            'name': display_name,
            'initials': initials,
            'email': u.email or '',
            'color': profile.avatar_color if profile and profile.avatar_color else '#0052cc',
            'image': profile.profile_image if profile and profile.profile_image else ''
        }

    creator_dict = get_user_dict(ticket.user, default_name='Unknown')
    assignee_dict = get_user_dict(ticket.assigned_to, default_name='Unassigned')

    data = {
        'ticket_id': ticket.ticket_id,
        'ticket_code': ticket.ticket_code,
        'subject': ticket.subject,
        'description': ticket.description or '',
        'status': ticket.status.status_name if ticket.status else '',
        'status_id': ticket.status.status_id if ticket.status else None,
        'priority': ticket.priority.priority_name if ticket.priority else '',
        'priority_id': ticket.priority.priority_id if ticket.priority else None,
        'category': ticket.category.category_name if ticket.category else '',
        'creator': creator_dict['name'],
        'creator_email': creator_dict['email'],
        'creator_initials': creator_dict['initials'],
        'creator_color': creator_dict['color'],
        'creator_image': creator_dict['image'],
        'assignee': assignee_dict['name'],
        'assignee_email': assignee_dict['email'],
        'assignee_initials': assignee_dict['initials'],
        'assignee_color': assignee_dict['color'],
        'assignee_image': assignee_dict['image'],
        'start_date': safe_format_date(ticket.start_date, '%Y-%m-%d'),
        'start_date_formatted': safe_format_date(ticket.start_date, '%d %b %Y'),
        'due_date': safe_format_date(ticket.due_date, '%Y-%m-%d'),
        'due_date_formatted': safe_format_date(ticket.due_date, '%d %b %Y'),
        'is_due_soon': ticket.is_due_soon,
        'created_at': safe_format_date(ticket.created_at, '%d %b %Y, %H:%M'),


        'can_edit': can_user_edit_ticket(request.user),
        'comments': comments_data,
        'logs': logs_data,
        'attachments': attachments_data,
    }
    return JsonResponse({'success': True, 'ticket': data})


@csrf_exempt
@require_POST
def api_edit_ticket(request, ticket_id):
    """Edit ticket details (subject, description, assignee, priority, category, start date, due date)."""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    if not can_user_edit_ticket(request.user):
        return JsonResponse({'success': False, 'error': 'Permission denied. Your role only has View access and cannot edit tickets.'}, status=403)

    try:
        data = json.loads(request.body)
        subject = data.get('subject', '').strip()
        description = data.get('description', '').strip()
        assigned_to_id = data.get('assigned_to_id')
        priority_id = data.get('priority_id')
        category_id = data.get('category_id')
        start_date = data.get('start_date') or None
        due_date = data.get('due_date') or None

        if subject:
            ticket.subject = subject
        if description is not None:
            ticket.description = description

        old_assignee = ticket.assigned_to
        new_assignee = None

        if assigned_to_id == '' or assigned_to_id is None:
            ticket.assigned_to = None
        else:
            new_assignee = User.objects.filter(pk=assigned_to_id).first()
            ticket.assigned_to = new_assignee

        if priority_id:
            prio = Priority.objects.filter(pk=priority_id).first()
            if prio:
                ticket.priority = prio

        if category_id:
            cat = TicketCategory.objects.filter(pk=category_id).first()
            if cat:
                ticket.category = cat

        if 'start_date' in data:
            ticket.start_date = start_date
        ticket.due_date = due_date
        ticket.save()

        # Send email if assigned_to was updated to a new user
        if new_assignee and (not old_assignee or old_assignee.pk != new_assignee.pk):
            send_assignment_email(ticket, new_assignee)


        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else User.objects.first()
        TicketLog.objects.create(
            ticket=ticket,
            user=user,
            action_type="Update",
            new_value=f"Updated details for {ticket.ticket_code}"
        )

        return JsonResponse({'success': True, 'ticket_id': ticket.ticket_id, 'ticket_code': ticket.ticket_code})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def api_upload_attachment(request, ticket_id):
    """Upload a new attachment file/image to an existing ticket."""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    try:
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else User.objects.first()
        files = request.FILES.getlist('attachments')
        if not files:
            return JsonResponse({'success': False, 'error': 'No files provided.'}, status=400)

        created_attachments = []
        for file_obj in files:
            file_url = save_file_to_storage(file_obj, 'attachments')
            att = TicketAttachment.objects.create(
                ticket=ticket,
                uploaded_by=user,
                file_name=file_obj.name,
                file_path=file_url,
                file_type=file_obj.content_type or ''
            )
            created_attachments.append(att.file_name)

        TicketLog.objects.create(
            ticket=ticket,
            user=user,
            action_type="Attachment Added",
            new_value=f"Uploaded {', '.join(created_attachments)}"
        )

        return JsonResponse({'success': True, 'message': f"Uploaded {len(created_attachments)} file(s)"})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def api_upload_comment_image(request):
    """Upload an image specifically for inline comment display (not added to TicketAttachments)."""
    try:
        files = request.FILES.getlist('image') or request.FILES.getlist('file') or request.FILES.getlist('attachments')
        if not files:
            return JsonResponse({'success': False, 'error': 'No image file provided.'}, status=400)

        uploaded_urls = []
        for file_obj in files:
            file_url = save_file_to_storage(file_obj, 'comment_images')
            uploaded_urls.append(file_url)

        return JsonResponse({
            'success': True,
            'url': uploaded_urls[0] if uploaded_urls else '',
            'urls': uploaded_urls
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def api_add_comment(request, ticket_id):
    """Add a new comment to a ticket."""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    try:
        data = json.loads(request.body)
        comment_text = data.get('comment_text')
        is_internal = data.get('is_internal', False)
        parent_id = data.get('parent_id') or None

        if not comment_text:
            return JsonResponse({'success': False, 'error': 'Comment text is required.'}, status=400)

        user = request.user if request.user.is_authenticated else User.objects.first()
        parent_comment = TicketComment.objects.filter(pk=parent_id).first() if parent_id else None

        comment = TicketComment.objects.create(
            ticket=ticket,
            user=user,
            parent_comment=parent_comment,
            comment_text=comment_text,
            is_internal=is_internal
        )


        profile = getattr(user, 'profile', None)
        full_name = profile.full_name.strip() if profile and profile.full_name else ''
        public_name = profile.public_name.strip() if profile and profile.public_name else ''
        user_display = full_name or public_name or user.username
        parts = user_display.split()
        initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else user_display[:2].upper()
        avatar_color = profile.avatar_color if profile and profile.avatar_color else '#0052cc'
        profile_image = profile.profile_image if profile and profile.profile_image else ''

        # Trigger Pusher real-time live event
        try:
            pusher_client.trigger(
                f'ticket_{ticket_id}',
                'new-comment',
                {
                    'comment_id': comment.comment_id,
                    'parent_id': comment.parent_comment.comment_id if comment.parent_comment else None,
                    'user': user_display,
                    'user_initials': initials,
                    'user_avatar_color': avatar_color,
                    'user_profile_image': profile_image,
                    'text': comment.comment_text,
                    'is_internal': comment.is_internal,
                    'created_at': comment.created_at.strftime('%d %b %Y, %H:%M')
                }
            )
        except Exception as p_err:
            print("Pusher trigger error:", p_err)

        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.comment_id,
                'parent_id': comment.parent_comment.comment_id if comment.parent_comment else None,
                'user': user_display,
                'user_initials': initials,
                'user_avatar_color': avatar_color,
                'user_profile_image': profile_image,
                'text': comment.comment_text,
                'is_internal': comment.is_internal,
                'created_at': comment.created_at.strftime('%d %b %Y, %H:%M')
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def api_delete_ticket(request, ticket_id):
    """Delete a ticket by ID via AJAX."""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    try:
        ticket_code = ticket.ticket_code
        ticket.delete()
        return JsonResponse({'success': True, 'ticket_code': ticket_code})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@login_required
@require_POST
def api_update_user_role(request, user_id):
    """Admin-only API endpoint to update a team member's role in real-time."""
    current_profile = getattr(request.user, 'profile', None)
    is_admin = request.user.is_superuser or (current_profile and current_profile.role and current_profile.role.role_name in ['Admin', 'Administrator'])

    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Permission denied. Only Admins can modify team roles.'}, status=403)

    target_user = get_object_or_404(User, id=user_id)
    try:
        data = json.loads(request.body)
        raw_role_input = data.get('role_name', '').strip()
        new_role_name = normalize_role_name(raw_role_input)

        if not new_role_name:
            return JsonResponse({'success': False, 'error': 'Role name is required.'}, status=400)

        role_obj, _ = Role.objects.get_or_create(role_name=new_role_name)
        
        profile, _ = UserProfile.objects.get_or_create(user=target_user)
        profile.role = role_obj
        profile.save()

        if new_role_name in ['Administrator', 'Admin']:
            target_user.is_staff = True
            target_user.is_superuser = True
        elif new_role_name in ['Support Agent']:
            target_user.is_staff = True
            target_user.is_superuser = False
        else:
            target_user.is_staff = False
            target_user.is_superuser = False
        target_user.save()

        try:
            pusher_client.trigger('team_management', 'role-updated', {
                'user_id': target_user.id,
                'new_role': role_obj.role_name
            })
        except Exception:
            pass

        return JsonResponse({'success': True, 'user_id': target_user.id, 'new_role': role_obj.role_name})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@login_required
@require_POST
def api_remove_user(request, user_id):
    """Admin-only API endpoint to remove a user from Team Vatana."""
    current_profile = getattr(request.user, 'profile', None)
    is_admin = request.user.is_superuser or (current_profile and current_profile.role and current_profile.role.role_name in ['Admin', 'Administrator'])

    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Permission denied. Only Admins can remove team members.'}, status=403)

    if user_id == request.user.id:
        return JsonResponse({'success': False, 'error': 'You cannot remove your own account.'}, status=400)

    target_user = get_object_or_404(User, id=user_id)
    try:
        target_user.is_active = False
        target_user.save()

        profile = getattr(target_user, 'profile', None)
        if profile:
            profile.status = 'Inactive'
            profile.save()

        try:
            pusher_client.trigger('team_management', 'user-removed', {
                'user_id': target_user.id
            })
        except Exception:
            pass

        return JsonResponse({'success': True, 'user_id': user_id, 'username': target_user.username})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def api_get_profile(request):
    """API endpoint to get current user's profile details."""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    user_display = profile.full_name or profile.public_name or user.username
    parts = user_display.split()
    initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else user_display[:2].upper()

    return JsonResponse({
        'success': True,
        'profile': {
            'username': user.username,
            'email': user.email or '',
            'full_name': profile.full_name or '',
            'public_name': profile.public_name or user.username,
            'job_title': profile.job_title or '',
            'pronouns': profile.pronouns or '',
            'avatar_color': profile.avatar_color or '#0052cc',
            'header_color': profile.header_color or '#85b8ff',
            'profile_image': profile.profile_image or '',
            'initials': initials,
            'role': profile.role.role_name if profile.role else 'User'
        }
    })


@csrf_exempt
@login_required
@require_POST
def api_update_profile(request):
    """API endpoint allowing users to edit their own profile (name, public name, job title, pronouns, avatar color, header color, profile image)."""
    try:
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)

        full_name = request.POST.get('full_name', '').strip()
        public_name = request.POST.get('public_name', '').strip()
        job_title = request.POST.get('job_title', '').strip()
        pronouns = request.POST.get('pronouns', '').strip()
        avatar_color = request.POST.get('avatar_color', '').strip()
        header_color = request.POST.get('header_color', '').strip()
        remove_photo = request.POST.get('remove_photo') == 'true'

        if full_name:
            profile.full_name = full_name
            parts = full_name.split(maxsplit=1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''
            user.save()

        if public_name:
            profile.public_name = public_name

        profile.job_title = job_title
        profile.pronouns = pronouns

        if avatar_color:
            profile.avatar_color = avatar_color
        if header_color:
            profile.header_color = header_color

        if remove_photo:
            profile.profile_image = None
        elif 'profile_image' in request.FILES:
            image_file = request.FILES['profile_image']
            custom_name = f"user_{user.id}_{image_file.name}"
            profile.profile_image = save_file_to_storage(image_file, 'profile_images', custom_filename=custom_name)

        profile.save()

        user_display = profile.full_name or profile.public_name or user.username
        parts = user_display.split()
        initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else user_display[:2].upper()

        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully!',
            'profile': {
                'full_name': profile.full_name or '',
                'public_name': profile.public_name or '',
                'job_title': profile.job_title or '',
                'pronouns': profile.pronouns or '',
                'avatar_color': profile.avatar_color or '#0052cc',
                'header_color': profile.header_color or '#85b8ff',
                'profile_image': profile.profile_image or '',
                'initials': initials,
                'user_display': user_display
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


