from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from .models import *


class RegisterCustomUserForm(UserCreationForm):
    username = forms.CharField(label='username', widget=forms.TextInput(attrs={'class': 'input__nickname', 'placeholder': 'input username...'}))
    email = forms.EmailField(label='email', widget=forms.EmailInput(attrs={'class': 'input__mail', 'placeholder': 'input email...'}))
    password1 = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class': 'input__password', 'placeholder': 'input password...'}))
    password2 = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class': 'input__password', 'placeholder': 'repeat password...'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']


class LoginCustomUserForm(AuthenticationForm):
    password = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class': 'input__password',
                                                                                   'placeholder': 'input password...'}))
    username = forms.CharField(label='username', widget=forms.TextInput(attrs={'class': 'input__nickname',
                                                                               'placeholder': 'input username...'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'password']


class ChangeCustomUserDescriptionForm(forms.ModelForm):
    class Meta:
        model = UserDescription
        fields = ['sex', 'political_orientation', 'art_style', 'ideology', 'credo', 'description']
        widgets = {
            'ideology': forms.Textarea(attrs={'cols': 60, 'rows': 1, 'class': 'form_textarea'}),
            'credo': forms.Textarea(attrs={'cols': 60, 'rows': 5, 'class': 'form_textarea'}),
            'description': forms.Textarea(attrs={'cols': 60, 'rows': 10, 'class': 'form_textarea'})
        }


class ChangeCustomUserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form_input'}),
            'avatar': forms.FileInput(attrs={'class': 'form_file'})
        }


class ChangeCustomUserPasswordForm(SetPasswordForm):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput(attrs={'class': 'form_input'}))
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'class': 'form_input'}))
    new_password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput(attrs={'class': 'form_input'}))

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 != new_password2:
            raise forms.ValidationError("The two password fields didn't match1.")
        user = self.user
        if not user.check_password(old_password):
            raise forms.ValidationError("Your old password was entered incorrectly.")
        return cleaned_data

    class Meta:
        model = get_user_model()
        fields = ['old_password', 'new_password1', 'new_password2']
        widgets = {
            'old_password': forms.PasswordInput(attrs={'class': 'form_input'}),
            'new_password1': forms.PasswordInput(attrs={'class': 'form_input'}),
            'new_password2': forms.PasswordInput(attrs={'class': 'form_input'})
        }


class CreateDiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['visibility', 'aviability_lvl', 'theme', 'content']
        widgets = {
            'theme': forms.Textarea(attrs={'cols': 60, 'rows': 1, 'class': 'form_textarea'}),
            'content': forms.Textarea(attrs={'cols': 60, 'rows': 10, 'class': 'form_textarea'})
        }
