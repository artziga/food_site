from django.db import models


class Profile(models.Model):
    user = models.ForeignKey('auth.User', null=True, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, verbose_name='Возраст')
    gender = models.BooleanField(null=True, verbose_name='Пол')
    weight = models.IntegerField(null=True, verbose_name='Вес')
    height = models.IntegerField(null=True, verbose_name='Рост')
    physical_activity = models.IntegerField(default=2, verbose_name='Уровень физической активности')
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
    dish_name = models.CharField(max_length=255, unique=False)
    href = models.CharField(max_length=255, unique=True)
    photo = models.CharField(max_length=255, null=True)
    total_cooking_time = models.IntegerField(null=True)
    active_cooking_time = models.IntegerField(null=True)
    portions_count = models.IntegerField(null=True)
    calories = models.IntegerField(null=True)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.dish_name


class Ingredient(models.Model):
    ingredient_name = models.CharField(max_length=255, unique=True)
    protein_value = models.FloatField(null=True)
    fats_value = models.FloatField(null=True)
    carbohydrates_value = models.FloatField(null=True)
    energy_value = models.FloatField(null=True)
    department = models.ForeignKey(StoreDepartment, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.ingredient_name


class Recipe(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    quantity = models.FloatField()
    measure_unit = models.CharField(max_length=255, null=True)
    note = models.CharField(max_length=255, null=True)


class Weight(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    weight = models.FloatField(null=True)


class Menu(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    meal = models.CharField(max_length=255, null=True)
    day_of_week = models.CharField(max_length=255, null=True)


