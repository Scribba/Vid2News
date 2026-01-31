import os
from dotenv import load_dotenv

from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from src.extracting.prompts import TRANSCRIPT_PARSING_PROMPT
from src.extracting.utils import Transcript, News
from src.utils.logger import logger


DEFAULT_TEMPERATURE = 0.0
DEFAULT_MODEL_NAME = "gpt-4"


class NewsItem(BaseModel):
    """Pydantic model for structured LLM output parsing."""
    title: str = Field(description="Headline for the news item")
    summary: str = Field(description="Brief 2-3 sentence summary")
    content: str = Field(description="Full details and context")
    keywords: list[str] = Field(default_factory=list, description="Relevant keywords")
    category: str = Field(default="", description="News category")
    entities: list[str] = Field(default_factory=list, description="Named entities mentioned")


class NewsExtractionOutput(BaseModel):
    """Pydantic model for the complete extraction result."""
    news_items: list[NewsItem] = Field(default_factory=list, description="List of extracted news items")


class TranscriptParser:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=DEFAULT_MODEL_NAME,
            temperature=DEFAULT_TEMPERATURE,
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        self.prompt = PromptTemplate(
            input_variables=["transcript_text"],
            template=TRANSCRIPT_PARSING_PROMPT,
        )
        self.output_parser = PydanticOutputParser(pydantic_object=NewsExtractionOutput)

        self.chain = self.prompt | self.llm | self.output_parser

    def run(self, transcript: Transcript):
        try:
            response = self.chain.invoke({
                "transcript_text": transcript.text
            })

            news_list = []
            for news_item in response.news_items:
                news = News(
                    **news_item.model_dump(),
                    source_video_title=transcript.title,
                    source_video_url=transcript.url,
                    source_channel=transcript.channel_name
                )
                news_list.append(news)

            logger.debug(f"Extracted {len(news_list)} news items from transcript {transcript.video_id}")
            return news_list

        except Exception as e:
            logger.error(f"Error extracting news from transcript {transcript.video_id}: {e}")
            return []


if __name__ == "__main__":

    load_dotenv("/Users/wnowogor/PycharmProjects/Vid2News/.env")

    transcript = Transcript(
        video_id="dummy_id",
        title="dummy_title",
        text="""How would you describe the European Union in 18 words? >> Which sometimes is too slow for sure
        and is to be reformed for sure, but which is predictable, loyal. This clip from Emanuel Macron's
        speech delivered in classic aviator sunglasses dominated global media coverage not only because of
        the French president's polished oratory presence and confident gestures but because it captured a deeper
        truth about today's European Union especially when set against what is unfolding elsewhere in the world.
        This year's Davos summit, traditionally dismissed as winter camp for the global elite,
        produced more moments like this than usual. And for good reason. If the United States openly reaching for
        the jour European territory in the form of Greenland, the last remaining sense of normality is disappearing.
        Everything's destiny is to change, to be transformed, to perish so that new things can be born.
        Marcos Orurelius once said, \"After years of hesitation and gradual resistance, our European and broader Western
         leaders finally beginning to accept and implement this change.\" Ursula Vanderlayan is often associated with
          speeches that ultimately amount to very little. Was it different this time? Quote, geopolitical shocks can and
        """,
        channel_name="dummy_channel_name",
    )
    parser = TranscriptParser()
    news = parser.run(transcript)

    for news_item in news:
        print(news_item)


