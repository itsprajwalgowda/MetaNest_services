from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.finance.models import LateFeeHistory
from apps.finance.models.Bill import Bill
from apps.finance.models.MaintenanceConfiguration import (
    MaintenanceConfiguration,
)
from apps.finance.models.Payment import Payment

class LateFeeService:

    @staticmethod
    def calculate_late_fee(bill):
        """
        Calculate late fee for a bill based on
        the configured grace period and late fee rules.
        """

        configuration = MaintenanceConfiguration.objects.filter(
            is_deleted=False
        ).first()

        if not configuration:
            raise ValueError(
                "Maintenance configuration not found."
            )

        today = timezone.localdate()

        # No late fee before or on due date
        if today <= bill.due_date:
            return Decimal("0.00")

        overdue_days = (
            today - bill.due_date
        ).days

        # Grace period
        chargeable_days = (
            overdue_days - configuration.grace_period_days
        )

        if chargeable_days <= 0:
            return Decimal("0.00")

        late_fee = (
            Decimal(chargeable_days)
            * configuration.late_fee_per_day
        )

        # Apply maximum late fee limit
        if late_fee > configuration.maximum_late_fee:
            late_fee = configuration.maximum_late_fee

        return late_fee


    @staticmethod
    def apply_late_fee(bill):
        """
        Calculate and apply late fee to a bill.
        Preserves existing late fee waivers and prevents duplicate application.
        """

        from apps.finance.models.LateFeeHistory import LateFeeHistory

        late_fee = LateFeeService.calculate_late_fee(bill)

        # No late fee applicable
        if late_fee <= Decimal("0.00"):
            return bill

        # Get all late fee history records for this bill
        histories = LateFeeHistory.objects.filter(
            bill=bill,
            is_deleted=False
        )

        # Calculate total amount already waived
        total_waived = histories.aggregate(
            total=Sum("waived_amount")
        )["total"] or Decimal("0.00")

        # Calculate remaining late fee after waivers
        effective_late_fee = late_fee - total_waived

        if effective_late_fee < Decimal("0.00"):
            effective_late_fee = Decimal("0.00")

        # Prevent duplicate application
        if bill.late_fee == effective_late_fee:
            return bill

        bill.late_fee = effective_late_fee
        bill.total_amount = (
            bill.principal_amount + bill.late_fee
        )

        if bill.status != Bill.STATUS_PAID:
            bill.status = Bill.STATUS_OVERDUE

        bill.save(
            update_fields=[
                "late_fee",
                "total_amount",
                "status",
                "updated_at",
            ]
        )

        # Create history only if this bill has no previous history
        if not histories.exists():
            LateFeeHistory.objects.create(
                bill=bill,
                principal_amount=bill.principal_amount,
                late_fee_amount=late_fee,
                waived_amount=Decimal("0.00"),
                total_amount=bill.total_amount,
            )

        return bill

    @staticmethod
    def get_late_fee_history():
        from apps.finance.models.LateFeeHistory import LateFeeHistory

        return LateFeeHistory.objects.filter(
            is_deleted=False
        ).select_related(
            "bill"
        ).order_by(
            "-created_at"
        )

    @staticmethod
    @transaction.atomic
    def waive_late_fee(history_id, waived_amount, waiver_reason):

        from apps.finance.models.LateFeeHistory import LateFeeHistory

        history = LateFeeHistory.objects.filter(
            id=history_id,
            is_deleted=False
        ).select_related("bill").first()

        if not history:
            raise ValueError(
                "Late fee history not found."
            )

        waived_amount = Decimal(waived_amount)

        if waived_amount <= Decimal("0.00"):
            raise ValueError(
                "Waived amount must be greater than zero."
            )

        if waived_amount > history.late_fee_amount:
            raise ValueError(
                "Waived amount cannot exceed late fee amount."
            )

        if history.waived_amount > Decimal("0.00"):
            raise ValueError(
                "Late fee has already been waived."
            )

        bill = history.bill

        # Update history
        history.waived_amount = waived_amount
        history.waiver_reason = waiver_reason
        history.waived_at = timezone.now()

        history.total_amount = (
            history.principal_amount
            + history.late_fee_amount
            - waived_amount
        )

        history.save(
            update_fields=[
                "waived_amount",
                "waiver_reason",
                "waived_at",
                "total_amount",
                "updated_at",
            ]
        )

        # Update bill
        bill.late_fee = bill.late_fee - waived_amount

        if bill.late_fee < Decimal("0.00"):
            bill.late_fee = Decimal("0.00")

        bill.total_amount = (
            bill.principal_amount + bill.late_fee
        )

        # Calculate total paid
        total_paid = Payment.objects.filter(
            bill=bill,
            payment_status=Payment.PAYMENT_STATUS_SUCCESS,
            is_deleted=False,
        ).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        # Determine bill status
        if total_paid >= bill.total_amount:
            bill.status = Bill.STATUS_PAID

        elif total_paid > Decimal("0.00"):
            bill.status = Bill.STATUS_PARTIALLY_PAID

        else:
            bill.status = Bill.STATUS_OVERDUE

        bill.save(
            update_fields=[
                "late_fee",
                "total_amount",
                "status",
                "updated_at",
            ]
        )

        return history