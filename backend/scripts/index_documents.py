import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.api.deps import get_indexing_service  # noqa: E402
from app.core.logging import configure_logging  # noqa: E402


async def main() -> None:
    configure_logging()
    reports = await get_indexing_service().index_all()
    if not reports:
        print("Aucun PDF trouve dans documents/.")
        return
    for report in reports:
        print(report)


if __name__ == "__main__":
    asyncio.run(main())

