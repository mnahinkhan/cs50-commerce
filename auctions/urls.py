from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-listing", views.create_listing, name="create listing"),
    path("listing-page/<int:listing_id>", views.listing_page, name="listing page"),
    path("watchlist-action/<int:listing_id>", views.watchlist_action, name="watchlist action"),
    path("create-bid/<int:listing_id>", views.create_bid, name="create bid")
]
