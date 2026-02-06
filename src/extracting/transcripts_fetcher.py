import os
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from datetime import datetime, timedelta
from typing import Optional, List
import json
import scrapetube

from src.utils.logger import logger
from src.extracting.utils import Transcript


DEFAULT_N_VIDEOS = 5
LANGUAGES = ["en"]
RELATIVE_TIME_RE = re.compile(
    r"(?P<value>\d+)\s+(?P<unit>second|minute|hour|day|week|month|year)s?\s+ago"
)


class ChannelTranscriptsFetcher:
    def __init__(self, channel_url: str):
        self.channel_url = channel_url
        self._transcript_api = YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=os.getenv("WEBSHARE_PROXY_USERNAME"),
                proxy_password=os.getenv("WEBSHARE_PROXY_PASSWORD"),
            )
        )

    def fetch_transcripts(
        self,
        n_videos: Optional[int] = None,
        since_date: Optional[datetime] = None,
        json_save_path: Optional[str] = None
    ) -> List[Transcript]:
        if n_videos is None and since_date is None:
            n_videos = DEFAULT_N_VIDEOS

        # Determine how many videos to scan
        scan_limit = n_videos if n_videos is not None else DEFAULT_N_VIDEOS
        if since_date is not None:
            scan_limit = max(scan_limit, 50)
            since_date = self._normalize_datetime(since_date)

        videos = self._get_channel_videos(limit=scan_limit)
        logger.debug(f"Retrieved {len(videos)} video metadata entries")

        transcripts = []
        failed = 0
        for video_data in videos:
            video_metadata = self._parse_video_metadata(video_data)
            video_id = video_metadata["video_id"]
            published_at = video_metadata["published_at"]

            if not video_id:
                logger.debug(f"Could not find video id, skipping to next metadata entry")
                continue
            if since_date is not None:
                if published_at is None:
                    logger.debug(
                        "Missing publish date for %s; skipping due to since_date filter",
                        video_metadata["title"],
                    )
                    continue
                if published_at < since_date:
                    logger.debug(
                        "Reached videos older than since_date (%s); stopping scan",
                        since_date.isoformat(),
                    )
                    break

            logger.debug("Fetching transcript for video %s", video_metadata["title"])
            transcript_text = self._fetch_transcript_for_video(video_id)

            if transcript_text is None:
                failed += 1
                continue

            transcript = Transcript(
                video_id=video_id,
                title=video_metadata["title"],
                text=transcript_text or "",
                publish_date=published_at,
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
        published_at = self._extract_published_at(video_data)

        return {
            "video_id": video_id,
            "title": title,
            "published_at": published_at,
        }

    def _normalize_datetime(self, value: datetime) -> datetime:
        if value.tzinfo is not None:
            return value.astimezone().replace(tzinfo=None)
        return value

    def _extract_published_at(self, video_data: dict) -> Optional[datetime]:
        if "publishedTimestamp" in video_data:
            try:
                return datetime.fromtimestamp(int(video_data["publishedTimestamp"]))
            except (TypeError, ValueError):
                pass

        published_date = video_data.get("publishedDate")
        if published_date:
            try:
                parsed = datetime.fromisoformat(published_date)
                return self._normalize_datetime(parsed)
            except ValueError:
                pass

        published_time_text = video_data.get("publishedTimeText", {})
        text = ""
        if isinstance(published_time_text, dict):
            text = (
                published_time_text.get("simpleText")
                or (published_time_text.get("runs") or [{}])[0].get("text", "")
            )
        elif isinstance(published_time_text, str):
            text = published_time_text

        if not text:
            return None

        match = RELATIVE_TIME_RE.search(text.lower())
        if not match:
            return None

        value = int(match.group("value"))
        unit = match.group("unit")
        if unit == "second":
            delta = timedelta(seconds=value)
        elif unit == "minute":
            delta = timedelta(minutes=value)
        elif unit == "hour":
            delta = timedelta(hours=value)
        elif unit == "day":
            delta = timedelta(days=value)
        elif unit == "week":
            delta = timedelta(weeks=value)
        elif unit == "month":
            delta = timedelta(days=value * 30)
        else:
            delta = timedelta(days=value * 365)

        return datetime.now() - delta

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
    from dotenv import load_dotenv
    from pathlib import Path
    from src.utils.path_utils import get_repo_root

    repo_root = get_repo_root(Path(__file__))
    load_dotenv(repo_root / ".env")

    fetcher = ChannelTranscriptsFetcher("https://www.youtube.com/@GoodTimesBadTimes")
    fetcher.fetch_transcripts(n_videos=10, json_save_path="transcripts.json")