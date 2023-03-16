import urllib.parse

from django import forms
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.db.models import Prefetch, Q
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from food.services.create_menu import get_set_of_dish, get_daily_menu
import random

from .models import *
from django.views.generic import ListView, CreateView, FormView

from .templates.forms import RegisterUserForm, LoginUserForm, CollectDataForm, MenuGenerateForm, FilterForm
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


def get_filters(request):
    filters = {}
    min_calories = request.GET.get('min_cal')
    max_calories = request.GET.get('max_cal')
    min_active_cooking_time = request.GET.get('min_a_time')
    max_active_cooking_time = request.GET.get('max_a_time')
    min_total_cooking_time = request.GET.get('min_t_time')
    max_total_cooking_time = request.GET.get('max_t_time')
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
    return filters


class Home(DataMixin, ListView):
    paginate_by = 10
    model = Dish
    template_name = 'food/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Главная страница')
        return dict(list(context.items()) + list(c_def.items()))


class FilterFormClass:
    def get_filled_filter_parameters(self):
        filter_parameters = {}
        get_dict = self.request.GET
        for parameter in get_dict:
            if get_dict[parameter]:
                if parameter == 'categories':
                    filter_parameters['categories'] = get_dict.getlist('categories')
                else:
                    filter_parameters[parameter] = get_dict[parameter]
        return filter_parameters

    def filter_parameters(self):
        parameters_for_url = self.request.GET.copy()
        if 'page' in parameters_for_url:
            del parameters_for_url['page']
        filled_parameters = self.get_filled_filter_parameters()
        return parameters_for_url, filled_parameters


class Dishes(DataMixin, ListView, FilterFormClass):
    paginate_by = 10
    model = Dish
    template_name = 'food/dishes.html'
    context_object_name = 'dishes'
    success_url = reverse_lazy('dishes')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_params, parameters = self.filter_parameters()
        c_def = self.get_user_context(
            title='Блюда',
            filter_params=filter_params.urlencode(),
            filter_form=FilterForm(initial=parameters),
            is_filtered=bool(parameters))
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        queryset = super().get_queryset()
        form = FilterForm(self.request.GET)
        if form.is_valid():
            queryset = form.filter(queryset)
        return queryset

    def get_success_url(self):
        url = reverse('dishes')
        form = FilterForm(self.request.GET)
        query_params = form.get_query_params()
        if query_params:
            url += '?' + '&'.join([f'{key}={value}' for key, value in query_params.items()])
        return url


class Ingredients(DataMixin, ListView):
    paginate_by = 10
    model = Ingredient
    template_name = 'food/ingredients.html'
    context_object_name = 'ingredients'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Ингредиенты')
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        search = self.request.GET.get('search')
        queryset = Ingredient.objects.filter(ingredient_name__icontains=search)
        return queryset


class DishesByIngredient(DataMixin, ListView, FilterFormClass):
    paginate_by = 10
    model = Dish
    template_name = 'food/dishes.html'
    context_object_name = 'dishes'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_params, parameters = self.filter_parameters()
        c_def = self.get_user_context(
            title='Блюда',
            filter_params=filter_params.urlencode(),
            filter_form=FilterForm(initial=parameters),
            is_filtered=bool(parameters))
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        selected_ingredient = self.kwargs['ing_id']
        menu = Dish.objects.filter(
            Q(recipe__ingredient__pk=selected_ingredient)
        )
        form = FilterForm(self.request.GET)
        if form.is_valid():
            menu = form.filter(menu)
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
