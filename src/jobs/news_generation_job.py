import os
import json
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.extracting.simple_news_extractor import SimpleNewsExtractor
from src.processing.clustering import NewsClusteringEngine
from src.generating.news_generator import NewsGenerator
from src.utils.logger import logger
from src.utils.grist_client import GristClient


CONFIGS_PATH = Path("/Users/wnowogor/PycharmProjects/Vid2News/configs")
TIME_DELTA = timedelta(hours=24)


def generate(config: dict):
    extractors = [SimpleNewsExtractor(url) for url in config["source_channels"]]
    since_date = datetime.now() - TIME_DELTA

    news = []

    def run_extractor(extractor):
        try:
            results = extractor.run(since_date=since_date)
            logger.info(
                "Extracted %s transcripts from channel %s",
                len(results),
                extractor.channel_id,
            )
            return results
        except Exception as e:
            logger.error(
                "Failed to extract transcripts from channel %s",
                extractor.channel_id,
                exc_info=e,
            )
            return []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(run_extractor, ex) for ex in extractors]

        for future in as_completed(futures):
            news.extend(future.result())

    clustering_engine = NewsClusteringEngine()
    clusters_df = clustering_engine.get_clusters(news, json_save_path="news_clusters.json")

    news_generator = NewsGenerator()
    news_list = news_generator.generate_from_df(clusters_df)

    upload_data = []
    for news in news_list:
        data = {
            "title": news.title,
            "content": news.content,
            "source_video_urls": str(news.source_video_urls),
            "source_channels": str(news.source_channels),
            "status": "not approved"
        }
        upload_data.append(data)

    uploader = GristClient(
        document_id=config["grist_document_id"],
        table_id=config["grist_table_name"],
    )
    uploader.upload(upload_data)

    logger.info("Job finished!")


if __name__ == "__main__":
    load_dotenv("/Users/wnowogor/PycharmProjects/Vid2News/.env")

    configs = []
    for file in os.listdir(CONFIGS_PATH):
        with open(CONFIGS_PATH / file, "r") as f:
            config = json.load(f)
            configs.append(config)

    for config in configs:
        generate(config)
