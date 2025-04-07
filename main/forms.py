from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import HelpRequest

class SignUpForm(UserCreationForm):
    class Meta:
        model = get_user_model()  # Используем кастомную модель пользователя
        fields = ('username', 'password1', 'password2')

#class SignUpForm(UserCreationForm):
#    username = forms.CharField(max_length=50)
#    password1 = forms.CharField(widget=forms.PasswordInput)
#    password2 = forms.CharField(widget=forms.PasswordInput)
 #   class Meta:
  #      model = User
   #     fields = ('username', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()  # Используем кастомную модель пользователя
        fields = ['username', 'email', 'avatar', 'city', 'phone_number', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class HelpRequestForm(forms.ModelForm):
    class Meta:
        model = HelpRequest
        fields = ['title', 'description', 'location']