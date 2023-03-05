from random import random, choice

from food.models import *

MEAL_PARTS = {'Завтрак': 0.3, 'Обед': 0.25, 'Ужин': 0.2}


class Meal:

    def __init__(self,
                 metabolism: int,
                 meal: str,
                 cooking_time: int = 30,
                 serving_size: int = 350,
                 hysteresis: float = 0.15,
                 dish_to_use_id=None):
        part_from_daily_calories = MEAL_PARTS[meal]
        self._high_hysteresis = 1 + hysteresis  # допуск отклонения калорий от целевого значения вверх
        self._low_hysteresis = 1 - hysteresis  # допуск отклонения калорий от целевого значения вниз
        self._serving_size = serving_size  # размер порции в г
        self._calories_needed = metabolism * part_from_daily_calories  # целевое количество калорий на один приём пищи
        self._cooking_time = cooking_time  # максимальное время готовки
        self._calories_range = self._calories_needed * self._low_hysteresis, self._calories_needed * self._high_hysteresis
        self._dish_to_use_id = dish_to_use_id
        self._meal = meal
        self.dish = self.get_set_of_dish()

    def get_dish(self, calories_filter: bool, calories_range: tuple = None):
        filters_list = {'calories__isnull': False, 'tags__meal__meal_name': self._meal}
        if calories_filter:
            if calories_range is None:
                filters_list['calories__range'] = self._calories_range
            else:
                filters_list['calories__range'] = calories_range
        dish = Dish.objects.filter(**filters_list).order_by("?").first()
        return dish

    def get_set_of_dish(self, metabolism, meal, dishes_to_use=None):
        meal_calories_part_to_service_size = metabolism * MEAL_PARTS[meal] / 3  # размер порции принят 300г
        low_calories, high_calories = meal_calories_part_to_service_size * 0.9, meal_calories_part_to_service_size * 1.1

        while True:
            if dishes_to_use:
                pass
            else:
                dish1 = self.get_dish(calories_filter=False)
                if low_calories <= dish1.calories <= high_calories:
                    return dish1,
                else:
                    calories_range = (self._calories_range[0] - dish1.calories, self._calories_range[1] - dish1.calories)
                    dish2 = self.get_dish(calories_filter=True, calories_range=calories_range)
                    if not dish2:
                        continue
                    return dish1, dish2

class DayMenu:
    def __init__(self, target: str = '', breakfast_to_use_id=None, lunch_to_use_id=None, dinner_to_use_id=None):
        self._breakfast = Eating(metabolism=METABOLISM, cooking_time=20, category='breakfast', alias='breakfast',
                                 dish_to_use_id=breakfast_to_use_id)
        self._lunch = Lunch(metabolism=METABOLISM, cooking_time=30)
        self._dinner = Eating(metabolism=METABOLISM, cooking_time=20, category='second_dish', alias='dinner',
                              dish_to_use_id=dinner_to_use_id)
        self.day_menu_variants = self.get_menu(100)


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
        if dishes_to_use:
            pass
        else:
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







