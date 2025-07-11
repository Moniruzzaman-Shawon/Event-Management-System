from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'w-full border-b-2 border-gray-300 focus:border-blue-500 px-1 py-3 transition-all'
        }),
    )
    first_name = forms.CharField(
        required=True,
        label="First Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your first name',
            'class': 'w-full border-b-2 border-gray-300 focus:border-blue-500 px-1 py-3 transition-all'
        }),
    )
    last_name = forms.CharField(
        required=True,
        label="Last Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your last name',
            'class': 'w-full border-b-2 border-gray-300 focus:border-blue-500 px-1 py-3 transition-all'
        }),
    )
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your username',
            'class': 'w-full border-b-2 border-gray-300 focus:border-blue-500 px-1 py-3 transition-all'
        }),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'w-full border-b-2 border-gray-300 focus:border-blue-500 px-1 py-3 transition-all'
        }),
        help_text="",  
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password',
            'class': 'w-full border-b-2 border-gray-300 focus:border-blue-500 px-1 py-3 transition-all'
        }),
        help_text="",  
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username


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
