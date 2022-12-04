from django import forms
from django.core.validators import MinValueValidator

from .models import Bid, Listing, Comment


class CreateListingForm(forms.ModelForm):
    """
    Form for user to create a new listing.
    Data stored in `Listing` model.
    """
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid", "image_url", "category"]
        widgets = {
            "starting_bid": forms.NumberInput(attrs={'step': 0.50}),
        }
        labels = {
            "image_url": "Image URL"
        }
        help_texts = {
            "description": "Provide a short description of your listing",
            "starting_bid": "Enter the minimum bid (in $)",
            "image_url": "(optional) Provide a URL to an image for your listing",
            "category": "Select the category of your listing."
        }


class NewBidForm(forms.ModelForm):
    """
    Form for user to create a new bid for a particular listing.
    Data stored in `Bid` model.
    Ensure any new bid is higher than the current one.
    """
    class Meta:
        model = Bid
        fields = ["bidder", "listing", "price"]
        widgets = {
            "bidder": forms.HiddenInput(),
            "listing": forms.HiddenInput()
        }

    # should min_bid be validated in form or in views??
    def __init__(self, *args, **kwargs):
        # Dynamically validate form to reflect current bid price
        min_bid = kwargs.pop("min_bid")
        super(NewBidForm, self).__init__(*args, **kwargs)
        self.fields["price"].validators = [MinValueValidator(min_bid, message="Enter a bid higher than the current price.")]


class NewCommentForm(forms.ModelForm):
    """
    Form for user to add a new comment for any listing.
    """
    class Meta:
        model = Comment
        fields = ["comment"]
