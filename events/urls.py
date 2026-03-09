from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_event, name='create_event'),
    path('list/', views.event_list, name='event_list'),
    path('attendance/upload/', views.upload_attendance, name='upload_attendance'),
]