from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes.models import (Favourite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe

from .filters import RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (AvatarSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipePostSerializer,
                          RecipeSerializer, RecipeShortSerializer,
                          SubscribeSerializer, TagSerializer)

User = get_user_model()


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RecipeFilter
    ordering_fields = ["id"]
    ordering = ["-id"]
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        self.request.user.save()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipePostSerializer

    @action(detail=True, methods=["get"],
            url_path="get-link", url_name="get-link")
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = recipe.short_link
        if not short_link:
            return Response(
                {"error": "Короткая ссылка не существует."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"short-link": short_link})

    def handle_favorite_or_shopping_cart(
        self, request, pk, model, error_message_added, error_message_removed
    ):
        if request.method == "POST":
            if model.objects.filter(user=request.user, recipe__id=pk).exists():
                return Response(
                    {"errors": error_message_added},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            recipe = get_object_or_404(Recipe, id=pk)
            model.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        obj = model.objects.filter(user=request.user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"errors": error_message_removed},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="favorite",
        url_name="favorite",
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        return self.handle_favorite_or_shopping_cart(
            request, pk, Favourite,
            "Рецепт уже был добавлен", "Рецепт уже был удален"
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="shopping_cart",
        url_name="shopping_cart",
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        return self.handle_favorite_or_shopping_cart(
            request,
            pk,
            ShoppingCart,
            "Рецепт уже был добавлен",
            "Рецепт уже был удален",
        )

    @action(detail=False, methods=["get"],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(
                {"errors": "Корзина покупок пуста"},
                status=status.HTTP_400_BAD_REQUEST
            )
        ingredients = (
            IngredientRecipe.objects.filter(
                recipe__shopping_cart__user=request.user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
        )
        shopping_list = "Список покупок \n"
        shopping_items = []
        for ingredient in ingredients:
            item = (
                f'- {ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f' - {ingredient["total_amount"]}'
            )
            shopping_items.append(item)

        shopping_list += "\n".join(shopping_items)
        response = HttpResponse(shopping_list, content_type="text/plain")
        filename = f"{user.username}_shopping_list.txt"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ["get"]
    pagination_class = None


def redirect_short_link(request, short_link):
    full_short_link = f"{request.get_host()}/s/{short_link}"
    recipe = get_object_or_404(Recipe, short_link=full_short_link)
    recipe_url = f"/recipes/{recipe.id}/"
    return redirect(recipe_url)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="subscribe",
        url_name="subscribe",
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, **kwargs):
        author_id = self.kwargs.get("id")
        author = get_object_or_404(User, id=author_id)

        if request.method == "POST":
            Subscribe.objects.create(user=request.user, author_id=author_id)
            serializer = SubscribeSerializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = get_object_or_404(
            Subscribe, user=request.user, author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], 
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscriptions_sent__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages,
                                         many=True, 
                                         context={"request": request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["put", "delete"],
        permission_classes=[IsAuthenticated],
        url_path="me/avatar",
    )
    def avatar(self, request):
        user = request.user

        if request.method == "PUT":
            serializer = AvatarSerializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.update(user, serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        user.avatar.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
