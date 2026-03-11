from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_leaderboard, name='view_leaderboard'),
    path('update-referral/<str:ieee_number>/', views.update_manual_referral, name='update_manual_referral'),
    path('badges/eligibility/', views.badge_eligibility, name='badge_eligibility'),
    path('badges/assign/', views.assign_badges, name='assign_badges'),
    path('badges/export/', views.export_badges_csv, name='export_badges_csv'),
]
