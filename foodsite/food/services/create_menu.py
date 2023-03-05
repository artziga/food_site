from food.models import *

MEAL_PARTS = {'Завтрак': 0.3, 'Обед': 0.25, 'Ужин': 0.2}


def get_random_dish(calories_range=None, meal=None):
    filters_list = {'calories__isnull': False}
    if meal:
        filters_list['tags__meal__meal_name'] = meal
    if calories_range:
        filters_list['calories__range'] = calories_range
    dish = Dish.objects.filter(**filters_list).order_by("?").first()
    return dish


def get_set_of_dish(metabolism, meal, dishes_to_use=None):
    meal_calories_part_to_service_size = metabolism * MEAL_PARTS[meal] / 3  # размер порции принят 300г
    low_calories, high_calories = meal_calories_part_to_service_size * 0.9, meal_calories_part_to_service_size * 1.1

    while True:
        dish1 = get_random_dish(meal=meal)
        if low_calories <= dish1.calories <= high_calories:
            return dish1,
        else:
            calories_range = (low_calories - dish1.calories, high_calories - dish1.calories)
            dish2 = get_random_dish(calories_range=calories_range, meal=meal)
            if not dish2:
                continue
            return dish1, dish2


def get_daily_menu(metabolism):
    meals = ['Завтрак', 'Обед', 'Ужин']
    daily_menu = []
    for meal in meals:
        daily_menu.append([meal, get_set_of_dish(metabolism=metabolism, meal=meal)])
    return daily_menu







