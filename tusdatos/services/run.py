import asyncio

from tusdatos.core.database import trails_as_defendant_db, trials_as_actor_db
from tusdatos.services.scraper import JudicialProcessScraper


async def main():
    user_document_num = ""
    search_role = "DEMANDADO"

    scraper = JudicialProcessScraper(search_role=search_role, user_document_num=user_document_num)
    causes = await scraper.extract_data()

    document = {
        "_id": user_document_num,
        "causes": causes.model_dump(),
    }

    if search_role == "ACTOR":
        await trials_as_actor_db.replace_one(
            filter={"_id": user_document_num},
            replacement=document,
            upsert=True,
        )

    if search_role == "DEMANDADO":
        await trails_as_defendant_db.replace_one(
            filter={"_id": user_document_num},
            replacement=document,
            upsert=True,
        )


if __name__ == "__main__":
    asyncio.run(main())
