from . import *

DEBUG = False

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration, LoggingIntegration

sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.INFO   # Send errors as events
)

sentry_sdk.init(
    dsn="https://57df46d460e3492997462bddc1118433@o371148.ingest.sentry.io/5203994",
    integrations=[sentry_logging],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)
