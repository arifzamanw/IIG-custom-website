from django.contrib import admin

from .models import Job, JobApplication

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'created_at', 'is_active']
    search_fields = ['title', 'location']

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['job', 'name', 'email', 'phone', 'created_at']
    search_fields = ['name', 'email', 'job__title']
