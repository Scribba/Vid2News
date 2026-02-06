import os
import requests
import pandas as pd
from pathlib import Path
from src.utils.logger import logger
from src.utils.path_utils import get_repo_root

BASE_URL = "https://scribba-sm.getgrist.com/api"


class GristClient:
    def __init__(self, document_id: str, table_id: str):
        self.document_id = document_id
        self.table_id = table_id
        self.headers = {
            "Authorization": f"Bearer {os.environ.get('GRIST_API_KEY')}",
            "Content-Type": "application/json"
        }

    def upload(self, data: list[dict]):
        payload = {"records": [{"fields": row} for row in data]}
        resp = requests.post(
            f"{BASE_URL}/docs/{self.document_id}/tables/{self.table_id}/records",
            headers=self.headers,
            json=payload,
        )

        resp.raise_for_status()
        if resp.status_code != 200:
            logger.error(resp.json())
        else:
            logger.info("Successfully uploaded records")

    def fetch_table(self, max_rows: int = 100, include_ids: bool = False) -> pd.DataFrame:
        resp = requests.get(
            f"{BASE_URL}/docs/{self.document_id}/tables/{self.table_id}/records",
            headers=self.headers,
            params={"limit": max_rows}
        )
        resp.raise_for_status()
        data = resp.json()
        records = data.get("records", [])
        if include_ids:
            rows = []
            for rec in records:
                fields = dict(rec.get("fields", {}))
                fields["id"] = rec.get("id")
                rows.append(fields)
        else:
            rows = [rec.get("fields", {}) for rec in records]

        df = pd.DataFrame(rows)
        logger.info(f"Fetched {len(df)} records from Grist table")
        return df

    def update_rows(self, updates: list[dict]):
        payload = {"records": updates}

        resp = requests.patch(
            f"{BASE_URL}/docs/{self.document_id}/tables/{self.table_id}/records",
            headers=self.headers,
            json=payload,
        )

        resp.raise_for_status()
        logger.info(f"Updated {len(updates)} records in Grist table")


if __name__ == "__main__":
    from dotenv import load_dotenv

    repo_root = get_repo_root(Path(__file__))
    load_dotenv(repo_root / ".env")

    uploader = GristClient(document_id="n5DoTVv7Zr4q", table_id="NaGlobalnie")

    df = uploader.fetch_table()

    updates = [
        {
            "id": 1,
            "fields": {
                "status": "not approved"
            }
        }
    ]

    uploader.update_rows(updates )

