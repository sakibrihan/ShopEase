import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .forms import RegistrationForm, OTPForm, PasswordResetRequestForm, SetNewPasswordForm
from .models import OTP, RegistrationNotification, PasswordResetToken


def generate_otp():
    """Generate a random 6-digit OTP."""
    return str(random.randint(100000, 999999))


def notify_admin_new_registration(user):
    """Send email to admin about new user registration and store in DB."""
    # Store notification in DB
    notification, created = RegistrationNotification.objects.get_or_create(
        user=user,
        defaults={
            'username': user.username,
            'email': user.email,
        }
    )

    # Send email to admin
    subject = f'🎉 New User Registered - {user.username} | ShopEase'
    message = f"""
Hello Admin,

A new user has just registered on ShopEase!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NEW USER DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  👤 Username:  {user.username}
  📧 Email:     {user.email}
  📅 Joined:    {timezone.now().strftime('%B %d, %Y at %I:%M %p')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This user has been successfully verified and added to our portal.

Best regards,
ShopEase System
"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        notification.admin_notified = True
        notification.save()
        print(f'\n{"="*50}')
        print(f'  ✅ Admin notification email sent for: {user.username}')
        print(f'{"="*50}\n')
    except Exception as e:
        print(f'\n{"="*50}')
        print(f'  ⚠️ Failed to send admin email: {e}')
        print(f'{"="*50}\n')


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

                    # Notify admin about new registration
                    notify_admin_new_registration(user)

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


# ============================================
# PASSWORD RESET VIEWS
# ============================================

def password_reset_request(request):
    """Request a password reset by entering email."""
    if request.user.is_authenticated:
        return redirect('products:home')

    demo_reset_link = None

    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email, is_active=True)

            # Invalidate any existing unused tokens
            PasswordResetToken.objects.filter(user=user, used=False).update(used=True)

            # Create new token
            token_obj = PasswordResetToken(user=user)
            token_obj.save()

            # Build the reset link
            reset_url = request.build_absolute_uri(f'/accounts/password-reset/confirm/{token_obj.token}/')

            # Send reset email to the user
            subject = '🔑 Password Reset - ShopEase'
            message = f"""
Hello {user.username},

We received a request to reset your password for your ShopEase account.

Click the link below to set a new password:
{reset_url}

This link will expire in 1 hour.

If you did not request this, please ignore this email.

Best regards,
ShopEase Team
"""
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f'  ⚠️ Failed to send reset email: {e}')

            # For demo: show the link on the page
            demo_reset_link = reset_url

            print(f'\n{"="*50}')
            print(f'  PASSWORD RESET for {user.username}')
            print(f'  Link: {reset_url}')
            print(f'{"="*50}\n')

            messages.success(request, 'Password reset link has been generated!')
            return render(request, 'accounts/password_reset_email_sent.html', {
                'demo_reset_link': demo_reset_link,
                'email': email,
            })
    else:
        form = PasswordResetRequestForm()

    return render(request, 'accounts/password_reset_request.html', {'form': form})


def password_reset_confirm(request, token):
    """Validate token and allow user to set a new password."""
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('accounts:password_reset')

    if not token_obj.is_valid:
        messages.error(request, 'This reset link has expired or already been used. Please request a new one.')
        return redirect('accounts:password_reset')

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user = token_obj.user
            user.set_password(form.cleaned_data['new_password1'])
            user.save()

            # Mark token as used
            token_obj.used = True
            token_obj.save()

            messages.success(request, 'Your password has been reset successfully! You can now log in.')
            return redirect('accounts:password_reset_complete')
    else:
        form = SetNewPasswordForm()

    return render(request, 'accounts/password_reset_confirm.html', {
        'form': form,
        'token': token,
    })


def password_reset_complete(request):
    """Password reset success page."""
    return render(request, 'accounts/password_reset_complete.html')
