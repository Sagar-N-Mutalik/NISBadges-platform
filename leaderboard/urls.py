from django.urls import path
from . import views

urlpatterns = [
    path('referrals/process/', views.process_referrals, name='process_referrals'),
    path('', views.view_leaderboard, name='view_leaderboard'),
    path('badges/eligibility/', views.badge_eligibility, name='badge_eligibility'),
    path('badges/assign/', views.assign_badges, name='assign_badges'),
    path('badges/export/', views.export_badges_csv, name='export_badges_csv'),
]