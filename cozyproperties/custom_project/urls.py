from django.urls import path
from custom_project.views import *


app_name = 'custom_project'
urlpatterns = [
    path('', gallery, name='gallery'),
    path('project/<int:project_id>', project, name='project'),
]
