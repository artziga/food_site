from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import models

from food.models import Profile


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.CharField(label='Email', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повторите пароль', widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.TextInput(attrs={'class': 'form-input'}))


class CollectDataForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        gender_choices = [(None, '-------'),
                          (True, 'Мужской'),
                          (False, 'Женский')]
        physical_activity_choice = [
            (1, 'Минимальные нагрузки (сидячая работа)'),
            (2, 'Необременительные тренировки 3 раза в неделю'),
            (3, 'Тренировки 5 раз в неделю (работа средней тяжести)'),
            (4, 'Интенсивные тренировки 5 раз в неделю'),
            (5, 'Ежедневные тренировки'),
            (6, 'Ежедневные интенсивные тренировки или занятия 2 раза в день'),
            (7, 'Тяжелая физическая работа или интенсивные тренировки 2 раза в день')
        ]
        self.fields['physical_activity'] = forms.IntegerField(
            label='Уровень физической активности',
            widget=forms.Select(choices=physical_activity_choice))
        self.fields['gender'] = forms.NullBooleanField(label='Пол', widget=forms.Select(choices=gender_choices))

    weight = forms.IntegerField(label='Вес')
    height = forms.IntegerField(label='Рост')
    basic_metabolism = forms.IntegerField(widget=forms.HiddenInput(), disabled=True, required=False)

    def clean(self):
        cleaned_data = super().clean()
        height = cleaned_data.get('height')
        weight = cleaned_data.get('weight')
        age = cleaned_data.get('age')
        man = cleaned_data.get('gender')

        """Расчет базового обмена веществ по формуле Маффина-Джеора:
        10 × вес в кг + 6.25 × рост в см - 5 × возраст в годах + 5  - для мужчин
        10 × вес в кг + 6.25 × рост в см - 5 × возраст в годах - 161  - для женщин"""
        basic_metabolism_value = 10 * weight + 6.25 * (height - 5) - 5 * age
        if man:
            basic_metabolism_value += 5
        else:
            basic_metabolism_value -= 161
        cleaned_data['basic_metabolism'] = basic_metabolism_value
        return cleaned_data

    class Meta:
        model = Profile
        fields = ['age', 'gender', 'weight', 'height', 'physical_activity']


class MenuGenerateForm(forms.Form):
    generate_menu = forms.BooleanField(required=False, widget=forms.HiddenInput(), initial=True)