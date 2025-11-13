from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create/", views.create, name="create"),
    path("listing/<int:listing_id>", views.listing_page, name="listing_page"),
    path("watchlist/<int:listing_id>", views.watchlist, name="watchlist"),
    path("close/<int:listing_id>", views.close_auction, name="close_auction"),
    path("won_auctions/", views.won_auctions, name="won_auctions"),
]
