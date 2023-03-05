from django import forms
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from food.services.create_menu import get_set_of_dish, get_daily_menu
import random

from .models import *
from django.views.generic import ListView, CreateView

from .templates.forms import RegisterUserForm, LoginUserForm, CollectDataForm, MenuGenerateForm
from .templates.utils import DataMixin

days = {
    'monday': 'Понедельник',
    'tuesday': 'Вторник',
    'wednesday': 'Среда',
    'thursday': 'Четверг',
    'friday': 'Пятница',
    'saturday': 'Суббота',
    'sunday': 'Воскресенье'
}


class Home(DataMixin, ListView):
    paginate_by = 10
    model = Dish
    template_name = 'food/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Главная страница')
        return dict(list(context.items()) + list(c_def.items()))


class Dishes(DataMixin, ListView):
    paginate_by = 10
    model = Dish
    template_name = 'food/dishes.html'
    context_object_name = 'dishes'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Блюда')
        return dict(list(context.items()) + list(c_def.items()))


class DishesByCategory(DataMixin, ListView):
    paginate_by = 10
    model = Dish
    template_name = 'food/dishes.html'
    context_object_name = 'dishes'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Блюда')
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        selected_cat = self.kwargs['cat_slug']
        menu = (Dish.objects.
                filter(tags__meal__slug=selected_cat))
        return menu


class Ingredients(DataMixin, ListView):
    paginate_by = 10
    model = Ingredient
    template_name = 'food/ingredients.html'
    context_object_name = 'ingredients'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Ингредиенты')
        return dict(list(context.items()) + list(c_def.items()))


class DishesByIngredient(DataMixin, ListView):
    paginate_by = 10
    model = Dish
    template_name = 'food/dishes.html'
    context_object_name = 'dishes'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Блюда')
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        selected_ingredient = self.kwargs['ing_id']
        menu = (Recipe.objects.select_related('dish').
                filter(ingredient__pk=selected_ingredient))
        return menu


class Categories(DataMixin, ListView):
    model = Meal
    template_name = 'food/categories.html'
    context_object_name = 'categories'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Категории')
        return dict(list(context.items()) + list(c_def.items()))


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'food/register.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Регистрация')
        return dict(list(context.items()) + list(c_def.items()))


class LoginUser(DataMixin, LoginView):
    username = forms.CharField(label='Логин')
    form_class = LoginUserForm
    template_name = 'food/login.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Авторизация')
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')


class CollectData(DataMixin, CreateView):
    form_class = CollectDataForm
    template_name = 'food/collect_data.html'
    success_url = reverse_lazy('regenerate_menu')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.basic_metabolism = form.cleaned_data['basic_metabolism']
        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Сбор данных')
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('regenerate_menu')


class ShowMenu(DataMixin, ListView):
    model = Dish
    form_class = Dishes
    template_name = 'food/show_menu.html'
    success_url = reverse_lazy('show_menu')
    context_object_name = 'daily_menu'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_day = self.kwargs['day_slug']
        is_profile_exists = Profile.objects.filter(user=self.request.user).exists()
        is_menu_exists = Menu.objects.filter(user=self.request.user).exists()
        c_def = self.get_user_context(
            title='Меню',
            days=days,
            selected_day=selected_day,
            is_profile_exists=is_profile_exists,
            is_menu_exists=is_menu_exists
        )

        return dict(list(context.items()) + list(c_def.items()))

    def prepare_list(self, qs):
        meals = ['Завтрак', 'Обед', 'Ужин']
        daily_menu = [[meal, []] for meal in meals]
        for i in qs:
            if i.meal == 'Завтрак':
                daily_menu[0][1].append(i)
            elif i.meal == 'Обед':
                daily_menu[1][1].append(i)
            elif i.meal == 'Ужин':
                daily_menu[2][1].append(i)
        return daily_menu

    def get_queryset(self):
        menu = self.prepare_list(Menu.objects.select_related('dish').
        filter(
            user=self.request.user,
            day_of_week=days[self.kwargs['day_slug']]))
        return menu


def regenerate_menu(request):
    Menu.objects.filter(user=request.user).delete()
    create_menu(request)
    return redirect(go_to_monday)


def reset_the_questionnaire_data(request):
    Profile.objects.filter(user=request.user).delete()
    return redirect('collect_user_data')


def create_menu(request):
    metabolism = Profile.objects.get(user=request.user).basic_metabolism
    week_menu = []
    menues = [get_daily_menu(metabolism=metabolism) for i in range(7)]
    random.shuffle(menues)
    for day, menu in zip(days.keys(), menues):
        for meal in menu:
            for dish in meal[1]:
                week_menu.append(Menu(user=request.user, dish=dish, day_of_week=days[day], meal=meal[0]))
    Menu.objects.bulk_create(week_menu)
    return redirect('monday/')


def go_to_monday(request):
    return redirect('monday/')


def logout_user(request):
    logout(request)
    return redirect('login')


def about(request):
    return HttpResponse('О нас')


def contacts(request):
    return HttpResponse('Контакты')
