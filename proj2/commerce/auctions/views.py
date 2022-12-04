from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django import forms

from .models import User, Listing, Comment
from .forms import CreateListingForm, NewBidForm, NewCommentForm


def index(request):
    """
    Default view for auctions app.
    Display all active listings.
    """
    # Obtain all currently active listings
    active_listings = Listing.objects.exclude(is_closed=True)
    return render(request, "auctions/index.html", {"active_listings": active_listings})


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
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        # If user is already logged in, redirect to home page
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))
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
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="/login")
def create(request):
    """Create a new listing."""
    if request.method == "POST":
        # Populate form
        form = CreateListingForm(request.POST)
        if form.is_valid():
            # Reference the new `Listing` to the current `User`
            new_listing = form.save(commit=False)
            new_listing.creator = request.user
            new_listing.current_price = new_listing.starting_bid
            new_listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", {"form": form})
    else:
        return render(request, "auctions/create.html", {"form": CreateListingForm()})


def listing(request, listing_id):
    """
    Responsible for loading pages specific to each listing.
    If user is signed in, they should be able to add item to watchlist and make bids.
    If user created listing, they should be able to close it.
    If user signed in on a closed listing, they win if they have the highest current bid.
    If user is signed in, they should be able to make comments which are displayed.
    """
    # Retrieve info on the given listing
    listing = Listing.objects.get(pk=listing_id)
    current_price = listing.current_price

    # Creator view - creators can close their listings
    if request.user == listing.creator:

        # Creator closed listing via form (press submit button)
        if request.method == "POST":
            form = forms.Form(request.POST)
            if form.is_valid():
                # Update fields for `listing` model instance
                listing.is_closed = True
                listing.winner = listing.current_bidder
                listing.current_bidder = None
                listing.save()
                return HttpResponseRedirect(reverse("index"))

        # Display form to close listing
        else:
            return render(request, "auctions/listing.html", {"listing": listing})

    # Default non-creator view - users can make bids or add to watchlist
    else:

        # If listing is closed, check for winner
        if listing.is_closed:
            return render(request, "auctions/listing.html", {"listing": listing})

        # Normal bidding view for non-winners and non-creators
        # User submitted bid form
        if request.method == "POST":
            form = NewBidForm(request.POST, min_bid=current_price)
            if form.is_valid():
                # Save NewBidForm to Bid model
                new_bid = form.save()
                # Update listing with current price and bidder
                if new_bid.price > listing.current_price:
                    listing.current_price = new_bid.price
                    listing.current_bidder = new_bid.bidder
                    listing.save()
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(
                    request, "auctions/listing.html", {"listing": listing, "form": form}
                )

        # User accessing bid form
        else:
            form = NewBidForm(
                initial={"bidder": request.user, "listing": listing},
                min_bid=current_price,
            )

            return render(
                request, "auctions/listing.html", {"listing": listing, "form": form}
            )


@login_required(login_url="/login")
def user_profile(request):
    """
    User profile that displays their wins, leading bids, created listings and history of bids.
    """
    return render(request, "auctions/user_profile.html", {"user": request.user})


@login_required(login_url="/login")
def watchlist(request):
    """
    View that saves a user's watchlist (if POST),
    or displays a list of their watchlist (if GET).
    """
    # User pressed "add/remove watchlist" button from listing page
    if request.method == "POST":
        # Get the current listing
        listing_id = request.POST.get("listing_id")
        listing = Listing.objects.get(id=listing_id)

        # Check if item is to be added or removed
        if request.POST.get("watchlist") == "add":
            listing.watchers.add(request.user)
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
        elif request.POST.get("watchlist") == "remove":
            listing.watchers.remove(request.user)
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

    # User accessing his watchlist page
    else:
        # Remove all watchers from closed listings
        closed_listings = Listing.objects.filter(is_closed=True)
        for listing in closed_listings:
            listing.watchers.clear()

        return render(
            request,
            "auctions/watchlist.html",
            {"watchlist": request.user.watchlist.all()},
        )


@login_required(login_url="/login")
def comment(request, listing_id):
    """
    View that saves a new comment for a particular listing.
    """
    # Ensure comment is submitted via form
    if request.method == "POST":
        # Populate form
        form = NewCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.commentor = request.user
            comment.listing = Listing.objects.get(pk=listing_id)
            comment.save()
            # Return to listing page to view new comments
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        else:
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    # Ignore any requests to url '/comment/<int:listing_id>'
    else:
        return redirect("index")
