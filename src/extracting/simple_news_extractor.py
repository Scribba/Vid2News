from datetime import datetime
from typing import List, Optional

from src.extracting.transcript_parser import TranscriptParser
from src.extracting.transcripts_fetcher import ChannelTranscriptsFetcher
from src.extracting.utils import Transcript, News
from src.utils import logger


class SimpleNewsExtractor:
    def __init__(self, channel_url: str):
        self.channel_id = channel_url
        self.transcripts_fetcher = ChannelTranscriptsFetcher(channel_url)
        self.transcript_parser = TranscriptParser()

    def run(
        self,
        n_videos: Optional[int] = None,
        since_date: Optional[datetime] = None,
        json_save_path: Optional[str] = None
    ) -> List[News]:
        pass