from rest_framework import generics
from NeuroMail.models.email_ai_template import EmailAiTemplate
from NeuroMail.serializers.email_ai_template import EmailAiTemplateSerializer
from drf_yasg.utils import swagger_auto_schema


class EmailAiTemplateListView(generics.ListAPIView):
    """
    This API provides predefined AI tone templates 
    (e.g., Donald Trump, Michelle Obama) that can be used 
    to rephrase emails in the new email box UI.
    """

    queryset = EmailAiTemplate.objects.all()
    serializer_class = EmailAiTemplateSerializer

    @swagger_auto_schema(
        operation_summary="List available AI tone templates",
        operation_description=(
            "Returns a list of available AI tone templates "
            "such as Donald Trump or Michelle Obama.\n\n"
            "These can be used to rephrase email content in different writing styles."
        ),
        responses={200: EmailAiTemplateSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
