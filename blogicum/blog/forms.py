from django import forms

from .models import Post, Comment, User


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['author']
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=True,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=(
            '''Ваш пароль не должен быть слишком похож
            на другую вашу личную информацию.'''
            '''Ваш пароль должен содержать как минимум 8 символов.'''
            '''Пароль не может состоять только из цифр.'''
        ))
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Для подтверждения введите пароль еще раз.'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name',
                  'last_name', 'email', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password1 = self.cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if (password1 and password2 and password1 != password2):
            self.add_error('password2', 'Пароли не совпадают.')


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name',
                  'last_name', 'email']
