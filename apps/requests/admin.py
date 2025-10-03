from django.contrib import admin
from .models import ServiceType, ServiceArea, ServiceRequest, RequestImage, RequestComment, RequestStatusHistory

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_class', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']

@admin.register(ServiceArea)
class ServiceAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']

class RequestImageInline(admin.TabularInline):
    model = RequestImage
    extra = 0
    readonly_fields = ['uploaded_by', 'uploaded_at']

class RequestCommentInline(admin.TabularInline):
    model = RequestComment
    extra = 0
    readonly_fields = ['user', 'created_at']

class RequestStatusHistoryInline(admin.TabularInline):
    model = RequestStatusHistory
    extra = 0
    readonly_fields = ['from_status', 'to_status', 'changed_by', 'created_at']

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_number', 'title', 'citizen', 'service_type', 
        'status', 'priority', 'created_at', 'assigned_to'
    ]
    list_filter = [
        'status', 'priority', 'request_type', 'service_type', 
        'service_area', 'created_at'
    ]
    search_fields = [
        'ticket_number', 'title', 'description', 
        'citizen__username', 'citizen__email'
    ]
    readonly_fields = ['ticket_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('ticket_number', 'citizen', 'service_type', 'service_area')
        }),
        ('Detalles de la Solicitud', {
            'fields': ('request_type', 'title', 'description', 'address', 'priority')
        }),
        ('Estado y Asignación', {
            'fields': ('status', 'assigned_to', 'reviewed_by')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'expected_completion', 'completed_at')
        }),
        ('Contacto', {
            'fields': ('citizen_phone', 'citizen_email')
        }),
        ('Costos', {
            'fields': ('estimated_cost', 'actual_cost')
        }),
        ('Ubicación', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': ('notes',)
        })
    )
    
    inlines = [RequestImageInline, RequestCommentInline, RequestStatusHistoryInline]

@admin.register(RequestImage)
class RequestImageAdmin(admin.ModelAdmin):
    list_display = ['request', 'description', 'is_before', 'uploaded_by', 'uploaded_at']
    list_filter = ['is_before', 'uploaded_at']
    search_fields = ['request__ticket_number', 'description']
    readonly_fields = ['uploaded_by', 'uploaded_at']

@admin.register(RequestComment)
class RequestCommentAdmin(admin.ModelAdmin):
    list_display = ['request', 'user', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['request__ticket_number', 'comment', 'user__username']
    readonly_fields = ['user', 'created_at']

@admin.register(RequestStatusHistory)
class RequestStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['request', 'from_status', 'to_status', 'changed_by', 'created_at']
    list_filter = ['from_status', 'to_status', 'created_at']
    search_fields = ['request__ticket_number', 'reason']
    readonly_fields = ['request', 'from_status', 'to_status', 'changed_by', 'created_at']