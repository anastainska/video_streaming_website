from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import Subscriber


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required. Add a valid email address')

    class Meta:
        model = Subscriber
        fields = ("email", "username", "password1", "password2")


class UserAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = Subscriber
        fields = ("email", "password")

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Invalid login")


class AccountUpdateForm(forms.ModelForm):

    class Meta:
        model = Subscriber
        fields = ('email', 'username', 'date_of_birth')

    def clean_email(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            try:
                account = Subscriber.objects.exclude(pk=self.instance.pk).get(email=email)
            except Subscriber.DoesNotExist:
                return email
            raise forms.ValidationError('Email "%s" is already in use.' % account)

    def clean_username(self):
        if self.is_valid():
            username = self.cleaned_data['username']
            try:
                account = Subscriber.objects.exclude(pk=self.instance.pk).get(username=username)
            except Subscriber.DoesNotExist:
                return username
            raise forms.ValidationError('Username "%s" is already in use.' % account.username)
