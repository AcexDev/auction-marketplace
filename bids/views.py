from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from auctions.models import Auction
from .models import Bid
from .serializers import BidSerializer


class PlaceBidView(generics.CreateAPIView):
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_auction(self):
        return get_object_or_404(Auction, id=self.kwargs['auction_id'])

    def create(self, request, *args, **kwargs):
        auction = self.get_auction()

        # Check auction is active
        if auction.status != Auction.Status.ACTIVE:
            return Response(
                {"error": "This auction is not active."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check auction is not expired
        if auction.is_expired:
            auction.status = Auction.Status.COMPLETED
            auction.save()
            return Response(
                {"error": "This auction has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Owner cannot bid on their own auction
        if auction.owner == request.user:
            return Response(
                {"error": "You cannot bid on your own auction."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'auction': auction}
        )
        serializer.is_valid(raise_exception=True)

        # Save bid and update auction current price
        bid = serializer.save(bidder=request.user, auction=auction)
        auction.current_price = bid.amount
        auction.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AuctionBidListView(generics.ListAPIView):
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        auction_id = self.kwargs['auction_id']
        return Bid.objects.filter(auction_id=auction_id)
    
class UserBidListView(generics.ListAPIView):
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bid.objects.filter(bidder=self.request.user)