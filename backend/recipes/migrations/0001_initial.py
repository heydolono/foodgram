# Generated by Django 3.2.3 on 2024-07-05 22:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100, verbose_name="Название ингредиента"
                    ),
                ),
                (
                    "measurement_unit",
                    models.CharField(max_length=50, verbose_name="Единица измерения"),
                ),
            ],
            options={
                "verbose_name": "Ингредиент",
                "verbose_name_plural": "Ингредиенты",
            },
        ),
        migrations.CreateModel(
            name="IngredientRecipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.PositiveSmallIntegerField(verbose_name="Количество")),
                (
                    "ingredient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="recipes.ingredient",
                        verbose_name="Ингредиент",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ингредиент и рецепт",
                "verbose_name_plural": "Ингредиенты и рецепты",
            },
        ),
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=100, verbose_name="Название рецепта"),
                ),
                (
                    "image",
                    models.ImageField(
                        default=None,
                        null=True,
                        upload_to="recipes/",
                        verbose_name="Текстовое описание",
                    ),
                ),
                ("text", models.TextField(verbose_name="Текстовое описание")),
                (
                    "cooking_time",
                    models.PositiveIntegerField(
                        verbose_name="Время приготовления в минутах"
                    ),
                ),
                (
                    "short_link",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        unique=True,
                        verbose_name="Короткая ссылка",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="recipes",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор публикации",
                    ),
                ),
                (
                    "ingredients",
                    models.ManyToManyField(
                        related_name="recipes",
                        through="recipes.IngredientRecipe",
                        to="recipes.Ingredient",
                        verbose_name="Ингредиенты",
                    ),
                ),
            ],
            options={
                "verbose_name": "Рецепт",
                "verbose_name_plural": "Рецепты",
            },
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=50, unique=True, verbose_name="Название тега"
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        max_length=7, unique=True, verbose_name="Цветовой HEX-код"
                    ),
                ),
                ("slug", models.SlugField(unique=True, verbose_name="Слаг")),
            ],
            options={
                "verbose_name": "Тег",
                "verbose_name_plural": "Теги",
            },
        ),
        migrations.CreateModel(
            name="ShoppingCart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shopping_cart",
                        to="recipes.recipe",
                        verbose_name="Рецепт",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shopping_cart",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Корзина",
                "verbose_name_plural": "Корзина",
            },
        ),
        migrations.AddField(
            model_name="recipe",
            name="tags",
            field=models.ManyToManyField(
                related_name="recipes", to="recipes.Tag", verbose_name="Тег"
            ),
        ),
        migrations.AddField(
            model_name="ingredientrecipe",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="recipes.recipe",
                verbose_name="Рецепт",
            ),
        ),
        migrations.CreateModel(
            name="Favourite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorites",
                        to="recipes.recipe",
                        verbose_name="Рецепт",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorites",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Избранное",
                "verbose_name_plural": "Избранное",
            },
        ),
        migrations.AddConstraint(
            model_name="shoppingcart",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_shopping_cart"
            ),
        ),
        migrations.AddConstraint(
            model_name="favourite",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_favourite"
            ),
        ),
    ]
