import json
from datetime import datetime
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.extracting.transcript_parser import TranscriptParser
from src.extracting.transcripts_fetcher import ChannelTranscriptsFetcher
from src.extracting.utils import News
from src.utils.logger import logger


class SimpleNewsExtractor:
    def __init__(self, channel_url: str):
        self.channel_id = channel_url
        self.transcripts_fetcher = ChannelTranscriptsFetcher(channel_url)
        self.transcript_parser = TranscriptParser()

    def run(
        self,
        n_videos: Optional[int] = None,
        since_date: Optional[datetime] = None,
        json_save_path: Optional[str] = None,
        max_workers: int = 4,
    ) -> List[News]:

        transcripts = self.transcripts_fetcher.fetch_transcripts(
            n_videos=n_videos,
            since_date=since_date,
        )

        logger.info(f"Fetched {len(transcripts)} transcripts")

        news: List[News] = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.transcript_parser.run, transcript): transcript
                for transcript in transcripts
            }

            for future in as_completed(futures):
                transcript = futures[future]
                try:
                    result = future.result()
                    news.extend(result)
                except Exception as e:
                    logger.exception(
                        f"Failed to process transcript {getattr(transcript, 'video_id', None)}: {e}"
                    )

        logger.info(f"Extracted {len(news)} news items")

        if json_save_path:
            self._save_to_json(news, json_save_path)

        return news

    @staticmethod
    def _save_to_json(news: List[News], path: str) -> None:
        data = {
            "generated_at": datetime.utcnow().isoformat(),
            "news_items": [item.to_dict() for item in news],
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved news to {path}")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv("/Users/wnowogor/PycharmProjects/Vid2News/.env")

    extractor = SimpleNewsExtractor("https://www.youtube.com/@GoodTimesBadTimes")
    extractor.run(n_videos=1, json_save_path="news.json")