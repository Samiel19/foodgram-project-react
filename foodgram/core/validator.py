from django.core.exceptions import ValidationError
from recipy.models import Ingredient, Tag

def tags_validator(tags_id, Tag: 'Tag'):
    exists_tags = Tag.objects.filter(id__in=tags_id)
    if len(exists_tags) != len(tags_id):
        raise ValidationError('Такого тэга нет!')
    

def ingredients_validator(ingredients, Ingredient: 'Ingredient'):

    ings = {}

    for ing in ingredients:
        if not str(ing['amount']).isdigit():
            raise ValidationError('Ингридиент должен быть числом!')

        amount = ings.get(ing['id'], 0) + int(ing['amount'])
        if amount <= 0:
            raise ValidationError('Неправильное количество ингридиента')

        ings[ing['id']] = amount

    if not ings:
        raise ValidationError('Нужны ингридиенты!')

    db_ings = Ingredient.objects.filter(pk__in=ings.keys())
    if not db_ings:
        raise ValidationError('Неправильные ингидиенты')

    for ing in db_ings:
        ings[ing.pk] = (ing, ings[ing.pk])

    return ings