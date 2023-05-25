from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Prefetch, Q
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.forms import modelform_factory
from food.services.create_menu import get_set_of_dish, get_daily_menu
import random
from django.db.transaction import atomic

from .models import *
from django.views.generic import ListView, CreateView, DetailView

from .templates.forms import *
from .templates.utils import DataMixin, days, get_filters


class Home(DataMixin, ListView):
    """Показывает приветственную страницу"""
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
        user_black_list = set(
            DishBlackList.objects.
            values_list('dish', flat=True).
            filter(user=self.request.user, added_by_ingredient__isnull=True))
        user_black_list_by_ingredients = set(DishBlackList.objects.values_list(
            'dish', flat=True).filter(user=self.request.user, added_by_ingredient__isnull=False))

        c_def = self.get_user_context(
            title='Блюда',
            filter_params=filter_params.urlencode(),
            filter_form=FilterForm(initial=parameters),
            is_filtered=bool(parameters),
            black_list=user_black_list,
            black_list_by_ingredients=user_black_list_by_ingredients,
        )
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        form = FilterForm(self.request.GET)
        if form.is_valid():
            queryset = form.filter(queryset, user)
        return queryset

    def get_success_url(self):
        url = reverse('dishes')
        form = FilterForm(self.request.GET)
        query_params = form.get_query_params()
        if query_params:
            url += '?' + '&'.join([f'{key}={value}' for key, value in query_params.items()])
        return url


class DishDetailView(DataMixin, DetailView):
    model = Dish
    context_object_name = 'dish'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        dish = self.get_object()
        ingredients = dish.recipe_set.select_related('ingredient').all()
        c_def = self.get_user_context(title='Блюдо', ingredients=ingredients)
        return dict(list(context.items()) + list(c_def.items()))


class IngredientDetailView(DataMixin, DetailView):
    model = Ingredient
    context_object_name = 'ingredient'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Блюдо')
        return dict(list(context.items()) + list(c_def.items()))


class SearchView(DataMixin, ListView):
    paginate_by = 10
    model = Dish
    template_name = 'food/dishes.html'
    context_object_name = 'dishes'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        searched = bool(self.request.GET.get('search'))
        c_def = self.get_user_context(
            title='Поиск',
            is_filtered=bool(searched)
        )
        context = dict(list(context.items()) + list(c_def.items()))
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        search = self.request.GET.get('search')
        if search:
            queryset = Dish.objects.filter(dish_name__icontains=search)
        else:
            queryset = Dish.objects.all()
        return queryset


class IngredientsView(DataMixin, ListView):
    paginate_by = 20
    model = Ingredient
    template_name = 'food/ingredients.html'
    context_object_name = 'ingredients'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user_black_list = set(
            IngredientBlackList.objects.values_list('ingredient', flat=True).filter(user=self.request.user))

        c_def = self.get_user_context(title='Ингредиенты', black_list=user_black_list)
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_authenticated:
            is_staff = User.objects.get(username=user).is_staff
            if is_staff:
                queryset = Ingredient.objects.all()
            else:
                queryset = Ingredient.objects.filter(Q(user__isnull=True) | Q(user=user))
        else:
            queryset = Ingredient.objects.filter(Q(user__isnull=True))
        search = self.request.GET.get('search', None)
        queryset = queryset.filter(ingredient_name__icontains=search) if search else queryset.all()
        return queryset


class AddIngredientView(DataMixin, CreateView):
    template_name = 'food/add_ingredient.html'
    form_class = AddIngredientForm
    model = Ingredient
    success_url = reverse_lazy('ingredients')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Добавить ингредиент')
        return dict(list(context.items()) + list(c_def.items()))


class AddRecipeView(DataMixin, CreateView):
    template_name = 'food/add_dish.html'
    model = Dish
    form_class = AddDishForm
    success_url = reverse_lazy('dishes')

    def get_success_url(self):
        return reverse_lazy('dishes')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        add_ingredients_form = RecipeFormSet(queryset=Recipe.objects.none())
        c_def = self.get_user_context(title='Добавить рецепт', add_ingredients_formset=add_ingredients_form)
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        ingredients_formset = RecipeFormSet(self.request.POST, queryset=Recipe.objects.none())
        with atomic():
            dish = form.save()
            if ingredients_formset.is_valid():
                for recipe_form in ingredients_formset:
                    if recipe_form.cleaned_data:
                        recipe = recipe_form.save(commit=False)
                        recipe.dish = dish  # Назначаем dish
                        recipe.save()

            else:
                print(ingredients_formset.errors, ingredients_formset.non_form_errors())
        return HttpResponseRedirect(self.get_success_url())


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
        user = self.request.user
        menu = Dish.objects.filter(
            Q(recipe__ingredient__pk=selected_ingredient)
        )
        # form = FilterForm(self.request.GET)
        # if form.is_valid():
        #     menu = form.filter(menu, user)
        return menu


class Categories(DataMixin, ListView):
    model = Meal
    template_name = 'food/categories.html'
    context_object_name = 'categories'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Категории')
        return dict(list(context.items()) + list(c_def.items()))


class BlackListView(DataMixin, ListView):
    template_name = 'food/categories.html'
    context_object_name = 'black_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Чёрный список')
        return dict(list(context.items()) + list(c_def.items()))


class DishBlackListView(BlackListView):
    model = DishBlackList


class IngredientBlackListView(BlackListView):
    model = IngredientBlackList


def add_ingredient_to_black_list_view(request, pk):
    user = request.user
    ingredient = Ingredient.objects.get(pk=pk)
    try:
        IngredientBlackList.objects.create(user=user, ingredient=ingredient)
    except IntegrityError:
        print('Попытка добавить ингредиент в чс дважды')
    related_dishes = Dish.objects.filter(
        Q(recipe__ingredient__pk=ingredient.pk))
    for dish in related_dishes:
        try:
            DishBlackList.objects.create(user=user, dish=dish, added_by_ingredient=ingredient)
        except IntegrityError:
            print('Попытка добавить в чс блюдо дважды')

    return redirect(request.META.get('HTTP_REFERER'))


def add_dish_to_black_list_view(request, pk):
    user = request.user
    dish = Dish.objects.get(pk=pk)
    try:
        DishBlackList.objects.create(user=user, dish=dish)
    except IntegrityError:
        print('Попытка добавить в чс блюдо дважды')

    return redirect(request.META.get('HTTP_REFERER'))


def remove_ingredient_from_black_list_view(request, pk):
    user = request.user
    ingredient = Ingredient.objects.get(pk=pk)
    IngredientBlackList.objects.filter(user=user, ingredient=ingredient).delete()
    dishes_to_delete = DishBlackList.objects.filter(user=user, added_by_ingredient=ingredient)
    dishes_to_delete.delete()
    return redirect(request.META.get('HTTP_REFERER'))


def remove_dish_from_black_list_view(request, pk):
    user = request.user
    dish = Dish.objects.get(pk=pk)
    dish_to_delete = DishBlackList.objects.get(user=user, dish=dish, added_by_ingredient__isnull=True)
    dish_to_delete.delete()
    return redirect(request.META.get('HTTP_REFERER'))


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


def prepare_list(qs):
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

    def get_queryset(self):
        menu = prepare_list(Menu.objects.select_related('dish').
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
    user = request.user
    metabolism = Profile.objects.get(user=user).basic_metabolism
    week_menu = []
    menues = [get_daily_menu(metabolism=metabolism, user=user) for i in range(7)]
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
