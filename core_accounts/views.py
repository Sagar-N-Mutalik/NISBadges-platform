from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_home')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard_home')
        else:
            messages.error(request, 'Invalid email or password.')
            
    return render(request, 'core_accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
