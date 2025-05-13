from rest_framework import generics

from NeuroMail.models.email_extension import EmailExtension
from NeuroMail.serializers.email_extension import EmailExtensionSerializer


class EmailExtensionListView(generics.ListAPIView):
    """This api is to get all available extensions to create mails like domain.com"""

    queryset = EmailExtension.objects.all()
    serializer_class = EmailExtensionSerializer

    def get_queryset(self):
        """Filter the queryset based on the is_active field."""
        return self.queryset.filter(is_active=True)
