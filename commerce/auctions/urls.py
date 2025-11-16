from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create/", views.create, name="create"),
    path("listing/<int:listing_id>/", views.listing_page, name="listing_page"),
    path("watchlist_toggle/<int:listing_id>/", views.watchlist_toggle, name="watchlist_toggle"),
    path("close/<int:listing_id>/", views.close_auction, name="close_auction"),
    path("won_auctions/", views.won_auctions, name="won_auctions"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("categories/", views.categories_list, name="categories_list"),
    path("category/<str:category_name>/", views.category_page, name="category_page"),
]
