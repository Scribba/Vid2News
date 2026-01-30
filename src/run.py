from src.extracting import SimpleNewsExtractor
from src.processing.clustering import NewsClusteringEngine


channels = [
    "https://www.youtube.com/@GoodTimesBadTimes",
    "https://www.youtube.com/channel/UCsy9I56PY3IngCf_VGjunMQ",
    "https://www.youtube.com/channel/UCVVRDJbTe6q6FJRR4m3h3_A",
    "https://www.youtube.com/channel/UCwnKziETDbHJtx78nIkfYug"
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
    clustering_engine.get_clusters(news, json_save_path="news_clusters.json")


