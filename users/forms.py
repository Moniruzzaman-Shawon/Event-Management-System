from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'w-full border-b-2 border-gray-300 focus:border-blue-500 px-1 py-3 transition-all'
        }),
    )
    
    phone_number = forms.CharField(
        required=False,
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your phone number',
            'class': 'w-full border-b-2 border-gray-300 focus:border-blue-500 px-1 py-3 transition-all'
        }),
    )

    profile_picture = forms.ImageField(
        required=False,
        label="Profile Picture",
    )

    class Meta:
        model = User  
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "profile_picture",
            "password1",
            "password2",
        ]

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'profile_picture')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your username',
            'class': 'w-full border-b-2 border-gray-300 focus:border-blue-500 px-1 py-3 transition-all',
            'autofocus': True,
        }),
        label="Username"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'w-full border-b-2 border-gray-300 focus:border-blue-500 px-1 py-3 transition-all',
        }),
        label="Password"
    )
