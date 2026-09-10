from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from apps.finance.models.Bill import Bill
from apps.finance.models.Payment import Payment


class PaymentService:

    @staticmethod
    @transaction.atomic
    def create_payment(
        bill,
        amount,
        payment_date,
        payment_mode,
        transaction_reference=None,
    ):
        if bill.status == Bill.STATUS_PAID:
            raise ValueError(
                "Bill is already fully paid."
            )

        amount = Decimal(amount)

        if amount <= 0:
            raise ValueError(
                "Payment amount must be greater than zero."
            )

        total_paid = Payment.objects.filter(
            bill=bill,
            payment_status=Payment.PAYMENT_STATUS_SUCCESS,
            is_deleted=False,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        outstanding_amount = (
            bill.total_amount - total_paid
        )

        if amount > outstanding_amount:
            raise ValueError(
                "Payment amount cannot exceed outstanding amount."
            )

        receipt_number = PaymentService.generate_receipt_number()

        payment = Payment.objects.create(
            bill=bill,
            receipt_number=receipt_number,
            amount=amount,
            payment_date=payment_date,
            payment_mode=payment_mode,
            payment_status=Payment.PAYMENT_STATUS_SUCCESS,
            transaction_reference=transaction_reference,
        )

        new_total_paid = total_paid + amount

        if new_total_paid == bill.total_amount:
            bill.status = Bill.STATUS_PAID
        else:
            bill.status = Bill.STATUS_PARTIALLY_PAID

        bill.save(update_fields=["status", "updated_at"])

        return payment

    @staticmethod
    def get_all_payments():
        return Payment.objects.filter(
            is_deleted=False
        ).select_related("bill").order_by("-payment_date", "-created_at")
    
    @staticmethod
    def generate_receipt_number():
        import uuid

        return f"REC-{uuid.uuid4().hex[:10].upper()}"