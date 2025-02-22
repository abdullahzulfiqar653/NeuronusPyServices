from NeuroMail.views.mailbox import (
    MailBoxListCreateView,
    MailBoxRetrieveDeleteView,
    MailBoxExistenceCheckView,
)
from NeuroMail.views.email import (
    EmailFileRetrieveView,
    MailboxEmailListCreateView,
    MailboxEmailMoveToTrashView,
    MailboxEmailRetrieveUpdateView,
    MailboxEmailDeleteFromTrashView,
    MailboxEmailRestoreFromTrashView,
)
from NeuroMail.views.email_extension import EmailExtensionListView
from NeuroMail.views.email_ai_template import EmailAiTemplateListView
from NeuroMail.views.email_rephrase import RephraseEmailCreateView

__all__ = [
    "MailBoxListCreateView",
    "MailBoxRetrieveDeleteView",
    "MailBoxExistenceCheckView",
    "EmailExtensionListView",
    "EmailAiTemplateListView",
    "RephraseEmailCreateView",
    "MailboxEmailListCreateView",
    "MailboxEmailMoveToTrashView",
    "MailboxEmailRetrieveUpdateView",
    "MailboxEmailDeleteFromTrashView",
    "MailboxEmailRestoreFromTrashView",
    "EmailFileRetrieveView",
]
