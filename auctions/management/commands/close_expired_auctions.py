from django.core.management.base import BaseCommand
from django.utils import timezone
from auctions.models import Auction
from bids.models import Bid


class Command(BaseCommand):
    help = 'Closes all expired auctions and assigns winners'

    def handle(self, *args, **kwargs):
        expired_auctions = Auction.objects.filter(
            status=Auction.Status.ACTIVE,
            end_time__lt=timezone.now()
        )

        closed_count = 0

        for auction in expired_auctions:
            highest_bid = auction.bids.order_by('-amount').first()
            auction.status = Auction.Status.COMPLETED
            if highest_bid:
                auction.winner = highest_bid.bidder
            auction.save()
            closed_count += 1
            self.stdout.write(f"Closed: {auction.title}")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully closed {closed_count} expired auctions.")
        )