from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated

from apps.finance.serializers.BillSerializer import BillSerializer
from apps.finance.services.BillService import BillService
from apps.finance.serializers.PaymentSerializer import PaymentSerializer
from apps.finance.services.PaymentService import PaymentService
from apps.finance.models.Bill import Bill
from apps.finance.serializers.WaiveLateFeeSerializer import (
    WaiveLateFeeSerializer
)
from apps.finance.services.LateFeeService import LateFeeService
from apps.finance.serializers.LateFeeHistorySerializer import (
    LateFeeHistorySerializer
)

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from apps.finance.swagger.finance_docs import (
    MAINTENANCE_CONFIGURATION_DOCS,
    UPDATE_MAINTENANCE_CONFIGURATION_DOCS,
    BILL_CREATE_DOCS,
    BILL_LIST_DOCS,
    PAYMENT_CREATE_DOCS,
    PAYMENT_LIST_DOCS,
    LATE_FEE_CREATE_DOCS,
    WAIVE_LATE_FEE_DOCS,
    LATE_FEE_HISTORY_DOCS,
)

from apps.finance.serializers.MaintenanceConfigurationSerializer import (
    MaintenanceConfigurationSerializer
)
from apps.finance.services.MaintenanceConfigurationService import (
    MaintenanceConfigurationService
)


class MaintenanceConfigurationView(APIView):

    @extend_schema(**MAINTENANCE_CONFIGURATION_DOCS)
    def get(self, request):
        configuration = MaintenanceConfigurationService.get_configuration()

        if not configuration:
            return Response(
                {
                    "message": "Maintenance configuration not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MaintenanceConfigurationSerializer(configuration)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(**UPDATE_MAINTENANCE_CONFIGURATION_DOCS)
    def put(self, request):
        serializer = MaintenanceConfigurationSerializer(
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)

        configuration = MaintenanceConfigurationService.update_configuration(
            serializer.validated_data
        )

        response_serializer = MaintenanceConfigurationSerializer(
            configuration
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )


class BillView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(**BILL_CREATE_DOCS)
    def post(self, request):
        serializer = BillSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        bill = BillService.generate_bill(
            billing_month=serializer.validated_data["billing_month"],
            area_charge=serializer.validated_data["area_charge"],
            flat_id=serializer.validated_data["flat"].id,
        )

        response_serializer = BillSerializer(bill)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(**BILL_LIST_DOCS)
    def get(self, request):
        bills = BillService.get_all_bills()

        serializer = BillSerializer(bills, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class PaymentView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(**PAYMENT_CREATE_DOCS)
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        try:
            payment = PaymentService.create_payment(
                bill=serializer.validated_data["bill"],
                amount=serializer.validated_data["amount"],
                payment_date=serializer.validated_data["payment_date"],
                payment_mode=serializer.validated_data["payment_mode"],
                transaction_reference=serializer.validated_data.get(
                    "transaction_reference"
                ),
            )

        except ValueError as exc:
            return Response(
                {
                    "success": False,
                    "message": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = PaymentSerializer(payment)

        return Response(
            {
                "success": True,
                "message": "Payment created successfully.",
                "data": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
    @extend_schema(**PAYMENT_LIST_DOCS)
    def get(self, request):
        payments = PaymentService.get_all_payments()

        serializer = PaymentSerializer(
            payments,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class LateFeeView(APIView):

    permission_classes = [IsAuthenticated]
    @extend_schema(**LATE_FEE_CREATE_DOCS)
    def post(self, request):
        bill_id = request.data.get("bill")

        if not bill_id:
            return Response(
                {
                    "success": False,
                    "message": "Bill ID is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            bill = Bill.objects.get(
                id=bill_id,
                is_deleted=False,
            )
        except Bill.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Bill not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            bill = LateFeeService.apply_late_fee(bill)

        except ValueError as exc:
            return Response(
                {
                    "success": False,
                    "message": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = BillSerializer(bill)

        return Response(
            {
                "success": True,
                "message": "Late fee applied successfully.",
                "data": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )    


class LateFeeHistoryView(APIView):

    permission_classes = [IsAuthenticated]
    @extend_schema(**LATE_FEE_HISTORY_DOCS)
    def get(self, request):
        history = LateFeeService.get_late_fee_history()

        serializer = LateFeeHistorySerializer(
            history,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class WaiveLateFeeView(APIView):

    permission_classes = [IsAuthenticated]
    @extend_schema(**WAIVE_LATE_FEE_DOCS)
    def post(self, request):

        serializer = WaiveLateFeeSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            history = LateFeeService.waive_late_fee(
                history_id=serializer.validated_data["history_id"],
                waived_amount=serializer.validated_data["waived_amount"],
                waiver_reason=serializer.validated_data["waiver_reason"],
            )

        except ValueError as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = LateFeeHistorySerializer(history)

        return Response(
            {
                "success": True,
                "message": "Late fee waived successfully.",
                "data": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )