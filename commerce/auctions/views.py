from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import ListingForm
from .models import AuctionListing, Bid, User


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
        
    if request.method == "POST":
        bid_amount = request.POST.get("bid_amount")
        
        if not bid_amount:
            messages.error(request, "Please enter your Bid Amount.")
            return redirect("listing_page", listing_id=listing_id)
        
        try:
            bid_amount = float(bid_amount)
            
            if bid_amount < current_bid:
                messages.error(request, f"Your Bid must be atleast ${current_bid}.")
            elif highest_bid is None and bid_amount < listing.starting_bid:
                messages.error(request, f"Your Bid must be atleast ${listing.starting_bid}.")
            else:
                #Created new_bid object here
                new_bid = Bid(
                    bidder = request.user,
                    listing = listing,
                    amount = bid_amount
                )
                new_bid.save()
                messages.success(request, "Your Bid has been placed!")
                
                current_bid = bid_amount
        
        except ValueError:
            messages.error(request, "Invalid Bid. Please enter a valid number.")
            
        return redirect("listing_page", listing_id=listing_id)
        
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

@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    
    if request.user != listing.creator:
        messages.error(request, "You are not allowed to close the listing.")
        return redirect("listing_page", listing_id=listing.id)
    
    if not listing.is_active:
        messages.error(request, "The listing is no longer active.")
        return redirect("listing_page", listing_id=listing.id)
    
    highest_bid = listing.bids.order_by('-amount').first()
    
    if highest_bid is not None:
        listing.is_active = False
        listing.winner = highest_bid.bidder
        listing.save()
        messages.success(request, f"Auction Closed! Congratulations {highest_bid.bidder.username}, You are the Winner!")
    else:
        listing.is_active = False
        listing.save()
        messages.success(request, "Auction closed with No Bids!")
    
    return redirect("listing_page", listing_id=listing.id)

@login_required
def won_auctions(request):
    won_listings = AuctionListing.objects.filter(winner=request.user)
    
    return render(request, "auctions/won_auctions.html", {
        "listings": won_listings
    })