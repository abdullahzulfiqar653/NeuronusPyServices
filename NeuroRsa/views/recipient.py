from rest_framework import generics, filters
from NeuroRsa.serializers.recipient import RecipientSerializer
from drf_yasg.utils import swagger_auto_schema
from NeuroRsa.models.recipient import Recipient
from drf_yasg import openapi


class RecipientListCreateView(generics.ListCreateAPIView):
    serializer_class = RecipientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        return self.request.user.recipients.all().order_by("-created_at")

    @swagger_auto_schema(
        operation_summary="List all RSA recipients",
        operation_description=(
            "Returns all recipients created by the authenticated user.\n\n"
            "**Supports search** on `name` field."
        ),
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search recipients by name",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: RecipientSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new RSA recipient",
        operation_description=(
            "Creates a new recipient for RSA communication by providing a `name`, "
            "`public_key`, and optional `emoji`.\n\n"
            "**Note:** `name` must be unique per user."
        ),
        request_body=RecipientSerializer,
        responses={
            201: RecipientSerializer(),
            400: "Validation error: Duplicate name or missing fields",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RecipientRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecipientSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Recipient.objects.none()
        return self.request.user.recipients.all()

    @swagger_auto_schema(
        operation_summary="Retrieve a recipient",
        operation_description="Fetch the details of a specific RSA recipient using its ID.",
        responses={200: RecipientSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a recipient",
        operation_description=(
            "Update the details of a recipient such as `name`, `public_key`, or `emoji`.\n\n"
            "**Note:** `name` must remain unique per user."
        ),
        request_body=RecipientSerializer,
        responses={200: RecipientSerializer()},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a recipient",
        operation_description="Permanently delete a recipient using its ID.",
        responses={204: "Recipient deleted successfully"},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
