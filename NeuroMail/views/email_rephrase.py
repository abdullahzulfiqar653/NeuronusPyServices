from rest_framework import generics
from NeuroMail.serializers.email_rephrase import RephraseEmailCreateSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RephraseEmailCreateView(generics.CreateAPIView):
    """API to rephrase email body using a selected AI tone template."""

    serializer_class = RephraseEmailCreateSerializer

    @swagger_auto_schema(
        operation_summary="Rephrase email body using AI template",
        operation_description=(
            "Rephrases the provided email body text using the selected AI tone template.\n\n"
            "**Inputs:**\n"
            "- `email_text`: Original email content you want rephrased\n"
            "- `template`: ID of the AI tone template to use (e.g., Michelle Obama)\n\n"
            "**Returns:** Rephrased email content."
        ),
        request_body=RephraseEmailCreateSerializer,
        responses={
            201: openapi.Response(
                description="Email rephrased successfully.",
            ),
            400: "Validation error or rephrasing failure.",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
