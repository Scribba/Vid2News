import os
import json
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

from src.utils.logger import logger
from src.utils.path_utils import get_repo_root
from src.utils.grist_client import GristClient
from src.publishing.fb_publisher import FacebookPublisher


REPO_ROOT = get_repo_root(Path(__file__))
CONFIGS_PATH = REPO_ROOT / "configs"


class PublishingException(Exception):
    pass


def publish_for_config(config: dict):
    grist_client = GristClient(
        document_id=config["grist_document_id"],
        table_id=config["grist_table_name"],
    )

    posts = grist_client.fetch_table(include_ids=True)
    approved_posts = posts[posts["status"] == "approved"]
    if approved_posts.empty:
        logger.info("No approved posts for table %s", config["grist_table_name"])
        return

    approved_posts = approved_posts.copy()
    approved_posts["score"] = pd.to_numeric(
        approved_posts.get("score"),
        errors="coerce",
    )
    top_post = approved_posts.sort_values(
        by="score",
        ascending=False,
        na_position="last",
    ).iloc[0]

    content = top_post.get("content")
    if not content:
        logger.warning(
            "Top approved post missing content for table %s",
            config["grist_table_name"],
        )
        raise PublishingException("Top approved post missing content for table %s")

    page_token = os.getenv(config["page_token_env_var_name"])
    page_id = os.getenv(config["page_id_env_var_name"])
    if not page_token or not page_id:
        logger.error(
            "Missing Facebook credentials for table %s",
            config["grist_table_name"],
        )
        raise PublishingException("Missing Facebook credentials for table %s")

    row_id = top_post.get("id")
    if not row_id:
        logger.warning(
            "Top approved post missing id for table %s",
            config["grist_table_name"],
        )
        raise PublishingException("Top approved post missing id for table %s")

    fb_client = FacebookPublisher(access_token=page_token, page_id=page_id)
    was_published = fb_client.publish(content)
    if not was_published:
        logger.warning(
            "Publishing failed for table %s, row %s",
            config["grist_table_name"],
            row_id,
        )
        raise PublishingException("Publishing failed for table %s, row %s")

    grist_client.update_rows([
        {
            "id": int(row_id),
            "fields": {
                "status": "published",
            },
        }
    ])


if __name__ == "__main__":
    load_dotenv(REPO_ROOT / ".env")

    configs = []
    for file in os.listdir(CONFIGS_PATH):
        with open(CONFIGS_PATH / file, "r") as f:
            config = json.load(f)
            configs.append(config)

    for config in configs:
        publish_for_config(config)
