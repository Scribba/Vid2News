from dataclasses import dataclass


@dataclass
class GeneratedNews:
    title: str
    content: str
    source_video_urls: list[str]
    source_channels: list[str]