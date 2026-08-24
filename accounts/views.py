import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .forms import RegistrationForm, OTPForm
from .models import OTP


def generate_otp():
    """Generate a random 6-digit OTP."""
    return str(random.randint(100000, 999999))


def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Inactive until OTP verified
            user.save()

            # Generate and store OTP
            otp_code = generate_otp()
            OTP.objects.create(
                user=user,
                otp=otp_code,
                expires_at=timezone.now() + timedelta(minutes=5),
            )

            # Print OTP to console (for demo/development)
            print(f'\n{"="*50}')
            print(f'  DEMO OTP for {user.username}: {otp_code}')
            print(f'{"="*50}\n')

            # Store user id in session for OTP verification
            request.session['otp_user_id'] = user.id
            request.session['demo_otp'] = otp_code  # For showing on page

            messages.success(request, 'Registration successful! Please verify your account with the OTP.')
            return redirect('accounts:verify_otp')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def verify_otp(request):
    """OTP verification view."""
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, 'No pending OTP verification. Please register first.')
        return redirect('accounts:register')

    demo_otp = request.session.get('demo_otp', '')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            try:
                from django.contrib.auth.models import User
                user = User.objects.get(id=user_id)
                otp_obj = OTP.objects.get(user=user)

                # Check attempts
                if otp_obj.attempts >= 5:
                    messages.error(request, 'Too many failed attempts. Please request a new OTP.')
                    return render(request, 'accounts/verify_otp.html', {
                        'form': form, 'demo_otp': demo_otp,
                    })

                # Check expiry
                if otp_obj.is_expired:
                    messages.error(request, 'OTP has expired. Please request a new one.')
                    return render(request, 'accounts/verify_otp.html', {
                        'form': form, 'demo_otp': demo_otp,
                    })

                # Validate OTP
                if entered_otp == otp_obj.otp:
                    otp_obj.verified = True
                    otp_obj.save()
                    user.is_active = True
                    user.save()

                    # Clean up session
                    del request.session['otp_user_id']
                    if 'demo_otp' in request.session:
                        del request.session['demo_otp']

                    messages.success(request, 'Account verified successfully! You can now log in.')
                    return redirect('accounts:login')
                else:
                    otp_obj.attempts += 1
                    otp_obj.save()
                    remaining = 5 - otp_obj.attempts
                    messages.error(request, f'Invalid OTP. {remaining} attempts remaining.')

            except (OTP.DoesNotExist, Exception):
                messages.error(request, 'OTP verification failed. Please try again.')
    else:
        form = OTPForm()

    return render(request, 'accounts/verify_otp.html', {
        'form': form,
        'demo_otp': demo_otp,
    })


def resend_otp(request):
    """Resend a new OTP."""
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, 'No pending verification. Please register first.')
        return redirect('accounts:register')

    try:
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)
        otp_code = generate_otp()

        otp_obj, created = OTP.objects.update_or_create(
            user=user,
            defaults={
                'otp': otp_code,
                'expires_at': timezone.now() + timedelta(minutes=5),
                'attempts': 0,
                'verified': False,
            }
        )

        request.session['demo_otp'] = otp_code

        print(f'\n{"="*50}')
        print(f'  DEMO OTP (resent) for {user.username}: {otp_code}')
        print(f'{"="*50}\n')

        messages.success(request, 'A new OTP has been generated.')
    except Exception:
        messages.error(request, 'Failed to resend OTP. Please try again.')

    return redirect('accounts:verify_otp')


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'products:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    """User logout view."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('products:home')


@login_required
def profile(request):
    """User profile page."""
    return render(request, 'accounts/profile.html')
