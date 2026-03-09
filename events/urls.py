from django.urls import path
from . import views

urlpatterns = [
    path('attendance/upload/', views.upload_attendance, name='upload_attendance'),
]