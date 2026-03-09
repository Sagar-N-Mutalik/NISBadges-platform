from django.urls import path
from . import views

urlpatterns = [
    path('referrals/process/', views.process_referrals, name='process_referrals'),
]