from django.core.exceptions import ValidationError

from recipe.models import Ingredient, Tag


def tags_validator(tags_id, Tag: 'Tag'):
    exists_tags = Tag.objects.filter(id__in=tags_id)
    if len(exists_tags) != len(tags_id):
        raise ValidationError('Такого тэга нет!')


def ingredients_validator(ingredients, Ingredient: 'Ingredient'):
    validated_ingredients = {}
    for ing in ingredients:
        if not str(ing['amount']).isdigit():
            raise ValidationError('Количество измеряется в числах!')
        amount = validated_ingredients.get(ing['id'], 0) + int(ing['amount'])
        if amount <= 0:
            raise ValidationError('Неправильное количество ингридиента')
        validated_ingredients[ing['id']] = amount
    if not validated_ingredients:
        raise ValidationError('Нужны ингридиенты!')
    db_validated_ingredients = Ingredient.objects.filter(
        pk__in=validated_ingredients.keys()
        )
    if not db_validated_ingredients:
        raise ValidationError('Неправильные ингидиенты')
    for ing in db_validated_ingredients:
        validated_ingredients[ing.pk] = (ing, validated_ingredients[ing.pk])
    return validated_ingredients
