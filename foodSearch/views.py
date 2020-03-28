#!/usr/bin/env python

"""
foodSearch views
"""

from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.http import JsonResponse

from .models import Category, Favorite, Product
from .query_parser import QueryParser
from .results_parser import ResultsParser


def index(request):
    """index View"""
    return render(request, 'foodSearch/index.html')

def legals(request):
    """View rendering legals page"""
    context = {
        'title':'Mentions légales'
    }
    return render(request, 'foodSearch/legals.html', context)

def register_view(request):
    """Registration view creating a user and returning json response to ajax"""
    response_data = {}
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    try:
        user = User.objects.get(username=username)
        response_data = {'user':"already in DB"}
    except User.DoesNotExist:
        user = User.objects.create(username=username, email=email, password=password)
        user.save()
        login(request, user)
        response_data = {'user':"success"}
    return HttpResponse(JsonResponse(response_data))

def login_view(request):
    """Login view returning json response to ajax"""
    response_data = {}
    username = request.POST['username']
    password = request.POST['password']
    try:
        user = User.objects.get(username=username)
        if user.password == password:
            login(request, user)
            response_data = {'user':"success"}
        else:
            response_data = {'user':"password wrong"}
    except User.DoesNotExist:
        response_data = {'user':"user unknown"}
    return HttpResponse(JsonResponse(response_data))

def userpage(request):
    """View rendering userpage"""
    title = request.user
    context = {'title':title}
    if request.user.is_authenticated:
        username = request.user.username
        email = request.user.email
        context['username'] = username
        context['email'] = email
    return render(request, 'foodSearch/userpage.html', context)

def watchlist(request):
    """View rendering wachlist page with products saved as substitute by user"""
    current_user = request.user
    title = 'Mes aliments'
    page = request.GET.get('page')
    user_watchlist = Favorite.objects.filter(user=current_user)

    if user_watchlist.count() > 6:
        paginate = True
    else:
        paginate = False

    if paginate:
        paginator = Paginator(user_watchlist, 6)
        watchlistpage = paginator.get_page(page)
    else:
        watchlistpage = user_watchlist

    if page is None:
        page = 1

    context = {
        'page':page,
        'title':title,
        'watchlistpage':watchlistpage,
        'paginate':paginate
    }
    return render(request, 'foodSearch/watchlist.html', context)

def search(request):
    """
    View rendering search page where user confirm his search product with one in DB
    This function uses the class QueryParser from module query_parser.py
    """
    query = request.GET.get('query')
    title = query

    if query == "":
        found_products = []
    else:
        parser = QueryParser(query)
        parser.get_final_list()
        found_products = parser.product_list[0:12]

    context = {
        'title' : title,
        'found_products': found_products,
    }
    return render(request, 'foodSearch/search.html', context)

def results(request, product_id):
    """
    View rendering results page showing more relevant substitutes
    This function uses the class ResultsParser from module results_parser.py
    """
    title = Product.objects.get(id=product_id).name
    page = request.GET.get('page')
    current_user = request.user
    parser = ResultsParser(product_id, current_user)
    if page is None:
        page = 1

    context = {
        'title':title,
        'product':parser.product,
        'result': parser.paginator(page),
        'page':page,
        "paginate": parser.paginate
    }
    return render(request, 'foodSearch/results.html', context)

def detail(request, product_id):
    """View rendering detail page with product informations detail"""
    product = Product.objects.get(id=product_id)
    context = {
        'product':product
    }
    return render(request, 'foodSearch/detail.html', context)

def load_favorite(request):
    """View loading or deleting favorite row and returning a json response to ajax"""
    user = request.POST['user']
    substitute_id = request.POST['substitute']
    favorite = request.POST['favorite']
    product_id = request.POST['product']

    current_user = User.objects.get(id=user)
    if favorite == "saved":
        # delete favorite
        try:
            substitute = Product.objects.get(id=substitute_id)
            product = Product.objects.get(id=product_id)
            Favorite.objects.get(user=current_user, substitute=substitute).delete()
            favorite = "unsaved"
        except:
            print('ERROR DELETE')
    else:
        # save as favorite
        try:
            substitute = Product.objects.get(id=substitute_id)
            product = Product.objects.get(id=product_id)
            Favorite.objects.create(user=current_user,
                                    substitute=substitute,
                                    initial_search_product=product)
            favorite = "saved"
        except:
            print('ERROR SAVE')

    return HttpResponse(JsonResponse({'substitute_id': substitute_id,
                                      'product_id': product_id,
                                      'favorite': favorite}))
