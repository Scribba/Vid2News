from dataclasses import dataclass


@dataclass
class GeneratedNews:
    content: str
    source_video_urls: list[str]
    source_channels: list[str]