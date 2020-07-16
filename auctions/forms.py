from django.forms import ModelForm, Textarea
from auctions.models import Listings, Bids


class ListingForm(ModelForm):
    class Meta:
        model = Listings
        fields = ['title', 'description', 'starting_bid', 'image_url', 'category']
        widgets = {
            'description': Textarea(attrs={'cols': 40, 'rows': 6}),
        }


class BidForm(ModelForm):
    class Meta:
        model = Bids
        fields = ['value_offer']