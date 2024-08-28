from .models import User, generate_otp
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from general.forms import UserLoginForm

"""
    user accounting functions that consist login and logout
"""


def user_login(request):
    if request.user.is_authenticated:
        return redirect('/')

    next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        if next:
            return redirect(next)
        return redirect('core:home')

    context = {
        'form': form,
    }

    return render(request, 'auth/login.html', context)


def user_logout(request):
    try:
        logout(request)
        return redirect('login')
    except:
        return render(request, 'auth/login.html')


def login_otp(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        email = request.POST.get('email-otp')
        otp = request.POST.get('otp')
        user = User.objects.get(email=email)

        if user.otp == otp:
            login(request, user)
            Otp = generate_otp()
            User.objects.filter(email=email).update(otp=Otp)
        return redirect('core:home')


    return render(request, 'auth/otp.html')