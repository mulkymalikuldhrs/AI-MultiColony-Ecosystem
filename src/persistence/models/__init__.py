"""ORM model registration entry point.

Importing this module ensures all ORM models are registered with
``Base.metadata`` so Alembic autogenerate detects every table.

The actual ORM classes have moved to entity-specific subpackages:
- ``deerflow.persistence.thread_meta``
- ``deerflow.persistence.run``
- ``deerflow.persistence.feedback``
- ``deerflow.persistence.user``

``RunEventRow`` remains in ``deerflow.persistence.models.run_event`` because
its storage implementation lives in ``deerflow.runtime.events.store.db`` and
there is no matching entity directory.
"""

from src.persistence.feedback.model import FeedbackRow
from src.persistence.models.run_event import RunEventRow
from src.persistence.run.model import RunRow
from src.persistence.thread_meta.model import ThreadMetaRow
from src.persistence.user.model import UserRow

__all__ = ["FeedbackRow", "RunEventRow", "RunRow", "ThreadMetaRow", "UserRow"]
