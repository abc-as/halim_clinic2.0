from django import forms
from .models import CustomUser, Profile
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class CustomUserRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'id_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'required': True}),
            'last_name': forms.TextInput(attrs={'required': True}),
            'phone_number': forms.TextInput(attrs={'required': True}),
            'id_number': forms.TextInput(attrs={'required': True}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Ensure the phone number is numeric and starts with '91'
            if not phone_number.isdigit():
                self.add_error('phone_number', 'Phone number must contain only digits.')
            if not phone_number.startswith('91'):
                phone_number = '91' + phone_number

            # Ensure the phone number is of a valid length (e.g., 12 digits with country code)
            if len(phone_number) != 12:
                self.add_error('phone_number', 'Phone number must be 10 digits long, excluding the country code.')
        return phone_number

    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if id_number:
            # Ensure the ID number is alphanumeric and meets a length requirement (e.g., 18 characters)
            if not id_number.isalnum():
                self.add_error('id_number', 'ID number must contain only alphanumeric characters.')
            if len(id_number) != 18:
                self.add_error('id_number', 'ID number must be exactly 18 characters long.')
        return id_number

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        id_number = cleaned_data.get('id_number')

        # Check if phone number already exists
        if phone_number and CustomUser.objects.filter(phone_number=phone_number).exists():
            self.add_error('phone_number', 'Phone number already exists. Try logging in.')

        # Check if ID number already exists
        if id_number and CustomUser.objects.filter(id_number=id_number).exists():
            self.add_error('id_number', 'ID number already exists. Try logging in.')

        # Ensure all fields are filled
        if not all([cleaned_data.get(field) for field in self._meta.fields]):
            self.add_error(None, 'All fields are required.')

        return cleaned_data

class LoginForm(forms.Form):
    identifier = forms.CharField(
        max_length=18,
        label='Enter UAE ID or Phone Number',
        required=True,
        error_messages={
            'required': 'This field cannot be empty.',
        }
    )

    def clean_identifier(self):
        identifier = self.cleaned_data.get('identifier')

        # Check if the identifier is either a phone number or id_number
        user_exists = CustomUser.objects.filter(phone_number=identifier).exists() or CustomUser.objects.filter(id_number=identifier).exists()
        if not user_exists:
            raise ValidationError('This phone number or UAE ID is not registered with us.')

        return identifier

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'gender', 'address', 'profile_picture', 'bio']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
