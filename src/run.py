from datetime import datetime, timedelta

from src.extracting import SimpleNewsExtractor
from src.processing.clustering import NewsClusteringEngine
from src.generating.news_generator import NewsGenerator
from src.utils.grist_client import GristClient
from src.utils.logger import logger


TIME_DELTA = timedelta(hours=24)


channels = [
    "https://www.youtube.com/@warographics643",
    "https://www.youtube.com/@VisualPolitikEN/videos",
    "https://www.youtube.com/@CaspianReport",
    "https://www.youtube.com/@johnnyharris",
    "https://www.youtube.com/@TheRedLinePod/videos",
    "https://www.youtube.com/@TheResearcherYT",
    "https://www.youtube.com/@ZeihanonGeopolitics",
    "https://www.youtube.com/@JamesKerLindsay",
    "https://www.youtube.com/@PBoyle",
    "https://www.youtube.com/@MoneyMacro",
    "https://www.youtube.com/@asiasociety",
    "https://www.youtube.com/@stgseries",
    "https://www.youtube.com/@hudsoninstitute",
    "https://www.youtube.com/@csis",
    "https://www.youtube.com/@CISAus",
    "https://www.youtube.com/@RusiOrg/featured",
    "https://www.youtube.com/@centreforeasternstudies/featured",
    "https://www.youtube.com/@GoodTimesBadTimes"
]


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv("/Users/wnowogor/PycharmProjects/Vid2News/.env")

    extractors = [SimpleNewsExtractor(url) for url in channels]

    news = []
    for i, extractor in enumerate(extractors):
        try:
            results = extractor.run(since_date=datetime.now() - TIME_DELTA)
            logger.info("Extracted %s transcripts from channel %s", len(results), extractor.channel_id)
            news.extend(results)
        except Exception as e:
            logger.error("Failed to extract transcripts from channel %s", extractor.channel_id)

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

    uploader = GristClient(document_id="n5DoTVv7Zr4q", table_id="Geopolitics")
    uploader.upload(upload_data)
# #


