from django.contrib import admin
from .models import Report, CitizenSatisfaction

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'generated_by', 'date_from', 'date_to', 'created_at']
    list_filter = ['report_type', 'created_at']
    search_fields = ['title']
    readonly_fields = ['created_at']

@admin.register(CitizenSatisfaction)
class CitizenSatisfactionAdmin(admin.ModelAdmin):
    list_display = ['request', 'rating', 'response_time_rating', 'quality_rating', 'created_at']
    list_filter = ['rating', 'would_recommend', 'created_at']
    search_fields = ['request__ticket_number', 'comments']
    readonly_fields = ['created_at']