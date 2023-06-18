from django.core.exceptions import ValidationError
from recipy.models import Ingredient, Tag

def tags_exist_validator(tags_ids: list[int | str], Tag: 'Tag') -> None:
    """Проверяет наличие тэгов с указанными id.

    Args:
        tags_ids (list[int | str]): Список id.
        Tag (Tag): Модель тэгов во избежании цикличного импорта.

    Raises:
        ValidationError: Тэга с одним из указанных id не существует.
    """
    exists_tags = Tag.objects.filter(id__in=tags_ids)

    if len(exists_tags) != len(tags_ids):
        raise ValidationError('Указан несуществующий тэг')
    

def ingredients_validator(
    ingredients: list[dict[str, str | int]],
    Ingredient: 'Ingredient',
) -> dict[int, tuple['Ingredient', int]]:

    valid_ings = {}

    for ing in ingredients:
        if not (isinstance(ing['amount'], int) or ing['amount'].isdigit()):
            raise ValidationError('Неправильное количество ингидиента')

        amount = valid_ings.get(ing['id'], 0) + int(ing['amount'])
        if amount <= 0:
            raise ValidationError('Неправильное количество ингридиента')

        valid_ings[ing['id']] = amount

    if not valid_ings:
        raise ValidationError('Неправильные ингидиенты')

    db_ings = Ingredient.objects.filter(pk__in=valid_ings.keys())
    if not db_ings:
        raise ValidationError('Неправильные ингидиенты')

    for ing in db_ings:
        valid_ings[ing.pk] = (ing, valid_ings[ing.pk])

    return valid_ings