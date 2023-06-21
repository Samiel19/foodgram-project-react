from recipy.models import IngredientAmount


def ingredient_amount(recipy, ingredients):
    ingredient_amount = []
    for ingredient, amount in ingredients.values():
        ingredient_amount.append(IngredientAmount(
            recipy=recipy,
            ingredients=ingredient,
            amount=amount
        ))
    IngredientAmount.objects.bulk_create(ingredient_amount)
