import base64

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from django.core.files.base import ContentFile

from django.contrib.auth import get_user_model
from django.db import transaction, models
from recipy.models import Follow, Ingredient, Recipy, Tag, User



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


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__',


class IngredientSerializer(serializers.Serializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__'


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
    is_favorit = serializers.SerializerMethodField()
    is_in_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipy
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorite',
            'is_in_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'is_favorite',
            'is_in_cart',
        )


    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipy = Recipy.objects.create(**validated_data)
        recipy.tags.set(tags)
        recipy.ingridients.set(ingredients)


    @transaction.atomic
    def update(self, recipy, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        for key, value in validated_data.items():
            if hasattr(recipy, key):
                setattr(recipy, key, value)
        if tags:
            recipy.tags.clear()
            recipy.tags.set(tags)
        if ingredients:
            recipy.ingredients.clear()
            recipy.ingredients.set(ingredients)
        recipy.save()
        return recipy
    
    
    def get_ingredients(self, recipy):
        ingredients = recipy.ingredients.values(
            'id', 'name', 'measurement_unit', amount=models.F('recipy__amount')
        )
        return ingredients

    def get_is_favorited(self, recipy):
        user = self.context.get('view').request.user
        if user.is_authenticated():
            return user.favorites.filter(recipy=recipy).exists()

    def get_is_in_cart(self, recipy):
        user = self.context.get('view').request.user
        if user.is_authenticated():
            return user.carts.filter(recipy=recipy).exists()
    

class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        fields = ('id', 'user', 'following')
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'following']
            )
        ]