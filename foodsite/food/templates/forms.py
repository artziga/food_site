from django import forms
from django.forms.models import modelformset_factory

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Min, Max, Q

from food.models import *


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
    # weight = forms.IntegerField(label='Вес')
    # height = forms.IntegerField(label='Рост')
    # basic_metabolism = forms.IntegerField(label='', widget=forms.HiddenInput(), disabled=True, required=False)

    def clean(self):
        cleaned_data = super().clean()
        age = cleaned_data.get('age')
        height = cleaned_data.get('height')
        weight = cleaned_data.get('weight')
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


class AddIngredientForm(forms.ModelForm):
    ingredient_name = forms.CharField(
        label='Ингредиент',
        error_messages={
            'unique': 'Данный ингредиент скоро будет добавлен, попробуйте проверить его позже'
        })

    class Meta:
        model = Ingredient
        fields = ['ingredient_name', 'protein_value', 'fats_value', 'carbohydrates_value', 'energy_value']


class AddForm(forms.ModelForm):
    class Meta:
        model = UserIngredient
        fields = ['add_to_common']


class AddDishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = '__all__'


class AddRecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        exclude = ('dish',)


RecipeFormSet = modelformset_factory(
    Recipe,
    form=AddRecipeForm,
    extra=6
)


class FilterForm(forms.Form):
    limits = Dish.objects.aggregate(
        min_calories=Min('calories'),
        max_calories=Max('calories'),
        min_active_cooking_time=Min('active_cooking_time'),
        max_active_cooking_time=Max('active_cooking_time'),
        min_total_cooking_time=Min('total_cooking_time'),
        max_total_cooking_time=Max('total_cooking_time')
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Meal.objects.all(),
        required=False,
        label='Категории',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-style checkbox-group'}),
        to_field_name='slug'

    )
    min_cal = forms.IntegerField(
        required=False,
        label='Минимальное число калорий',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': f"От {limits['min_calories']}"})
    )

    max_cal = forms.IntegerField(
        required=False,
        label='Максимальное число калорий',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': f"До {limits['max_calories']}"})
    )
    min_a_time = forms.IntegerField(
        required=False,
        label='Минимальное активное время готовки',
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': f"От {limits['min_active_cooking_time']}"})
    )
    max_a_time = forms.IntegerField(
        required=False,
        label='Максимальное активное время готовки',
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': f"До {limits['max_active_cooking_time']}"})
    )
    min_t_time = forms.IntegerField(
        required=False,
        label='Минимальное полное время готовки',
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': f"От {limits['min_total_cooking_time']}"})
    )
    max_t_time = forms.IntegerField(
        required=False,
        label='Максимальное полное время готовки',
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': f"До {limits['max_total_cooking_time']}"})
    )

    def get_query_params(self):
        query_params = {}
        for key, value in self.cleaned_data.items():
            if value:
                query_params[key] = value
        return query_params

    def filter(self, queryset, user):
        # queryset = queryset.filter(Q(user__isnull=True) | Q(user=user))
        filters = {}
        selected_categories = self.cleaned_data.get('categories')
        ingredient = self.cleaned_data.get('ingredient')
        min_calories = self.cleaned_data.get('min_cal')
        max_calories = self.cleaned_data.get('max_cal')
        min_active_cooking_time = self.cleaned_data.get('min_a_time')
        max_active_cooking_time = self.cleaned_data.get('max_a_time')
        min_total_cooking_time = self.cleaned_data.get('min_t_time')
        max_total_cooking_time = self.cleaned_data.get('max_t_time')
        if selected_categories:
            filters['tags__meal__in'] = selected_categories
        if ingredient:
            filters['recipe__'] = selected_categories
        if min_calories:
            filters['calories__gte'] = min_calories
        if max_calories:
            filters['calories__lte'] = max_calories
        if min_active_cooking_time:
            filters['active_cooking_time__gte'] = min_active_cooking_time
        if max_active_cooking_time:
            filters['active_cooking_time__lte'] = max_active_cooking_time
        if min_total_cooking_time:
            filters['total_cooking_time__gte'] = min_total_cooking_time
        if max_total_cooking_time:
            filters['total_cooking_time__lte'] = max_total_cooking_time
        queryset = queryset.filter(**filters).distinct()
        return queryset
