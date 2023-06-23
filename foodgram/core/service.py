from recipe.models import IngredientAmount


def ingredient_amount(recipe, ingredients):
    ingredient_amount = []
    for ingredient, amount in ingredients.values():
        ingredient_amount.append(IngredientAmount(
            recipe=recipe,
            ingredients=ingredient,
            amount=amount
        ))
    IngredientAmount.objects.bulk_create(ingredient_amount)
