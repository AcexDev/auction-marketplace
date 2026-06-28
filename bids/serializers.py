from rest_framework import serializers
from .models import Bid


class BidSerializer(serializers.ModelSerializer):
    bidder = serializers.StringRelatedField(read_only=True)
    auction = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Bid
        fields = ['id', 'auction', 'bidder', 'amount', 'created_at']
        read_only_fields = ['id', 'auction', 'bidder', 'created_at']

    def validate_amount(self, value):
        auction = self.context.get('auction')
        if value <= auction.current_price:
            raise serializers.ValidationError(
                f"Bid must be greater than current price of {auction.current_price}."
            )
        return value