from typing import DefaultDict
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.fields import related


class User(AbstractUser):
    pass


class Listing(models.Model):
    """ Represents a listing for auction. """
    # List of choices for category field
    CATEGORY_CHOICES = [
        ("fashion", "Fashion"),
        ("toys", "Toys and Games"),
        ("home_appliances", "Home Appliances"),
        ("electronics", "Electronics"),
        ("food", "Food"),
        ("others", "Others")
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_listings")
    current_bidder = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="leading_bids")
    current_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0.01)])
    is_closed = models.BooleanField(default=False)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="wins")
    watchers = models.ManyToManyField(User, blank=True, related_name="watchlist")

    title = models.CharField(max_length=32)
    description = models.CharField(max_length=128)
    starting_bid = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0.01)])
    image_url = models.URLField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Listing: {self.title} by User: {self.creator}"


class Bid(models.Model):
    """ Represents a bid for a particular `Listing`. """
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    price = models.DecimalField(max_digits=5, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bid of ${self.price} placed on {self.listing.id}: {self.listing.title}"


class Comment(models.Model):
    """ Represents a comment for a particular 'Listing'. """
    commentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment made by '{self.commentor}' on Listing '{self.listing.title}': '{self.comment}'"
