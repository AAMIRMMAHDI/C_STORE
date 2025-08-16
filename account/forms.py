from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
import re

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="ایمیل یا شماره موبایل",
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': True})
    )
    password = forms.CharField(
        label="کلمه عبور",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True})
    )

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        label="نام",
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': True})
    )
    last_name = forms.CharField(
        label="نام خانوادگی",
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': True})
    )
    email = forms.EmailField(
        label="ایمیل (اختیاری)",
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        label="شماره موبایل",
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': True})
    )
    password1 = forms.CharField(
        label="کلمه عبور",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True})
    )
    password2 = forms.CharField(
        label="تکرار کلمه عبور",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^09\d{9}$', username):
            raise forms.ValidationError('شماره موبایل باید ۱۱ رقمی باشد و با ۰۹ شروع شود.')
        return username

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^09\d{9}$', username):
            raise forms.ValidationError('شماره موبایل باید ۱۱ رقمی باشد و با ۰۹ شروع شود.')
        return username

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="کلمه عبور فعلی",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True})
    )
    new_password1 = forms.CharField(
        label="کلمه عبور جدید",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True})
    )
    new_password2 = forms.CharField(
        label="تکرار کلمه عبور جدید",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True})
    )