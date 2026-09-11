from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    total_flats = serializers.IntegerField()
    occupied_flats = serializers.IntegerField()
    vacant_flats = serializers.IntegerField()
    occupancy_percentage = serializers.IntegerField()
    total_wings = serializers.IntegerField()
    total_floors = serializers.IntegerField()
    current_month_collection = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    current_month_expected = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    current_month_outstanding = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    pending_flats = serializers.IntegerField()


class MonthlyCollectionSerializer(serializers.Serializer):
    month = serializers.CharField()
    collected = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    outstanding = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )


class OccupancyByWingSerializer(serializers.Serializer):
    wing = serializers.CharField()
    occupied_flats = serializers.IntegerField()


class RecentPaymentSerializer(serializers.Serializer):
    receipt_number = serializers.CharField()
    flat = serializers.CharField()
    resident = serializers.CharField()
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    payment_date = serializers.DateField()
    payment_mode = serializers.CharField()
    payment_status = serializers.CharField()


class DashboardSerializer(serializers.Serializer):
    summary = DashboardSummarySerializer()
    monthly_collection = MonthlyCollectionSerializer(many=True)
    occupancy_by_wing = OccupancyByWingSerializer(many=True)
    recent_payments = RecentPaymentSerializer(many=True)