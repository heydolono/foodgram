from django.contrib import admin
from django.contrib.admin import display

from .models import (Favourite, Ingredient,
                     IngredientRecipe, Recipe, ShoppingCart, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author', 'added_in_favorites', 'short_link')
    readonly_fields = ('added_in_favorites',)
    list_filter = ('author', 'tags',)
    search_fields = ('name', 'author__username', 'author__email')

    @display(description='Общее число добавлений этого рецепта в избранное')
    def added_in_favorites(self, obj):
        return obj.favourites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
