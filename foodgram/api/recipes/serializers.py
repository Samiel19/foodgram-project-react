import base64

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models, transaction

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipe.service import (
    ingredients_validator,
    ingredient_amount,
    tags_validator
)
from api.users.serializers import UserSerializer
from recipe.models import Cart, Favorites, Ingredient, Recipe, Tag, User
from user.models import Follow


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_following', 'recipes', 'recipes_count'
        )

    def get_is_following(self, user):
        current_user = self.context.get('current_user')
        other_user = user.following.all()
        if user.is_anonymous:
            return False
        if other_user.count() == 0:
            return False
        if Follow.objects.filter(user=user, following=current_user).exists():
            return True
        return False

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:3]
        request = self.context.get('request')
        return RecipeSerializer(
            recipes, many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__',


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__',


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        if not tags or not ingredients:
            raise ValidationError('Недостаточно данных.')
        tags_validator(tags, Tag)
        ingredients = ingredients_validator(ingredients, Ingredient)
        data.update({
            'tags': tags,
            'ingredients': ingredients,
            'author': self.context.get('request').user
        })
        return data

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit', amount=models.F('recipe__amount')
        )
        return ingredients

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.recipes.create(**validated_data)
        recipe.tags.set(tags)
        ingredient_amount(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        if ingredients:
            recipe.ingredients.clear()
            ingredient_amount(recipe, ingredients)
        recipe.save()
        return recipe

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Favorites.objects.filter(recipe=recipe, user=user).exists()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Cart.objects.filter(recipe=recipe, user=user).exists()


class FavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'recipe')
        model = Favorites
        validators = [
            UniqueTogetherValidator(
                queryset=Favorites.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def to_representation(self, instance):
        return RecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'recipe')
        model = Cart
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в корзину'
            )
        ]

    def to_representation(self, instance):
        return RecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
