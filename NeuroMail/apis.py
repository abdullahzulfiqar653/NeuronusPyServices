from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from main.views.download_file import FileDownloadAPIView


from NeuroMail.views import (
    MailBoxListCreateView,
    EmailFileRetrieveView,
    EmailExtensionListView,
    EmailAiTemplateListView,
    RephraseEmailCreateView,
    MailBoxRetrieveDeleteView,
    MailBoxExistenceCheckView,
    MailboxEmailListCreateView,
    MailboxEmailMoveToTrashView,
    MailboxEmailRetrieveUpdateView,
    MailboxEmailDeleteFromTrashView,
    MailboxEmailRestoreFromTrashView,
)

from main.views import (
    UserSignInView,
    UserSignUpView,
    UserProfileRetrieveUpdateView,
    RefreshTokenAPIView,
)


urlpatterns = [
    # =====================================================
    # User
    # =====================================================
    path("user/token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("user/generate-token/", UserSignInView.as_view(), name="generate-token"),
    path(
        "user/generate-pass-phrase/",
        UserSignUpView.as_view(),
        name="generate-pass-phrase",
    ),
    path(
        "user/profile/",
        UserProfileRetrieveUpdateView.as_view(),
        name="user-profile-retrieve-update-delete",
    ),
    path("user/refresh-token/", RefreshTokenAPIView.as_view(), name="refresh-token"),
    # =====================================================
    # MailBox
    # =====================================================
    path("mailbox/", MailBoxListCreateView.as_view(), name="mailbox-list-create"),
    path(
        "mailbox/extensions/",
        EmailExtensionListView.as_view(),
        name="mailbox-extension-list",
    ),
    path(
        "mailbox/existance/verify/",
        MailBoxExistenceCheckView.as_view(),
        name="mailbox-existance-verify",
    ),
    path(
        "mailbox/<str:pk>/",
        MailBoxRetrieveDeleteView.as_view(),
        name="mailbox-retrive-delete",
    ),
    # =====================================================
    # Email
    # =====================================================
    path(
        "mailbox/<str:mailbox_id>/emails/",
        MailboxEmailListCreateView.as_view(),
        name="mailbox-email-list-create",
    ),
    path(
        "mailbox/<str:mailbox_id>/emails/move-to-trash/",
        MailboxEmailMoveToTrashView.as_view(),
        name="mailbox-email-move-to-trash",
    ),
    path(
        "mailbox/<str:mailbox_id>/emails/restore-from-trash/",
        MailboxEmailRestoreFromTrashView.as_view(),
        name="mailbox-email-restore-from-trash",
    ),
    path(
        "mailbox/<str:mailbox_id>/emails/delete-from-trash/",
        MailboxEmailDeleteFromTrashView.as_view(),
        name="mailbox-email-delete-from-trash",
    ),
    path(
        "mailbox/<str:mailbox_id>/emails/<str:pk>/",
        MailboxEmailRetrieveUpdateView.as_view(),
        name="mailbox-email-retrieve-update",
    ),
    path(
        "emails/<str:email_id>/attachments/<str:pk>/",
        EmailFileRetrieveView.as_view(),
        name="email-file-retrieve",
    ),
    path(
        "emails/ai/templates/",
        EmailAiTemplateListView.as_view(),
        name="email-ai-templates-list",
    ),
    path(
        "emails/ai/rephrase/",
        RephraseEmailCreateView.as_view(),
        name="rephrase-email-create",
    ),
    # =====================================================
    # Media
    # =====================================================
    path(
        "media/file-download/",
        FileDownloadAPIView.as_view(),
        name="file-download-view",
    ),
]
