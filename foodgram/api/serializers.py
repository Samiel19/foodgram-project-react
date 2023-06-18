import base64
import webcolors

from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.core.exceptions import ValidationError
from recipy.models import Ingredient, Recipy, Tag, User, IngredientAmount, Favorites, Cart
from user.models import Follow
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from core.validator import tags_exist_validator, ingredients_validator
from core.service import ingredient_amount


class ShortRecipySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe.
    Определён укороченный набор полей для некоторых эндпоинтов.
    """
    class Meta:
        model = Recipy
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = '__all__',



class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = 'is_subscribed',
    
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return Follow.objects.filter(following=obj, user=user).exists()

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    

class UserFollowSerializer(serializers.ModelSerializer):

    following = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
    )
    user = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Самоподписка невозможна!'
            )
        ]

    def validate(self, data):
        if (data['user'] == data['following']
                and self.context['request'].method == 'POST'):
            raise serializers.ValidationError(
                'Самоподписка невозможна!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return FollowSerializer(
            instance.following,
            context={'request': request}
        ).data
    

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
        return RecipySerializer(
            recipes, many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')
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


class RecipySerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipy
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
        tags_ids = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        if not tags_ids or not ingredients:
            raise ValidationError('Недостаточно данных.')
        tags_exist_validator(tags_ids, Tag)
        ingredients = ingredients_validator(ingredients, Ingredient)
        data.update({
            'tags': tags_ids,
            'ingredients': ingredients,
            'author': self.context.get('request').user
        })
        return data


    def get_ingredients(self, recipy):
        ingredients = recipy.ingredients.values(
            'id', 'name', 'units', amount=models.F('recipy__amount')
        )
        return ingredients




    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipy = Recipy.objects.create(**validated_data)
        recipy.tags.set(tags)
        ingredient_amount(recipy, ingredients)
        return recipy


    @transaction.atomic
    def update(self, recipy, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for key, value in validated_data.items():
            if hasattr(recipy, key):
                setattr(recipy, key, value)
        if tags:
            recipy.tags.clear()
            recipy.tags.set(tags)
        if ingredients:
            recipy.ingredients.clear()
            ingredient_amount(recipy, ingredients)
            print(ingredients)
        recipy.save()
        return recipy
    

    def get_is_favorited(self, recipy):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Favorites.objects.filter(recipy=recipy, user=user).exists()

    def get_is_in_shopping_cart(self, recipy):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Cart.objects.filter(recipy=recipy, user=user).exists()


class FavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'recipy')
        model = Favorites
        validators = [
            UniqueTogetherValidator(
                queryset=Favorites.objects.all(),
                fields=('user', 'recipy'),
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def to_representation(self, instance):
        requset = self.context.get('request')
        return RecipySerializer(
            instance.recipy,
            context={'request': requset}
        ).data
    

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'recipy')
        model = Cart
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('user', 'recipy'),
                message='Рецепт уже добавлен в корзину'
            )
        ]

    def to_representation(self, instance):
        requset = self.context.get('request')
        return RecipySerializer(
            instance.recipy,
            context={'request': requset}
        ).data