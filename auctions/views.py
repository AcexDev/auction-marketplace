from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Auction
from .serializers import AuctionSerializer
from .permissions import IsOwnerOrAdmin


class AuctionViewSet(viewsets.ModelViewSet):
    serializer_class = AuctionSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        queryset = Auction.objects.all()
        status_filter = self.request.query_params.get('status', None)

        if status_filter:
            return queryset.filter(status=status_filter)

        # Default: active auctions for everyone, but owners can see their own cancelled
        return queryset.filter(status=Auction.Status.ACTIVE)

    def check_and_complete(self, auction):
        print(f"is_expired: {auction.is_expired}")
        print(f"end_time: {auction.end_time}")
        print(f"now: {timezone.now()}")
        print(f"status: {auction.status}")
        if auction.is_expired:
            highest_bid = auction.bids.order_by('-amount').first()
            auction.status = Auction.Status.COMPLETED
            if highest_bid:
                auction.winner = highest_bid.bidder
            auction.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_and_complete(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        for auction in queryset:
            self.check_and_complete(auction)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == Auction.Status.ACTIVE:
            instance.status = Auction.Status.CANCELLED
            instance.save()
            return Response({"message": "Auction cancelled."}, status=status.HTTP_200_OK)
        return Response(
            {"error": "Only active auctions can be cancelled."},
            status=status.HTTP_400_BAD_REQUEST
        )