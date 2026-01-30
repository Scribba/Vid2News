from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime
from typing import Optional, List
import json
import scrapetube

from src.utils.logger import logger
from src.extracting.utils import Transcript


DEFAULT_N_VIDEOS = 5
LANGUAGES = ["en"]


class ChannelTranscriptsFetcher:
    def __init__(self, channel_url: str):
        self.channel_url = channel_url
        self._transcript_api = YouTubeTranscriptApi()

    def fetch_transcripts(
        self,
        n_videos: Optional[int] = None,
        since_date: Optional[datetime] = None,
        json_save_path: Optional[str] = None
    ) -> List[Transcript]:
        if n_videos is None and since_date is None:
            n_videos = DEFAULT_N_VIDEOS

        # Determine how many videos to scan
        scan_limit = n_videos if n_videos else 100  # Scan more if filtering by date

        videos = self._get_channel_videos(limit=scan_limit)
        logger.debug(f"Retrieved {len(videos)} video metadata entries")

        transcripts = []
        failed = 0
        for video_data in videos:
            video_metadata = self._parse_video_metadata(video_data)
            video_id = video_metadata["video_id"]

            if not video_id:
                logger.debug(f"Could not find video id, skipping to next metadata entry")
                continue

            logger.debug("Fetching transcript for video %s", video_metadata["title"])
            transcript_text = self._fetch_transcript_for_video(video_id)

            if transcript_text is None:
                failed += 1
                continue

            transcript = Transcript(
                video_id=video_id,
                title=video_metadata["title"],
                text=transcript_text or "",
            )
            transcripts.append(transcript)

            if n_videos and len(transcripts) >= n_videos:
                break

        logger.info("Successfully fetched %s transcripts, %s failed attempts", len(transcripts), failed)

        if json_save_path is not None:
            self._save_transcripts_to_json(transcripts, json_save_path)

        return transcripts

    def _save_transcripts_to_json(self, transcripts: List[Transcript], path: str) -> None:
        """
        Save transcripts to a JSON file.

        :param transcripts: List of Transcript objects to save
        :param path: File path to save the JSON
        """
        data = {
            "channel_url": self.channel_url,
            "fetched_at": datetime.now().isoformat(),
            "count": len(transcripts),
            "transcripts": [t.to_dict() for t in transcripts],
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(transcripts)} transcripts to {path}")


    def _get_channel_videos(self, limit: Optional[int] = None) -> List[dict]:
        """
        Fetch video metadata from the channel.

        :param limit: Maximum number of videos to fetch
        :return: List of video metadata dictionaries
        """
        videos = []
        video_generator = scrapetube.get_channel(
            channel_url=self.channel_url,
            limit=limit,
            sort_by="newest"
        )

        for video in video_generator:
            videos.append(video)
            if limit and len(videos) >= limit:
                break

        return videos

    def _parse_video_metadata(self, video_data: dict) -> dict:
        """
        Parse video metadata from scrapetube response.
        """
        video_id = video_data.get("videoId", "")
        title = video_data.get("title", {}).get("runs", [{}])[0].get("text", "")

        return {
            "video_id": video_id,
            "title": title,
        }

    def _fetch_transcript_for_video(self, video_id: str) -> Optional[str]:
        """
        Fetch transcript text for a single video.

        :param video_id: YouTube video ID
        :return: Transcript text or None if unavailable
        """
        try:
            transcript_data = self._transcript_api.fetch(video_id, languages=LANGUAGES)
            text = " ".join(entry.text for entry in transcript_data)
            logger.debug(f"Successfully fetched transcript for video {video_id}")
            return text.strip()
        except Exception as e:
            logger.warning(f"Could not fetch transcript for {video_id}: {e}")
            return None


if __name__ == "__main__":
    fetcher = ChannelTranscriptsFetcher("https://www.youtube.com/@GoodTimesBadTimes")
    fetcher.fetch_transcripts(n_videos=2, json_save_path="transcripts.json")