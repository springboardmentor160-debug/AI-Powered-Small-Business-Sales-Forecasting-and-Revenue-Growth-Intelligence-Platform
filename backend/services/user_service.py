import logging

logger = logging.getLogger(__name__)


# In-memory user registry.
# This will be replaced by PostgreSQL persistence in Phase 2.
fake_users_db: dict[str, dict] = {}