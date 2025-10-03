from django.contrib import admin
from .models import TaskAssignment, TaskUpdate, Notification

@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ['request', 'assigned_to', 'status', 'priority', 'assigned_at']
    list_filter = ['status', 'priority', 'assigned_at']
    search_fields = ['request__ticket_number', 'assigned_to__username']
    readonly_fields = ['assigned_at', 'accepted_at', 'started_at', 'actual_completion']

@admin.register(TaskUpdate)
class TaskUpdateAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'updated_by', 'progress_percentage', 'created_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__username']
    readonly_fields = ['created_at']