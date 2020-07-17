from django.contrib import admin

# Register your models here.
from auctions.models import Listings, Comments, Bids, User

admin.site.register(Listings)
admin.site.register(Comments)
admin.site.register(Bids)
admin.site.register(User)