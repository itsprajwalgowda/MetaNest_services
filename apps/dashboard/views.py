from datetime import datetime

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.dashboard.serializers import DashboardSerializer
from apps.dashboard.services import DashboardService


@extend_schema(
    summary="Get Dashboard",
    description=(
        "Retrieve dashboard summary, monthly collection, "
        "occupancy by wing, and recent payments."
    ),
    parameters=[
        OpenApiParameter(
            name="month",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Dashboard month in YYYY-MM format.",
            examples=[
                OpenApiExample(
                    "September 2026",
                    value="2026-09",
                )
            ],
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=DashboardSerializer,
            description="Dashboard data retrieved successfully.",
        ),
        400: OpenApiResponse(
            description="Invalid month format.",
        ),
    },
    tags=["Dashboard"],
)
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get("month")

        if month:
            try:
                selected_date = datetime.strptime(
                    month,
                    "%Y-%m"
                )
            except ValueError:
                return Response(
                    {
                        "success": False,
                        "message": (
                            "Invalid month format. "
                            "Use YYYY-MM."
                        ),
                    },
                    status=400,
                )
        else:
            selected_date = datetime.today()

        dashboard_data = DashboardService.get_dashboard(
            year=selected_date.year,
            month=selected_date.month,
        )

        serializer = DashboardSerializer(dashboard_data)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=200,
        )