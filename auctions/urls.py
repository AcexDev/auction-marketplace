from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuctionViewSet
from bids.views import PlaceBidView, AuctionBidListView

router = DefaultRouter()
router.register(r'auctions', AuctionViewSet, basename='auction')

urlpatterns = [
    path('', include(router.urls)),
    path('auctions/<uuid:auction_id>/bids/', AuctionBidListView.as_view(), name='auction-bids'),
    path('auctions/<uuid:auction_id>/bids/place/', PlaceBidView.as_view(), name='place-bid'),
]