from . import *

DEBUG = False

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://e2bb23a862b14cc6a4bb50bf23f1c94f@o371148.ingest.sentry.io/5203737",
    integrations=[DjangoIntegration()],
)
