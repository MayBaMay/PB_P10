from . import *

DEBUG = False
ENV = os.getenv("ENV")

import sentry_sdk
import logging
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.django import DjangoIntegration

# All of this is already happening by default!
sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)

sentry_sdk.init(
    dsn="https://e2bb23a862b14cc6a4bb50bf23f1c94f@o371148.ingest.sentry.io/5203737",
    integrations=[DjangoIntegration(), sentry_logging],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)
