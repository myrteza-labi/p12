# monitoring.py
import os
import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from dotenv import load_dotenv

load_dotenv()

DSN = os.getenv("SENTRY_DSN")

# Capture des logs INFO+ et des exceptions
logging_integration = LoggingIntegration(
    level=None,        # capture nothing by default
    event_level="ERROR"  # capture errors as events
)

sentry_sdk.init(
    dsn=DSN,
    integrations=[SqlalchemyIntegration(), logging_integration],
    traces_sample_rate=0.1,   # ajustable en prod
    environment=os.getenv("ENVIRONMENT", "development"),
    release="epicevents@1.0.0"  # à mettre à jour avec tes versions
)
