from src.extracting import SimpleNewsExtractor
from src.processing.clustering import NewsClusteringEngine
from src.generating.news_generator import NewsGenerator
from src.utils.grist_uploader import GristUploader


channels = [
    "https://www.youtube.com/@GoodTimesBadTimes",
    # "https://www.youtube.com/channel/UCsy9I56PY3IngCf_VGjunMQ",
    # "https://www.youtube.com/channel/UCwnKziETDbHJtx78nIkfYug"
]


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv("/Users/wnowogor/PycharmProjects/Vid2News/.env")

    extractors = [SimpleNewsExtractor(url) for url in channels]

    news = []
    for i, extractor in enumerate(extractors):
        results = extractor.run(json_save_path=f"news_{i}.json", n_videos=5)
        news.extend(results)

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

    uploader = GristUploader(document_id="n5DoTVv7Zr4q", table_id="Geopolitics")
    uploader.upload(upload_data)



