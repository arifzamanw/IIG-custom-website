from django.urls import path
from . import views

urlpatterns = [
    path('', views.career_page, name='career_page'),
    path('apply/<int:job_id>/', views.apply_for_job, name='apply_for_job'),
    path('success/', views.job_application_success, name='job_application_success'),
]
