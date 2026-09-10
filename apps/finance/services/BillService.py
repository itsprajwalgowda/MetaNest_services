from decimal import Decimal

from django.utils import timezone

from apps.finance.models.Bill import Bill
from apps.finance.models.MaintenanceConfiguration import MaintenanceConfiguration
from apps.apartment_master.models import Flat


class BillService:

    @staticmethod
    def generate_bill(billing_month, area_charge, flat_id):
        configuration = MaintenanceConfiguration.objects.filter(
            is_deleted=False
        ).first()

        if not configuration:
            raise ValueError(
                "Maintenance configuration not found."
            )

        try:
            flat = Flat.objects.get(
                id=flat_id,
                is_deleted=False,
            )
        except Flat.DoesNotExist:
            raise ValueError(
                "Flat not found."
            )

        base_charge = configuration.base_charge
        water_charge = configuration.water_charge
        parking_charge = configuration.parking_charge
        sinking_fund = configuration.sinking_fund
        other_charge = configuration.other_charge

        principal_amount = (
            base_charge
            + Decimal(area_charge)
            + water_charge
            + parking_charge
            + sinking_fund
            + other_charge
        )

        total_amount = principal_amount

        due_date = billing_month.replace(
            day=configuration.due_day
        )

        bill = Bill.objects.create(
            flat=flat,
            billing_month=billing_month,
            due_date=due_date,
            base_charge=base_charge,
            area_charge=area_charge,
            water_charge=water_charge,
            parking_charge=parking_charge,
            sinking_fund=sinking_fund,
            other_charge=other_charge,
            principal_amount=principal_amount,
            late_fee=Decimal("0.00"),
            total_amount=total_amount,
            status=Bill.STATUS_GENERATED,
            generated_at=timezone.now(),
        )

        return bill

    @staticmethod
    def get_all_bills():
        return Bill.objects.filter(
            is_deleted=False
        ).order_by("-created_at")