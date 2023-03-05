from peewee import *

database = SqliteDatabase('db.sqlite3')

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database



class FoodDish(BaseModel):
    active_cooking_time = IntegerField(null=True)
    calories = IntegerField(null=True)
    dish_name = CharField()
    href = CharField(unique=True)
    portions_count = IntegerField(null=True)
    total_cooking_time = IntegerField(null=True)

    class Meta:
        table_name = 'food_dish'

class FoodTag(BaseModel):
    tag_name = CharField(unique=True)

    class Meta:
        table_name = 'food_tag'

class FoodDishTags(BaseModel):
    dish = ForeignKeyField(column_name='dish_id', field='id', model=FoodDish)
    tag = ForeignKeyField(column_name='tag_id', field='id', model=FoodTag)

    class Meta:
        table_name = 'food_dish_tags'
        indexes = (
            (('dish', 'tag'), True),
        )

class FoodStoredepartment(BaseModel):
    department_name = CharField(null=True)

    class Meta:
        table_name = 'food_storedepartment'

class FoodIngredient(BaseModel):
    carbohydrates_value = IntegerField(null=True)
    department = ForeignKeyField(column_name='department_id', field='id', model=FoodStoredepartment, null=True)
    energy_value = IntegerField(null=True)
    fats_value = IntegerField(null=True)
    ingredient_name = CharField(unique=True)
    protein_value = IntegerField(null=True)

    class Meta:
        table_name = 'food_ingredient'

class FoodMeal(BaseModel):
    meal_name = CharField()

    class Meta:
        table_name = 'food_meal'

class FoodRecipe(BaseModel):
    dish = ForeignKeyField(column_name='dish_id', field='id', model=FoodDish)
    ingredient_id = ForeignKeyField(column_name='ingredient_id_id', field='id', model=FoodIngredient)
    measure_unit = CharField(null=True)
    note = CharField(null=True)
    quantity = FloatField()

    class Meta:
        table_name = 'food_recipe'


class FoodTagMeal(BaseModel):
    meal = ForeignKeyField(column_name='meal_id', field='id', model=FoodMeal)
    tag = ForeignKeyField(column_name='tag_id', field='id', model=FoodTag)

    class Meta:
        table_name = 'food_tag_meal'
        indexes = (
            (('tag', 'meal'), True),
        )


class FoodWeight(BaseModel):
    ingredient = ForeignKeyField(column_name='ingredient_id', field='id', model=FoodIngredient)
    weight = FloatField(null=True)

    class Meta:
        table_name = 'food_weight'


class SqliteSequence(BaseModel):
    name = BareField(null=True)
    seq = BareField(null=True)

    class Meta:
        table_name = 'sqlite_sequence'
        primary_key = False

