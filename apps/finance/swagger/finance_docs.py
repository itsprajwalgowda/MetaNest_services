from decimal import Decimal

from drf_spectacular.utils import (
    OpenApiResponse,
    inline_serializer,
)

from rest_framework import serializers

from apps.finance.serializers.MaintenanceConfigurationSerializer import (
    MaintenanceConfigurationSerializer,
)
from apps.finance.serializers.BillSerializer import BillSerializer
from apps.finance.serializers.PaymentSerializer import PaymentSerializer
from apps.finance.serializers.LateFeeHistorySerializer import (
    LateFeeHistorySerializer,
)


MAINTENANCE_CONFIGURATION_DOCS = {
    "summary": "Get Maintenance Configuration",
    "description": (
        "Fetch the current global maintenance configuration. "
        "The configuration is applicable to future bills only."
    ),
    "responses": {
        200: MaintenanceConfigurationSerializer,
        404: OpenApiResponse(
            description="Maintenance configuration not found."
        ),
    },
    "tags": ["Finance"],
}


UPDATE_MAINTENANCE_CONFIGURATION_DOCS = {
    "summary": "Update Maintenance Configuration",
    "description": (
        "Create or update the global maintenance configuration. "
        "Changes will apply only to future bills and will not modify "
        "existing unpaid bills."
    ),
    "request": MaintenanceConfigurationSerializer,
    "responses": {
        200: MaintenanceConfigurationSerializer,
    },
    "tags": ["Finance"],
}


BILL_CREATE_DOCS = {
    "summary": "Generate Bill",
    "description": (
        "Generate a maintenance bill for a specific flat using the "
        "current global maintenance configuration. "
        "The flat must exist and must not be deleted. "
        "Configuration changes apply only to future bills."
    ),
    "request": BillSerializer,
    "responses": {
        201: BillSerializer,
    },
    "tags": ["Finance"],
}


BILL_LIST_DOCS = {
    "summary": "Get Bills",
    "description": (
        "Retrieve all generated maintenance bills."
    ),
    "responses": {
        200: BillSerializer(many=True),
    },
    "tags": ["Finance"],
}


PAYMENT_CREATE_DOCS = {
    "summary": "Create Payment",
    "description": (
        "Record a payment against a bill. "
        "Partial payments are supported. "
        "The bill status is updated based on the total successful "
        "payments received."
    ),
    "request": PaymentSerializer,
    "responses": {
        201: PaymentSerializer,
    },
    "tags": ["Finance"],
}


PAYMENT_LIST_DOCS = {
    "summary": "Get Payment History",
    "description": (
        "Retrieve all successful and failed payment records "
        "that have not been deleted."
    ),
    "responses": {
        200: PaymentSerializer(many=True),
    },
    "tags": ["Finance"],
}


LATE_FEE_CREATE_DOCS = {
    "summary": "Apply Late Fee",
    "description": (
        "Calculate and apply the applicable late fee to a bill "
        "based on the configured grace period, daily late fee, "
        "and maximum late fee. "
        "Existing late fee waivers are preserved."
    ),
    "request": inline_serializer(
        name="LateFeeRequest",
        fields={
            "bill": serializers.UUIDField(
                help_text="Bill ID"
            ),
        },
    ),
    "responses": {
        200: BillSerializer,
        400: OpenApiResponse(
            description="Invalid request or late fee cannot be applied."
        ),
        404: OpenApiResponse(
            description="Bill not found."
        ),
    },
    "tags": ["Finance"],
}


WAIVE_LATE_FEE_DOCS = {
    "summary": "Waive Late Fee",
    "description": (
        "Waive a specified amount of late fee for a bill and "
        "record the waiver reason."
    ),
    "request": inline_serializer(
        name="WaiveLateFeeRequest",
        fields={
            "history_id": serializers.UUIDField(
                help_text="Late fee history ID"
            ),
            "waived_amount": serializers.DecimalField(
                max_digits=10,
                decimal_places=2,
                min_value=Decimal("0.01"),
            ),
            "waiver_reason": serializers.CharField(
                help_text="Reason for waiving the late fee"
            ),
        },
    ),
    "responses": {
        200: LateFeeHistorySerializer,
        400: OpenApiResponse(
            description="Invalid waiver request."
        ),
        404: OpenApiResponse(
            description="Late fee history not found."
        ),
    },
    "tags": ["Finance"],
}


LATE_FEE_HISTORY_DOCS = {
    "summary": "Get Late Fee History",
    "description": (
        "Retrieve the history of late fees applied to bills, "
        "including waived amounts and waiver details."
    ),
    "responses": {
        200: LateFeeHistorySerializer(many=True),
    },
    "tags": ["Finance"],
}