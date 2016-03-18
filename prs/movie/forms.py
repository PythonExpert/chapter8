from django import forms
from django.contrib.auth.models import User
from movie.models import UserProfile

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('externalUserId', 'nationality',
                  'living_country', 'living_city',
                  'martialstatus', 'hobby', 'eating_habits',
                  'gender', 'age')

