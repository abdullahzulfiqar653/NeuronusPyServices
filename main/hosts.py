from django.conf import settings
from django_hosts import patterns, host


ACTIVE_HOSTS = settings.ACTIVE_HOSTS


host_patterns = patterns(
    "",
    host(rf"{ACTIVE_HOSTS['default']}", "main.urls", name="default"),
    host(rf"{ACTIVE_HOSTS['NeuroRsa']}", "NeuroRsa.urls", name="NeuroRsa"),
    host(rf"{ACTIVE_HOSTS['NeuroMail']}", "NeuroMail.urls", name="NeuroMail"),
    host(rf"{ACTIVE_HOSTS['NeuroDrive']}", "NeuroDrive.urls", name="NeuroDrive"),
    host(
        rf"{ACTIVE_HOSTS['GhostTransfer']}", "GhostTransfer.urls", name="GhostTransfer"
    ),
    host(
        rf"{ACTIVE_HOSTS['Download']}", "GhostTransfer.download_urls", name="Download"
    ),
    host(
        rf"{ACTIVE_HOSTS['PasswordManager']}",
        "PasswordManager.urls",
        name="PasswordManager",
    ),
)
