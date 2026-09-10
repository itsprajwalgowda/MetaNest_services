import uuid

from django.db import models


class Bill(models.Model):

    STATUS_GENERATED = "GENERATED"
    STATUS_PARTIALLY_PAID = "PARTIALLY_PAID"
    STATUS_PAID = "PAID"
    STATUS_OVERDUE = "OVERDUE"

    STATUS_CHOICES = [
        (STATUS_GENERATED, "Generated"),
        (STATUS_PARTIALLY_PAID, "Partially Paid"),
        (STATUS_PAID, "Paid"),
        (STATUS_OVERDUE, "Overdue"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    flat = models.ForeignKey(
        "apartment_master.Flat",
        on_delete=models.PROTECT,
        related_name="bills",
        null=True,
        blank=True,
    )

    # Billing Information
    billing_month = models.DateField()

    due_date = models.DateField()

    # Maintenance Charges
    base_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    area_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    water_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    parking_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    sinking_fund = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    other_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # Bill Amounts
    principal_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    late_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_GENERATED
    )

    generated_at = models.DateTimeField( 
        auto_now_add=True
    )

    # Common Fields
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    is_deleted = models.BooleanField(
        default=False
    )