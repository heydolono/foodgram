from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from .models import Recipe

def redirect_short_link(request, short_link):
    full_short_link = f'{request.get_host()}/s/{short_link}'
    recipe = get_object_or_404(Recipe, short_link=full_short_link)
    recipe_url = f'/recipes/{recipe.id}/'
    return redirect(recipe_url)