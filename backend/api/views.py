from django.db.models import Sum
from django.http import HttpResponse
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import RedirectView
from recipes.models import (Favourite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .pagination import CustomPagination
from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeShortSerializer, RecipePostSerializer,
                          TagSerializer, FavoriteCreateSerializer)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RecipeFilter
    ordering_fields = ['id']
    ordering = ['-id']
    pagination_class = CustomPagination
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        self.request.user.save()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipePostSerializer

    @action(detail=True, methods=['get'], url_path='get-link', url_name='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = recipe.short_link
        if not short_link:
            return Response({'error': 'Короткая ссылка не существует.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'short-link': short_link})

    @action(detail=True, methods=['post', 'delete'], url_path='favorite',
            url_name='favorite', permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        if request.method == 'POST':
            serializer = FavoriteCreateSerializer(data={'recipe': pk}, context={'request': request})
            if Favourite.objects.filter(user=request.user, recipe__id=pk).exists():
                return Response({'errors': 'Рецепт уже был добавлен'}, status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, id=pk)
            Favourite.objects.create(user=request.user, recipe=recipe)
            serializerrec = RecipeShortSerializer(recipe)
            return Response(serializerrec.data, status=status.HTTP_201_CREATED)
        else:
            serializer = FavoriteCreateSerializer(data={'recipe': pk}, context={'request': request})
            obj = Favourite.objects.filter(user=request.user, recipe__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт уже был удален'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart',
            url_name='shopping_cart', permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=request.user, recipe__id=pk).exists():
                return Response({'errors': 'Рецепт уже был добавлен'}, status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, id=pk)
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            obj = ShoppingCart.objects.filter(user=request.user, recipe__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт уже был удален'}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response({'errors': 'Корзина покупок пуста'}, status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientRecipe.objects.filter(recipe__shopping_cart__user=request.user).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_list = 'Список покупок \n'
        shopping_items = []
        for ingredient in ingredients:
            item = f'- {ingredient["ingredient__name"]} ({ingredient["ingredient__measurement_unit"]}) - {ingredient["amount"]}'
            shopping_items.append(item)

        shopping_list += '\n'.join(shopping_items)
        response = HttpResponse(shopping_list, content_type='text/plain')
        filename = f'{user.username}_shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    pagination_class = None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    

class TagListView(APIView):
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)


