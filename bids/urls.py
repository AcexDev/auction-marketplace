from django.urls import path
from .views import UserBidListView


urlpatterns = [   
    path('bids/my-bids/', UserBidListView.as_view(), name='my-bids'),
]