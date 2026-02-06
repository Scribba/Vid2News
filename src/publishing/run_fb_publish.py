import os
import time
from dotenv import load_dotenv

from src.publishing.fb_publisher import FacebookPublisher
from src.utils.grist_client import GristClient


if __name__ == "__main__":
    from pathlib import Path
    from src.utils.path_utils import get_repo_root

    repo_root = get_repo_root(Path(__file__))
    load_dotenv(repo_root / ".env")

    grist_client = GristClient(
        document_id="n5DoTVv7Zr4q", table_id="NaGlobalnie"
    )

    fb_client = FacebookPublisher(
        access_token=os.getenv("FB_NAGLOBALNIE_PUBLISHER_TOKEN"),
        page_id=os.getenv("FB_NAGLOBALNIE_PAGE_ID"),
    )

    posts = grist_client.fetch_table()
    approved_posts = posts[posts["status"] == "approved"]

    for post in approved_posts.iterrows():
        time.sleep(10)
        fb_client.publish(post[1]["content"])
