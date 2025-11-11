from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import ListingForm
from .models import AuctionListing
from .models import User


def index(request):
    listings = AuctionListing.objects.filter(is_active=True)
    
    return render(request, "auctions/index.html", {
        "listings": listings
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
def create(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        
        if form.is_valid():
            listing = form.save(commit=False)
            
            listing.creator = request.user
            listing.save()
            
            return redirect("index")
        
        else:
            return render(request, "auctions/create_listing.html", {
                "form": form
            })
            
    else:
        form = ListingForm()
        return render(request, "auctions/create_listing.html", {
            "form": form
        })
        
def listing_page(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    
    highest_bid_data = listing.bids.aggregate(Max('amount'))
    highest_bid = highest_bid_data['amount__max']
    
    if highest_bid is None:
        current_bid = listing.starting_bid
    else:
        current_bid = highest_bid
        
    return render(request, "auctions/listing.html", {
        "listing":listing,
        "current_bid":current_bid
    })
    
@login_required    
def watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    
    if request.user in listing.watchers.all():
        listing.watchers.remove(request.user)
    else:
        listing.watchers.add(request.user)
        
    return redirect("listing_page", listing_id=listing_id)