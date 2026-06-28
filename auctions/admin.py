from django.contrib import admin
from .models import Auction


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'status', 'starting_price', 'current_price', 'end_time', 'created_at']
    list_filter = ['status']
    search_fields = ['title', 'owner__email']
    readonly_fields = ['id', 'created_at', 'updated_at']