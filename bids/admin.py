from django.contrib import admin
from .models import Bid


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['bidder', 'auction', 'amount', 'created_at']
    search_fields = ['bidder__email', 'auction__title']
    readonly_fields = ['id', 'created_at']