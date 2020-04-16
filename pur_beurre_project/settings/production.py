import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from . import *

DEBUG = False

sentry_sdk.init(
    dsn="https://2e760245c52d4ff7bd9ece56a3129bc7@sentry.io/5184701",
    integrations=[DjangoIntegration()],
)
