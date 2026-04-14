#!/bin/sh
set -eu

python - <<'PY'
import asyncio
import os
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


database_url = os.environ["DATABASE_URL"]
max_attempts = int(os.environ.get("DB_MAX_ATTEMPTS", "60"))
retry_interval = float(os.environ.get("DB_RETRY_INTERVAL", "2"))


async def wait_for_database() -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    try:
        for attempt in range(1, max_attempts + 1):
            try:
                async with engine.connect() as connection:
                    await connection.execute(text("SELECT 1"))
                print("Database is ready.", flush=True)
                return
            except Exception as exc:  # pragma: no cover - startup retry path
                if attempt == max_attempts:
                    print(
                        f"Database did not become ready after {max_attempts} attempts: {exc}",
                        file=sys.stderr,
                        flush=True,
                    )
                    raise

                print(
                    f"Waiting for database ({attempt}/{max_attempts}): {exc}",
                    flush=True,
                )
                await asyncio.sleep(retry_interval)
    finally:
        await engine.dispose()


asyncio.run(wait_for_database())
PY

alembic upgrade head

exec "$@"
