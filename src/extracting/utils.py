from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import json

from src.utils import logger


@dataclass
class Transcript:
    """
    Represents a YouTube video transcript with metadata.
    """
    video_id: str
    title: str
    text: str
    channel_name: str = ""
    publish_date: Optional[datetime] = None
    url: str = field(init=False)

    def __post_init__(self):
        self.url = f"https://www.youtube.com/watch?v={self.video_id}"

    def __str__(self) -> str:
        return f"Transcript(video_id={self.video_id}, title={self.title[:50]}...)"

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> dict:
        """Convert transcript to dictionary format."""
        return {
            "video_id": self.video_id,
            "title": self.title,
            "text": self.text,
            "channel_name": self.channel_name,
            "publish_date": self.publish_date.isoformat() if self.publish_date else None,
            "url": self.url,
        }


@dataclass
class News:
    """
    Represents a news item extracted from a video transcript.
    """
    title: str
    summary: str
    content: str
    keywords: List[str] = field(default_factory=list)
    category: str = ""
    sentiment: str = ""
    importance: str = ""
    entities: List[str] = field(default_factory=list)
    source_video_id: str = ""
    source_video_title: str = ""
    source_video_url: str = ""
    source_channel: str = ""
    extracted_at: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"News(title={self.title[:50]}..., keywords={self.keywords[:3]})"

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> dict:
        """Convert News object to dictionary format."""
        return {
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "keywords": self.keywords,
            "category": self.category,
            "sentiment": self.sentiment,
            "importance": self.importance,
            "entities": self.entities,
            "source_video_id": self.source_video_id,
            "source_video_title": self.source_video_title,
            "source_video_url": self.source_video_url,
            "source_channel": self.source_channel,
            "extracted_at": self.extracted_at.isoformat(),
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert News object to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: dict, source_video_id: str = "", source_video_title: str = "",
                  source_video_url: str = "", source_channel: str = "") -> "News":
        """
        Create a News object from a dictionary (typically from LLM output).

        :param data: Dictionary containing news data
        :param source_video_id: ID of the source video
        :param source_video_title: Title of the source video
        :param source_video_url: URL of the source video
        :param source_channel: Channel name/ID
        :return: News object
        """
        return cls(
            title=data.get("title", ""),
            summary=data.get("summary", ""),
            content=data.get("content", ""),
            keywords=data.get("keywords", []),
            category=data.get("category", ""),
            sentiment=data.get("sentiment", "neutral"),
            importance=data.get("importance", "medium"),
            entities=data.get("entities", []),
            source_video_id=source_video_id,
            source_video_title=source_video_title,
            source_video_url=source_video_url,
            source_channel=source_channel,
        )


def save_news_to_json(news_list: List[News], path: str) -> None:
    """
    Save a list of News objects to a JSON file.

    :param news_list: List of News objects
    :param path: File path to save the JSON
    """
    data = {
        "generated_at": datetime.now().isoformat(),
        "count": len(news_list),
        "news": [n.to_dict() for n in news_list],
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved {len(news_list)} news items to {path}")