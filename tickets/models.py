from django.db import models
from django.contrib.auth.models import User

class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50)  # Admin / Support Agent / User
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.role_name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    full_name = models.CharField(max_length=100, blank=True, null=True)
    public_name = models.CharField(max_length=100, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    pronouns = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.CharField(max_length=255, blank=True, null=True)
    avatar_color = models.CharField(max_length=50, default='#0052cc')
    header_color = models.CharField(max_length=50, default='#85b8ff')
    department = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default='Active')  # Active / Inactive
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def generate_verification_token(self):
        import uuid
        from django.utils import timezone
        self.email_verification_token = uuid.uuid4().hex
        self.email_verification_sent_at = timezone.now()
        self.save(update_fields=['email_verification_token', 'email_verification_sent_at'])
        return self.email_verification_token

    def __str__(self):
        return self.full_name or self.public_name or self.user.username


class TicketCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)  # Technical / Billing / Network etc.
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='Active')  # Active / Inactive

    class Meta:
        db_table = 'ticket_categories'
        verbose_name_plural = 'Ticket categories'

    def __str__(self):
        return self.category_name


class Priority(models.Model):
    priority_id = models.AutoField(primary_key=True)
    priority_name = models.CharField(max_length=50)  # Low / Medium / High / Critical
    response_time_hours = models.IntegerField(default=24)
    resolution_time_hours = models.IntegerField(default=48)

    class Meta:
        db_table = 'priorities'
        verbose_name_plural = 'Priorities'

    def __str__(self):
        return self.priority_name


class TicketStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=50)  # Open / In Progress / Resolved / Closed / To Do / Done
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'ticket_statuses'
        verbose_name_plural = 'Ticket statuses'
        ordering = ['order', 'status_id']

    def __str__(self):
        return self.status_name


from datetime import date, timedelta
from django.utils import timezone

class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    ticket_code = models.CharField(max_length=50, unique=True)  # e.g., KAN-1, KAN-2
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets')
    category = models.ForeignKey(TicketCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    status = models.ForeignKey(TicketStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tickets'
        indexes = [
            models.Index(fields=['status', 'assigned_to'], name='idx_ticket_status_assignee'),
            models.Index(fields=['updated_at'], name='idx_ticket_updated_at'),
            models.Index(fields=['created_at'], name='idx_ticket_created_at'),
            models.Index(fields=['due_date'], name='idx_ticket_due_date'),
            models.Index(fields=['status', 'due_date'], name='idx_ticket_status_due'),
        ]

    def __str__(self):
        return f"{self.ticket_code} - {self.subject}"

    @property
    def is_due_soon(self):
        """Returns True if due_date is set, ticket is not completed (Done/Resolved/Closed), and due_date is on or before tomorrow (due_date <= today + 1 day)."""
        if not self.due_date:
            return False
        if self.status and self.status.status_name in ['Done', 'Resolved', 'Closed']:
            return False
        today = timezone.now().date()
        return self.due_date <= (today + timedelta(days=1))



class TicketAssignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='made_assignments')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'ticket_assignments'

    def __str__(self):
        return f"Assignment {self.assignment_id} for Ticket {self.ticket.ticket_code}"


class TicketComment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    comment_text = models.TextField()
    is_internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        db_table = 'ticket_comments'

    def __str__(self):
        return f"Comment by {self.user.username} on {self.ticket.ticket_code}"


class TicketAttachment(models.Model):
    attachment_id = models.AutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attachments')
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ticket_attachments'

    def __str__(self):
        return self.file_name


class SLARule(models.Model):
    sla_id = models.AutoField(primary_key=True)
    priority = models.ForeignKey(Priority, on_delete=models.CASCADE, related_name='sla_rules')
    response_time = models.IntegerField(help_text="Response time in hours")
    resolution_time = models.IntegerField(help_text="Resolution time in hours")
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'sla_rules'

    def __str__(self):
        return f"SLA for {self.priority.priority_name}"


class TicketLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logs')
    action_type = models.CharField(max_length=100)  # Create / Update / Assign / Resolve
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ticket_logs'

    def __str__(self):
        return f"Log {self.log_id}: {self.action_type} on {self.ticket.ticket_code}"


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=150)
    message = models.TextField()
    notification_type = models.CharField(max_length=50)  # Assignment / Comment / Status
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"


class ServiceRating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    rating_score = models.IntegerField(help_text="Score 1-5")
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'service_ratings'

    def __str__(self):
        return f"Rating {self.rating_score}/5 for {self.ticket.ticket_code}"


class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    report_type = models.CharField(max_length=100)  # Ticket / SLA / Agent Performance
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'reports'

    def __str__(self):
        return f"Report {self.report_type} generated at {self.generated_at}"


class TeamSetting(models.Model):
    name = models.CharField(max_length=100, default='Team Vatana')
    icon_type = models.CharField(max_length=20, default='preset')  # 'preset', 'custom', 'initials'
    icon_value = models.CharField(max_length=255, default='mountains')  # preset key or uploaded file path
    icon_bg_color = models.CharField(max_length=50, default='#0052cc')
    description = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'team_settings'
        verbose_name = 'Team Setting'
        verbose_name_plural = 'Team Settings'

    @classmethod
    def get_settings(cls):
        setting, _ = cls.objects.get_or_create(id=1, defaults={
            'name': 'Team Vatana',
            'icon_type': 'preset',
            'icon_value': 'mountains',
            'icon_bg_color': '#0052cc'
        })
        return setting

    @property
    def ticket_prefix(self):
        import re
        trimmed = (self.name or '').strip()
        clean = re.sub(r'^(team\s+|space\s+)', '', trimmed, flags=re.IGNORECASE).strip()
        chars = re.sub(r'[^a-zA-Z0-9]', '', clean)
        if len(chars) < 2:
            chars = re.sub(r'[^a-zA-Z0-9]', '', trimmed)
        if len(chars) >= 3:
            return chars[:3].upper()
        elif chars:
            return chars.upper()
        return 'KAN'

    @property
    def initials(self):
        words = (self.name or 'TV').strip().split()
        if len(words) >= 2:
            return (words[0][0] + words[1][0]).upper()
        elif len(words) == 1 and len(words[0]) >= 2:
            return words[0][:2].upper()
        elif len(words) == 1 and len(words[0]) == 1:
            return words[0][0].upper()
        return 'TV'

    def __str__(self):
        return self.name
