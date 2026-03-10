"""
URL configuration for nisbadges_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

admin.site.site_header = "NISBadges Admin Portal"
admin.site.site_title = "NISBadges System"
admin.site.index_title = "Platform Management"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core_accounts.urls')),         # Login and authentication flow
    path('dashboard/', include('members.urls')), # Members database
    path('events/', include('events.urls')),     # Event management & attendance
    path('leaderboard/', include('leaderboard.urls')), # Rankings & badge eligibility
    path('', RedirectView.as_view(pattern_name='dashboard_home', permanent=False), name='root_index'),
]
