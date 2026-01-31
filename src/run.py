from datetime import datetime, timedelta

from src.extracting import SimpleNewsExtractor
from src.processing.clustering import NewsClusteringEngine
from src.generating.news_generator import NewsGenerator
from src.utils.grist_client import GristClient
from src.utils.logger import logger


TIME_DELTA = timedelta(hours=48)


channels = [
    "https://www.youtube.com/@ZeihanonGeopolitics",         # Zeihan on Geopolitics - demografia, polityka, energia :contentReference[oaicite:1]{index=1}
    "https://www.youtube.com/user/CaspianReport",          # Caspian Report - dogłębne analizy globalne :contentReference[oaicite:2]{index=2}
    "https://www.youtube.com/c/Stratfor",                   # Stratfor - geopolityka i prognozy strategiczne :contentReference[oaicite:3]{index=3}
    "https://www.youtube.com/channel/UCKt7TllYn9qFzfjIdXZGMug", # StratNewsGlobal - strategiczne analizy :contentReference[oaicite:4]{index=4}
    "https://www.youtube.com/channel/UCHhC2FEUxxP7bSgY2RG-qA", # Geopolitical Futures - przyszłe trendy :contentReference[oaicite:5]{index=5}
    "https://www.youtube.com/channel/UCQ30Ahy2VwJXGGCj8XnXvHg", # Geopolitics & Empire - wywiady i dyskusje :contentReference[oaicite:6]{index=6}
    "https://www.youtube.com/c/CentreforGeopolitics",       # Centre for Geopolitics (Cambridge) :contentReference[oaicite:7]{index=7}
    "https://www.youtube.com/@GoodTimesBadTimes" # GoodTimesBadTimes
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

#     news_generator = NewsGenerator()
#     news_list = news_generator.generate_from_df(clusters_df)
#
#     upload_data = []
#     for news in news_list:
#         data = {
#             "title": news.title,
#             "content": news.content,
#             "source_video_urls": str(news.source_video_urls),
#             "source_channels": str(news.source_channels),
#             "status": "not approved"
#         }
#         upload_data.append(data)
#
#     uploader = GristClient(document_id="n5DoTVv7Zr4q", table_id="Geopolitics")
#     uploader.upload(upload_data)
# #


