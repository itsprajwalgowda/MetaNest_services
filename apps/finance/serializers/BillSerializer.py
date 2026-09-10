from decimal import Decimal

from rest_framework import serializers
from django.db.models import Sum

from apps.finance.models.Bill import Bill
from apps.finance.models.Payment import Payment


class BillSerializer(serializers.ModelSerializer):

    paid_amount = serializers.SerializerMethodField()
    balance_amount = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = [
            "id",
            "flat",
            "billing_month",
            "due_date",
            "base_charge",
            "area_charge",
            "water_charge",
            "parking_charge",
            "sinking_fund",
            "other_charge",
            "principal_amount",
            "late_fee",
            "total_amount",
            "paid_amount",
            "balance_amount",
            "status",
            "generated_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "due_date",
            "base_charge",
            "water_charge",
            "parking_charge",
            "sinking_fund",
            "other_charge",
            "principal_amount",
            "late_fee",
            "total_amount",
            "paid_amount",
            "balance_amount",
            "status",
            "generated_at",
            "created_at",
            "updated_at",
        ]

    def get_paid_amount(self, obj):
        paid_amount = Payment.objects.filter(
            bill=obj,
            payment_status=Payment.PAYMENT_STATUS_SUCCESS,
            is_deleted=False,
        ).aggregate(
            total=Sum("amount")
        )["total"]

        return paid_amount or Decimal("0.00")

    def get_balance_amount(self, obj):
        paid_amount = self.get_paid_amount(obj)

        balance = obj.total_amount - paid_amount

        if balance < Decimal("0.00"):
            balance = Decimal("0.00")

        return balance