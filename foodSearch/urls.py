from django.urls import path, re_path

from . import views # import views so we can use them in urls.

app_name = 'foodSearch'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('search/', views.search, name='search'),
    path('results/<int:product_id>/', views.results, name='results'),
    path('detail/<int:product_id>/', views.detail, name='detail'),
    path('userpage/', views.userpage, name='userpage'),
    path('load_favorite/', views.load_favorite, name='load_favorite'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('legals/', views.legals, name='legals'),
]
