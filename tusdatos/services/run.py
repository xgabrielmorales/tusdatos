import asyncio

from tusdatos.core.database import trials_as_actor_db, trials_as_defendant_db
from tusdatos.services.scraper import JudicialProcessScraper


async def main():
    user_document_num = ""
    search_role = "DEMANDADO"

    COLLECTION = {
        "ACTOR": trials_as_actor_db,
        "DEMANDADO": trials_as_defendant_db,
    }

    scraper = JudicialProcessScraper(
        user_document_num=user_document_num,
        search_role=search_role,
    )
    causes = await scraper.extract_data()

    document = {
        "_id": user_document_num,
        **causes.model_dump(),
    }

    kwargs = {
        "filter": {"_id": user_document_num},
        "replacement": document,
        "upsert": True,
    }

    await COLLECTION[search_role].replace_one(**kwargs)


if __name__ == "__main__":
    asyncio.run(main())
