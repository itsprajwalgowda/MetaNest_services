from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from apps.apartment_master.models import Flat, Wing, Floor
from apps.people.models import Resident
from apps.finance.models.Bill import Bill
from apps.finance.models.Payment import Payment


class DashboardService:

    @staticmethod
    def get_month_range(year, month):
        """
        Return the first and last date of the given month.
        """
        start_date = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        end_date = date(year, month, last_day)

        return start_date, end_date

    @staticmethod
    def get_summary(year, month):
        """
        Get the summary information displayed in the
        four dashboard cards.
        """

        # --------------------------------------------------
        # Flat statistics
        # --------------------------------------------------

        total_flats = Flat.objects.filter(
            is_deleted=False
        ).count()

        occupied_flats = Flat.objects.filter(
            is_deleted=False,
            residents__status="Active"
        ).distinct().count()

        vacant_flats = total_flats - occupied_flats

        occupancy_percentage = (
            round((occupied_flats / total_flats) * 100)
            if total_flats
            else 0
        )

        # --------------------------------------------------
        # Apartment statistics
        # --------------------------------------------------

        total_wings = Wing.objects.filter(
            is_deleted=False
        ).count()

        total_floors = Floor.objects.filter(
            is_deleted=False
        ).count()

        # --------------------------------------------------
        # Current month
        # --------------------------------------------------

        start_date, end_date = DashboardService.get_month_range(
            year,
            month
        )

        bills = Bill.objects.filter(
            is_deleted=False,
            billing_month__gte=start_date,
            billing_month__lte=end_date
        )

        current_month_expected = bills.aggregate(
            total=Sum("total_amount")
        )["total"] or Decimal("0.00")

        current_month_collection = Payment.objects.filter(
            is_deleted=False,
            payment_status=Payment.PAYMENT_STATUS_SUCCESS,
            bill__in=bills
        ).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        current_month_outstanding = (
            current_month_expected - current_month_collection
        )

        if current_month_outstanding < Decimal("0.00"):
            current_month_outstanding = Decimal("0.00")

        # --------------------------------------------------
        # Pending flats
        # --------------------------------------------------

        pending_flats = bills.filter(
            status__in=[
                Bill.STATUS_GENERATED,
                Bill.STATUS_PARTIALLY_PAID,
                Bill.STATUS_OVERDUE,
            ]
        ).values("flat").distinct().count()

        return {
            "total_flats": total_flats,
            "occupied_flats": occupied_flats,
            "vacant_flats": vacant_flats,
            "occupancy_percentage": occupancy_percentage,
            "total_wings": total_wings,
            "total_floors": total_floors,
            "current_month_collection": current_month_collection,
            "current_month_expected": current_month_expected,
            "current_month_outstanding": current_month_outstanding,
            "pending_flats": pending_flats,
        }

    @staticmethod
    def get_monthly_collection(year, month):
        """
        Get collection and outstanding amounts
        for the last six months including the selected month.
        """

        monthly_data = []

        for offset in range(5, -1, -1):
            current_month = month - offset
            current_year = year

            while current_month <= 0:
                current_month += 12
                current_year -= 1

            while current_month > 12:
                current_month -= 12
                current_year += 1

            start_date, end_date = DashboardService.get_month_range(
                current_year,
                current_month
            )

            bills = Bill.objects.filter(
                is_deleted=False,
                billing_month__gte=start_date,
                billing_month__lte=end_date
            )

            expected = bills.aggregate(
                total=Sum("total_amount")
            )["total"] or Decimal("0.00")

            collected = Payment.objects.filter(
                is_deleted=False,
                payment_status=Payment.PAYMENT_STATUS_SUCCESS,
                bill__in=bills
            ).aggregate(
                total=Sum("amount")
            )["total"] or Decimal("0.00")

            outstanding = expected - collected

            if outstanding < Decimal("0.00"):
                outstanding = Decimal("0.00")

            monthly_data.append({
                "month": start_date.strftime("%b"),
                "collected": collected,
                "outstanding": outstanding,
            })

        return monthly_data

    @staticmethod
    def get_occupancy_by_wing():
        """
        Get occupied flat count for every active wing.
        """

        wings = Wing.objects.filter(
            is_deleted=False
        ).order_by("name")

        occupancy_data = []

        for wing in wings:
            occupied_flats = Flat.objects.filter(
                is_deleted=False,
                floor__wing=wing,
                residents__status="Active"
            ).distinct().count()

            occupancy_data.append({
                "wing": wing.name,
                "occupied_flats": occupied_flats,
            })

        return occupancy_data


    @staticmethod
    def get_recent_payments(year, month, limit=10):
        """
        Get the most recent successful payments for the dashboard.
        """
        start_date, end_date = DashboardService.get_month_range(
            year,
            month
        )
        payments = Payment.objects.filter(
            is_deleted=False,
            payment_status=Payment.PAYMENT_STATUS_SUCCESS,
            payment_date__gte=start_date,
            payment_date__lte=end_date,
        ).select_related(
            "bill",
            "bill__flat",
            "bill__flat__floor",
            "bill__flat__floor__wing",
        ).order_by(
            "-payment_date",
            "-created_at"
        )[:limit]

        payment_data = []

        for payment in payments:
            flat = payment.bill.flat

            resident = None

            if flat:
                resident = Resident.objects.filter(
                    flat=flat,
                    status="Active"
                ).order_by("id").first()

            flat_number = ""

            if flat:
                flat_number = (
                    f"{flat.floor.wing.name}-{flat.flat_number}"
                )

            payment_data.append({
                "receipt_number": payment.receipt_number,
                "flat": flat_number,
                "resident": resident.name if resident else "",
                "amount": payment.amount,
                "payment_date": payment.payment_date,
                "payment_mode": payment.payment_mode,
                "payment_status": payment.payment_status,
            })

        return payment_data

    @staticmethod
    def get_dashboard(year, month):
        """
        Get all dashboard data in one response.
        """

        return {
            "summary": DashboardService.get_summary(
                year,
                month
            ),
            "monthly_collection": DashboardService.get_monthly_collection(
                year,
                month
            ),
            "occupancy_by_wing": DashboardService.get_occupancy_by_wing(),
            "recent_payments": DashboardService.get_recent_payments(
                year,
                month
            ),  
        }