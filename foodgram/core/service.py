from enum import Enum, IntEnum
from django.db import models
from recipy.models import IngredientAmount, Recipy


class Tuples(tuple, Enum):
    # Размер сохраняемого изображения рецепта
    RECIPE_IMAGE_SIZE = 500, 300
    # Поиск объектов только с переданным параметром.
    # Например только в избранном: `is_favorited=1`
    SYMBOL_TRUE_SEARCH = '1', 'true'
    # Поиск объектов не содержащих переданный параметр.
    # Например только не избранное: `is_favorited=0`
    SYMBOL_FALSE_SEARCH = '0', 'false'
    ADD_METHODS = 'GET', 'POST'
    DEL_METHODS = 'DELETE',
    ACTION_METHODS = 'GET', 'POST', 'DELETE'
    UPDATE_METHODS = 'PUT', 'PATCH'



def ingredient_amount(recipy, ingredients):
    ingredient_amount = []
    for ingredient, amount in ingredients.values():
        ingredient_amount.append(IngredientAmount(
            recipy=recipy,
            ingredients=ingredient,
            amount=amount
        ))
    IngredientAmount.objects.bulk_create(ingredient_amount)