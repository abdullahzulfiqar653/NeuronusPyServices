from NeuroMail.serializers.email import EmailSerializer
from NeuroMail.serializers.mailbox import MailboxSerializer
from NeuroMail.serializers.temp_mail import TempEmailFakeSerializer
from NeuroMail.serializers.email_starred import EmailUpdateSerializer
from NeuroMail.serializers.email_extension import EmailExtensionSerializer
from NeuroMail.serializers.email_attachment import EmailAttachmentSerializer
from NeuroMail.serializers.email_ai_template import EmailAiTemplateSerializer
from NeuroMail.serializers.email_rephrase import RephraseEmailCreateSerializer


__all__ = [
    "EmailSerializer",
    "MailboxSerializer",
    "EmailUpdateSerializer",
    "TempEmailFakeSerializer",
    "EmailExtensionSerializer",
    "EmailAiTemplateSerializer",
    "EmailAttachmentSerializer",
    "RephraseEmailCreateSerializer",
]
