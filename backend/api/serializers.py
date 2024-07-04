import base64
from django.db.models import F
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.exceptions import ValidationError

from recipes.models import (
    Tag, Ingredient, Recipe, IngredientRecipe, Favourite, ShoppingCart)
from users.models import (
    User, Subscribe
)
from users.validators import validate_username


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password',)
        lookup_field = 'username'

    def validate_username(self, value):
        return validate_username(value)


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj).exists()


class SubscribeSerializer(CustomUserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + \
            ('recipes_count', 'recipes')
        read_only_fields = ('email', 'username')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeShortSerializer(recipes, many=True, read_only=True)

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = ['avatar']


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    short_link = serializers.CharField(source='get_short_link', read_only=True)

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
            'short_link',
        )

    def get_ingredients(self, obj):
        return obj.ingredients.annotate(amount=F(
            'ingredientrecipe__amount')).values(
            'id', 'name', 'measurement_unit', 'amount'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and Favourite.objects.filter(
            user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and ShoppingCart.objects.filter(
            user=user, recipe=obj).exists()

    def get_short_link(self, obj):
        return obj.short_link


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField()
    short_link = serializers.CharField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'short_link',
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError({'ingredients': 'Добавьте ингредиент'})
        unique_ingredients = set()
        for item in ingredients:
            ingredient_id = item.get('id')
            amount = item.get('amount')
            if not ingredient_id or not amount:
                raise ValidationError(
                    {'ingredients': 'Неверные данные об ингредиентах'})
            if ingredient_id in unique_ingredients:
                raise ValidationError(
                    {'ingredients': 'Ингредиенты не должны повторяться'})
            if amount <= 0:
                raise ValidationError(
                    {'amount':
                     'Количество ингредиентов должно быть больше нуля'})
            unique_ingredients.add(ingredient_id)
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError({'tags': 'Нужно выбрать тег'})
        if len(tags) != len(set(tags)):
            raise ValidationError({'tags': 'Тег не должен повторяться'})
        return tags

    def create_short_link(self):
        current_domain = self.context['request'].get_host()
        return f'{current_domain}/s/{get_random_string(length=10)}'

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        validated_data['short_link'] = self.create_short_link()
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._create_ingredient_recipes(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.ingredients.clear()
        self._create_ingredient_recipes(instance, ingredients)
        return instance

    def _create_ingredient_recipes(self, recipe, ingredients):
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])

    def to_representation(self, instance):
        context = {'request': self.context['request']}
        return RecipeSerializer(instance, context=context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteCreateSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favourite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = self.context['request'].user
        recipe = data.get('recipe')
        if self.context['request'].method == 'POST':
            if Favourite.objects.filter(user=user, recipe=recipe).exists():
                raise ValidationError('Рецепт уже добавлен в избранное')
        elif self.context['request'].method == 'DELETE':
            if not Favourite.objects.filter(user=user, recipe=recipe).exists():
                raise ValidationError('Рецепт уже удален из избранного')
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        recipe = validated_data.get('recipe')
        favourite, created = Favourite.objects.get_or_create(
            user=user, recipe=recipe)
        return favourite
