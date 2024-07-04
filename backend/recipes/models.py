from django.db import models
from django.db.models import UniqueConstraint
from users.models import User


class Tag(models.Model):
    """ Класс модели Тег """

    name = models.CharField(
        max_length=50,
        verbose_name='Название тега',
        unique=True)
    color = models.CharField(
        max_length=7,
        verbose_name='Цветовой HEX-код',
        unique=True)
    slug = models.SlugField(max_length=50, verbose_name='Слаг', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """ Класс модели Ингредиент """
    name = models.CharField(
        max_length=100,
        verbose_name='Название ингредиента')
    measurement_unit = models.CharField(
        max_length=50, verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """ Класс модели Рецепт """
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Автор публикации',
    )
    name = models.CharField(max_length=100, verbose_name='Название рецепта',)
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        default=None,
        verbose_name='Текстовое описание',
    )
    text = models.TextField('Текстовое описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
    )
    short_link = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Короткая ссылка')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """ Класс модели Ингредиент и Рецепт """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент и рецепт'
        verbose_name_plural = 'Ингредиенты и рецепты'

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredient.name} ({self.amount})"


class Favourite(models.Model):
    """ Класс модели Избранное """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(
                fields=[
                    'user',
                    'recipe'],
                name='unique_favourite')
        ]

    def __str__(self):
        return f'"{self.recipe}" добавлен в Избранное'


class ShoppingCart(models.Model):
    """ Класс модели Корзина """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            UniqueConstraint(
                fields=[
                    'user',
                    'recipe'],
                name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'"{self.recipe}" добавлен в корзину'
