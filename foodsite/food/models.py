from django.db import models
from django.core import validators


class Profile(models.Model):
    gender_choices = [(True, 'Мужской'),
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
    user = models.ForeignKey('auth.User', null=True, on_delete=models.CASCADE)
    age = models.IntegerField(
        null=True,
        validators=[
            validators.MinValueValidator(limit_value=1, message='Попробуйте, когда родитесь'),
            validators.MaxValueValidator(limit_value=100, message='Ты слишком стар для этого дерьма')
        ],
        verbose_name='Возраст')
    gender = models.BooleanField(null=True, choices=gender_choices, verbose_name='Пол')
    weight = models.IntegerField(null=True, verbose_name='Вес')
    height = models.IntegerField(null=True, verbose_name='Рост')
    physical_activity = models.IntegerField(
        default=2,
        choices=physical_activity_choice,
        verbose_name='Уровень физической активности')
    basic_metabolism = models.IntegerField(null=True, verbose_name='Базовый обмен веществ')


class Tag(models.Model):
    tag_name = models.CharField(max_length=255, unique=True)
    meal = models.ManyToManyField('Meal')

    def __str__(self):
        return self.tag_name


class Meal(models.Model):
    meal_name = models.CharField(max_length=255, verbose_name='Приём пищи')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='URL')

    class Meta:
        verbose_name = 'Приём пищи'
        verbose_name_plural = 'Приёмы пищи'
        ordering = ['id']

    def __str__(self):
        return self.meal_name


class StoreDepartment(models.Model):
    department_name = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.department_name


class Dish(models.Model):
    dish_name = models.CharField(max_length=255, unique=False, verbose_name='Рецепт')
    ingredients = models.ManyToManyField('Ingredient', through='Recipe', through_fields=('dish', 'ingredient'))
    href = models.CharField(max_length=255, unique=True, verbose_name='Ссылка на рецепт')
    photo = models.CharField(max_length=255, null=True, verbose_name='Фото')
    total_cooking_time = models.IntegerField(null=True, verbose_name='Общее время приготовления')
    active_cooking_time = models.IntegerField(null=True, verbose_name='Активное время приготовления')
    portions_count = models.IntegerField(null=True, verbose_name='Количество порций')
    calories = models.IntegerField(null=True, verbose_name='Энергетическая ценность')
    tags = models.ManyToManyField(Tag, verbose_name='Тэги')

    def __str__(self):
        return self.dish_name


class UserDish(models.Model):
    user = models.ForeignKey('auth.User', null=True, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, null=True, on_delete=models.CASCADE)
    recipe = models.TextField(verbose_name='Рецепт', null=True)
    add_to_common = models.BooleanField(verbose_name='Добавить в общий список', default=False)


class DishBlackList(models.Model):
    user = models.ForeignKey('auth.User', unique=False, null=True, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, null=True, on_delete=models.CASCADE)
    added_by_ingredient = models.ForeignKey('Ingredient', null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'dish', 'added_by_ingredient')


class Ingredient(models.Model):
    ingredient_name = models.CharField(max_length=255, unique=True, verbose_name='Ингредиент')
    protein_value = models.FloatField(null=True, verbose_name='Белки')
    fats_value = models.FloatField(null=True, verbose_name='Жиры')
    carbohydrates_value = models.FloatField(null=True, verbose_name='Углеводы')
    energy_value = models.FloatField(null=True, verbose_name='Энергетическая ценность (на 100г.)')
    department = models.ForeignKey(StoreDepartment, null=True, on_delete=models.CASCADE,
                                   verbose_name='Отдел в магазине')

    def __str__(self):
        return self.ingredient_name

    class Meta:
        ordering = ['ingredient_name']


class UserIngredient(models.Model):
    user = models.ForeignKey('auth.User', unique=False, null=True, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, unique=False, null=True, on_delete=models.CASCADE)
    add_to_common = models.BooleanField(verbose_name='Добавить в общий список', default=False)
    is_active = models.BooleanField(verbose_name='Активное', default=False)


class IngredientBlackList(models.Model):
    user = models.ForeignKey('auth.User', unique=False, null=True, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, unique=False, null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'ingredient')


class Recipe(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, verbose_name='Блюдо')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, verbose_name='Ингредиент')
    quantity = models.FloatField(verbose_name='Количество')
    measure_unit = models.CharField(max_length=255, null=True, verbose_name='Единицы измерения')
    note = models.CharField(max_length=255, null=True, verbose_name='Примечания')


class Weight(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    weight = models.FloatField(null=True)


class Menu(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    meal = models.CharField(max_length=255, null=True)
    day_of_week = models.CharField(max_length=255, null=True)
