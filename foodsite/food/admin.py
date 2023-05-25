from django.contrib import admin
from .models import *


class MealAdmin(admin.ModelAdmin):
    list_display = ('id', 'meal_name', 'slug')
    list_display_links = ('id', 'meal_name')
    search_fields = ('meal_name',)


class DishAdmin(admin.ModelAdmin):
    list_display = ('id', 'dish_name', 'href', 'photo', 'total_cooking_time',
                    'active_cooking_time', 'portions_count', 'calories')
    list_display_links = ('id', 'dish_name')
    search_fields = ('dish_name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('dish', 'ingredient', 'quantity', 'measure_unit', 'note')


class MenuAdmin(admin.ModelAdmin):
    list_display = ('user', 'dish', 'meal', 'day_of_week')


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'basic_metabolism')


class TagAmin(admin.ModelAdmin):
    list_display = ('tag_name',)
    search_fields = ('tag_name',)


admin.site.register(Meal, MealAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(Ingredient)
admin.site.register(Tag, TagAmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Recipe, RecipeAdmin)
