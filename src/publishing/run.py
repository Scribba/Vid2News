import os
from dotenv import load_dotenv

from src.publishing.fb_publisher import FacebookPublisher
from src.utils.grist_client import GristClient


if __name__ == "__main__":
    load_dotenv("/Users/wnowogor/PycharmProjects/Vid2News/.env")

    grist_client = GristClient(
        document_id="n5DoTVv7Zr4q", table_id="Geopolitics"
    )

    fb_client = FacebookPublisher(
        access_token=os.getenv("FB_NAGLOBALNIE_PUBLISHER_TOKEN"),
        page_id=os.getenv("FB_NAGLOBALNIE_PAGE_ID"),
    )

    posts = grist_client.fetch_table()
    approved_posts = posts[posts["status"] == "approved"]

    for post in approved_posts.iterrows():
        fb_client.publish(post[1]["content"])
