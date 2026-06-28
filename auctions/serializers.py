from rest_framework import serializers
from .models import Auction


class AuctionSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Auction
        fields = [
        'id', 'owner', 'title', 'description',
        'starting_price', 'current_price', 'end_time',
        'status', 'winner', 'created_at', 'updated_at'
    ]
    read_only_fields = ['id', 'owner', 'current_price', 'status', 'winner', 'created_at', 'updated_at']

    def validate_end_time(self, value):
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("End time must be in the future.")
        return value

    def create(self, validated_data):
        validated_data['current_price'] = validated_data['starting_price']
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)