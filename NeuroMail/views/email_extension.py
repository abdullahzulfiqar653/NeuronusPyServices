from rest_framework import generics
from NeuroMail.models.email_extension import EmailExtension
from NeuroMail.serializers.email_extension import EmailExtensionSerializer
from drf_yasg.utils import swagger_auto_schema


class EmailExtensionListView(generics.ListAPIView):
    """
    This API provides a list of all active email domain extensions
    that can be used while creating email addresses (e.g., @domain.com).
    """

    queryset = EmailExtension.objects.all()
    serializer_class = EmailExtensionSerializer

    def get_queryset(self):
        """Filter the queryset based on the is_active field."""
        return self.queryset.filter(is_active=True)

    @swagger_auto_schema(
        operation_summary="List active email domain extensions",
        operation_description=(
            "Returns all available and active email extensions "
            "(e.g., `@neuromail.digital`, `@neuromail.space`, `@neuromail.online`, `@neuromail.cloud` ) that users can select when creating email addresses."
        ),
        responses={200: EmailExtensionSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
