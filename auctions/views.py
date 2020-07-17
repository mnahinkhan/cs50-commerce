from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import ListingForm, BidForm
from .models import User, Listings, Bids, Comments


def index(request):
    return render(request, "auctions/index.html", {
        'listings': Listings.objects.filter(closed=False),
        'title': 'Active Listings'
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        try:
            new_listing = form.save(commit=False)
            assert request.user.is_authenticated
            new_listing.owner = request.user
            new_listing.save()
            messages.success(request, "Thanks, your listing has been saved!")
            return HttpResponseRedirect(reverse("index"))

        except ValueError:
            # Form was not valid, let's just return it back to the user so they can fix it
            pass

    else:
        form = ListingForm()
    return render(request, "auctions/create-listing.html", {
        "form": form
    })


def listing_page(request, listing_id, bid_form=None):

    listing = Listings.objects.get(pk=listing_id)
    print(listing.closed)
    if request.user.is_authenticated:
        is_watch_list = request.user.watchlist_items.filter(pk=listing_id).exists()

        # if bid form was passed to us already, we likely want to produce an error from create bid route.
        if not bid_form:
            bid_form = BidForm()

        is_mine = listing.owner == request.user
    else:
        is_watch_list = None
        bid_form = None
        is_mine = None

    return render(request, "auctions/listing.html", {
        'listing': listing,
        'is_watchlist': is_watch_list,
        'form': bid_form,
        'is_mine': is_mine
    })


@login_required
def watchlist_action(request, listing_id):
    if request.method == "POST":
        assert request.user.is_authenticated
        user = request.user
        listing = Listings.objects.get(pk=listing_id)
        if user.watchlist_items.filter(pk=listing_id).exists():
            user.watchlist_items.remove(listing)
        else:
            user.watchlist_items.add(listing)
    return HttpResponseRedirect(reverse("listing page", args=(listing_id,)))


@login_required
def create_bid(request, listing_id):
    if request.method == "POST":
        listing = Listings.objects.get(pk=listing_id)
        bid = Bids(user=request.user, listing=listing)
        bid_form = BidForm(request.POST, instance=bid)
        if bid_form.is_valid():
            bid_form.save()
            messages.success(request, "Thanks, your bid has been successfully made!")
        else:
            return listing_page(request, listing_id, bid_form=bid_form)

    return HttpResponseRedirect(reverse("listing page", args=(listing_id,)))


@login_required
def close_listing(request, listing_id):
    if request.method == "POST":
        assert request.user.is_authenticated
        listing = Listings.objects.get(pk=listing_id)
        print(request.user)
        print(listing.owner)
        print(listing.owner == request.user)
        if request.user == listing.owner:
            listing.closed = True
            listing.save()
    return HttpResponseRedirect(reverse("listing page", args=(listing_id,)))


@login_required
def make_comment(request, listing_id):
    if request.method == "POST":
        assert request.user.is_authenticated
        listing = Listings.objects.get(pk=listing_id)
        comment_content = request.POST['comment']
        comment = Comments(author=request.user, listing=listing, content=comment_content)
        comment.save()
    return HttpResponseRedirect(reverse("listing page", args=(listing_id,)))


def filtered_index(request, category):
    return render(request, "auctions/index.html", {
        'listings': Listings.objects.filter(closed=False, category=category),
        'title': f'Active listings under "{category}"'
    })


@login_required
def watchlist_page(request):
    assert request.user.is_authenticated
    return render(request, "auctions/index.html", {
        'listings': request.user.watchlist_items.all(),
        'title': "Watchlist Items"
    })


def category_listing_page(request):

    categories = list(set([listing.category for listing in Listings.objects.all() if listing.category]))
    print(categories)
    return render(request, "auctions/categories.html", {
        'categories': categories
    })
