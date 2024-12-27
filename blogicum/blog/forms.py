from django import forms
from .models import Post, Comment, UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        # Указываем модель, на основе которой должна строиться форма.
        model = Post
        # Указываем, что надо отобразить все поля.
        fields = '__all__'
        exclude = ["comment"]

        class Meta:
            widgets = {
                'pub_date': forms.DateInput(attrs={'type': 'date'})
            }


class ProfileForm(forms.ModelForm):
    class Meta:
        # Указываем модель, на основе которой должна строиться форма.
        model = UserProfile
        # Указываем, что надо отобразить все поля.
        fields = '__all__'


class CommentForm(forms.ModelForm):
    class Meta:
        # Указываем модель, на основе которой должна строиться форма.
        model = Comment
        # Указываем, что надо отобразить все поля.
        fields = '__all__'


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirmation = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'first_name',
                  'last_name', 'email', 'password', 'password_confirmation']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'
