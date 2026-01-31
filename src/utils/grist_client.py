import os
import requests
import pandas as pd
from src.utils.logger import logger

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

    def fetch_table(self, max_rows: int = 100) -> pd.DataFrame:
        resp = requests.get(
            f"{BASE_URL}/docs/{self.document_id}/tables/{self.table_id}/records",
            headers=self.headers,
            params={"limit": max_rows}
        )
        resp.raise_for_status()
        data = resp.json()
        records = [rec["fields"] for rec in data.get("records", [])]

        df = pd.DataFrame(records)
        logger.info(f"Fetched {len(df)} records from Grist table")
        return df

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv("/Users/wnowogor/PycharmProjects/Vid2News/.env")

    uploader = GristClient(document_id="n5DoTVv7Zr4q", table_id="Geopolitics")

    df = uploader.fetch_table()
    print(df)
