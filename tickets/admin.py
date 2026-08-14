from django.contrib import admin
from .models import (
    Role, UserProfile, TicketCategory, Priority, TicketStatus,
    Ticket, TicketAssignment, TicketComment, TicketAttachment,
    SLARule, TicketLog, Notification, ServiceRating, Report
)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_id', 'role_name', 'description')
    search_fields = ('role_name',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role', 'full_name', 'phone', 'department', 'status', 'created_at')
    list_filter = ('role', 'status', 'department')
    search_fields = ('user__username', 'full_name', 'phone')

@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_name', 'status', 'description')
    list_filter = ('status',)

@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ('priority_id', 'priority_name', 'response_time_hours', 'resolution_time_hours')

@admin.register(TicketStatus)
class TicketStatusAdmin(admin.ModelAdmin):
    list_display = ('status_id', 'status_name', 'order', 'description')
    ordering = ('order',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_code', 'subject', 'user', 'category', 'priority', 'status', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('ticket_code', 'subject', 'description')

@admin.register(TicketAssignment)
class TicketAssignmentAdmin(admin.ModelAdmin):
    list_display = ('assignment_id', 'ticket', 'assigned_by', 'assigned_to', 'assigned_at')

@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ('comment_id', 'ticket', 'user', 'is_internal', 'created_at')
    list_filter = ('is_internal',)

@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ('attachment_id', 'ticket', 'uploaded_by', 'file_name', 'uploaded_at')

@admin.register(SLARule)
class SLARuleAdmin(admin.ModelAdmin):
    list_display = ('sla_id', 'priority', 'response_time', 'resolution_time')

@admin.register(TicketLog)
class TicketLogAdmin(admin.ModelAdmin):
    list_display = ('log_id', 'ticket', 'user', 'action_type', 'created_at')
    list_filter = ('action_type',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_id', 'user', 'ticket', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('is_read', 'notification_type')

@admin.register(ServiceRating)
class ServiceRatingAdmin(admin.ModelAdmin):
    list_display = ('rating_id', 'ticket', 'user', 'rating_score', 'created_at')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_id', 'report_type', 'generated_by', 'generated_at')
