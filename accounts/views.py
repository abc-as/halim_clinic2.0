# views.py
from django.http import JsonResponse
from .utils import generate_jwt_token,send_otp_in_background,send_otp_via_whatsapp
from .decorators import auth_check
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserRegistrationForm, LoginForm, ProfileForm
from children.forms import ChildForm
from children.models import Child
from .models import CustomUser, Profile
from django.views import View
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from datetime import timezone


def send_otp(request):
    phone_number = request.POST.get('phone_number')
    otp = send_otp_in_background(phone_number)
    request.session['otp'] = otp

    return JsonResponse({'message': 'OTP sent successfully'})


@csrf_exempt
@auth_check
def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            request.session['registration_data'] = form.cleaned_data
            phone_number = form.cleaned_data['phone_number']
            otp = send_otp_via_whatsapp(phone_number)
            request.session['otp'] = otp

            messages.success(request, f'OTP sent to {phone_number}. Please verify to complete registration.')
            request.session['phone_number'] = phone_number
            return redirect('verify_otp_login')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})




def verify_otp(request):
    if request.method == 'POST':
        input_otp = request.POST.get('otp')
        saved_otp = request.session.get('otp')

        if input_otp == str(saved_otp):
            registration_data = request.session.get('registration_data')
            form = CustomUserRegistrationForm(registration_data)
            if form.is_valid():
                user = form.save()
                token = generate_jwt_token(user)
                response = redirect('profile')
                response.set_cookie('jwt_token', token, httponly=True, secure=True)
                del request.session['otp']
                del request.session['registration_data']

                messages.success(request, 'Registration successful!')
                request.session['user_id'] = user.id
                return response
            else:
                messages.error(request, 'Form data is invalid. Please try again.')
                return redirect('register')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('verify_otp')

    return render(request, 'accounts/verify_otp.html')

@csrf_exempt
@auth_check
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            phone_number = None
            if identifier:
                if len(identifier) != 12:
                    try:
                        user = CustomUser.objects.get(id_number=identifier)
                        phone_number = user.phone_number

                    except CustomUser.DoesNotExist:
                        messages.error(request, 'UAE ID not found.')
                        return render(request, 'accounts/login.html', {'form': form})
                else:
                    # Assume it's a phone number
                    try:
                        user = CustomUser.objects.get(phone_number=identifier)
                        phone_number = user.phone_number
                    except CustomUser.DoesNotExist:
                        messages.error(request, 'Phone number not found.')
                        return render(request, 'accounts/login.html', {'form': form})
            else:
                messages.error(request, 'Invalid identifier format.')
                return render(request, 'accounts/login.html', {'form': form})

            # Send OTP
            otp = send_otp_via_whatsapp(phone_number)
            request.session['otp'] = otp
            request.session['phone_number'] = phone_number

            return redirect('verify_otp_login')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def verify_otp_login(request):
    if request.method == 'POST':
        otp_fields = [request.POST.get(f'otp{i+1}') for i in range(6)]
        input_otp = ''.join(otp_fields)
        saved_otp = request.session.get('otp')
        phone_number = request.session.get('phone_number')
        print(saved_otp, '=============================')
        print(input_otp, '-----')

        if input_otp == str(saved_otp):
            registration_data = request.session.get('registration_data')
            if registration_data:
                form = CustomUserRegistrationForm(registration_data)
                if form.is_valid():
                    user = form.save()
                    token = generate_jwt_token(user)
                    response = redirect('profile')
                    response.set_cookie('jwt_token', token, httponly=True, secure=True)
                    del request.session['otp']
                    del request.session['registration_data']

                    messages.success(request, 'Registration successful!')
                    request.session['user_id'] = user.id
                else:
                    messages.error(request, 'Form data is invalid. Please try again.')
                    return redirect('register')
            # Authenticate the user using the phone number and OTP
            user = authenticate(request, phone_number=phone_number)
            
            if user:
                # Log the user in
                auth_login(request, user)
                messages.success(request, 'Logged in successfully!')
                return redirect('/')
            else:
                messages.error(request, 'User authentication failed.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid OTP')

    return render(request, 'accounts/login_verify_otp.html')




class CreateProfileView(View):
    def get(self, request):
        form = ProfileForm()
        return render(request, 'accounts/create_profile.html', {'form': form})

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_id = request.session.get('user_id')
            if not user_id:
                return redirect('login')

            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return redirect('login')
            Profile.objects.create(user=user, **form.cleaned_data)
            return redirect('profile')

        return render(request, 'accounts/create_profile.html', {'form': form})


class ProfileView(View):

    def get(self, request):
        user_id = request.user.id
        if not user_id:
            return redirect('login')
        profile = Profile.objects.filter(user=user_id).first()
        print(profile, '=============')
        if not profile:
            return redirect('create_profile')
        return render(request, 'accounts/profile.html', {'profile': profile})


class EditProfileView(View):
    def get(self, request):
        user_id = request.user.id
        if not user_id:
            return redirect('login')
        try:
            profile = Profile.objects.get(user=user_id)
        except Profile.DoesNotExist:
            raise Http404("Profile does not exist")
        form = ProfileForm(instance=profile)
        return render(request, 'accounts/edit_profile.html', {'form': form})

    def post(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')  # Redirect to login if user_id is not in session
        try:
            profile = Profile.objects.get(user=user_id)
        except Profile.DoesNotExist:
            raise Http404("Profile does not exist")
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, 'accounts/edit_profile.html', {'form': form})

def HomeView(request):
    if request.method == 'POST':
        form = ChildForm(request.POST, request.FILES, user=request.user)  # Pass the user
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ChildForm()
    if request.user.is_authenticated:
        children = Child.objects.filter(parent=request.user)
    else:
        children = Child.objects.none()

    return render(request, 'home.html', {'children': children, "form":form})


def logout_user(request):
    logout(request)
    return redirect('login')


def about(request):
    return render(request, 'about.html')