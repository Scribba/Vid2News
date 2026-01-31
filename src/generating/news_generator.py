import os

import pandas as pd
import pydantic
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from src.generating.utils import GeneratedNews
from src.generating.prompts import POST_GENERATING_PROMPT
from src.utils.logger import logger


DEFAULT_DF_COLUMNS = ["title", "content", "keywords", "source_channel", "source_video_url", "category"]
DEFAULT_TEMPERATURE = 0.5
DEFAULT_MODEL_NAME = "gpt-4o-mini"


class GeneratedNewsItem(BaseModel):
    title: str = pydantic.Field(description="Title of the news")
    content: str = pydantic.Field(description="Content of the generated news")


class NewsGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=DEFAULT_MODEL_NAME,
            temperature=DEFAULT_TEMPERATURE,
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        self.prompt = PromptTemplate(
            input_variables=["news_list"],
            template=POST_GENERATING_PROMPT,
        )
        self.output_parser = PydanticOutputParser(pydantic_object=GeneratedNewsItem)

        self.chain = self.prompt | self.llm | self.output_parser

    def generate(self, text: str):
        try:
            response = self.chain.invoke({"news_list": text})
            news_content = response

            logger.debug(f"News generated: {news_content}")
            return news_content

        except Exception as e:
            logger.error(f"Error during news generation: {e}")
            return []

    def generate_from_df(self, df: pd.DataFrame):
        prompts, metadata = self._process_df(df)
        generated_news = []
        for prompt, meta in zip(prompts, metadata):
            news = self.generate(prompt)
            generated_news.append(GeneratedNews(
                title=news.title,
                content=news.content,
                source_video_urls=meta["source_video_urls"],
                source_channels=meta["source_channels"],
            ))
        return generated_news

    def _process_df(self, df: pd.DataFrame):
        news_prompts = []
        metadata = []
        for cluster_idx in df["cluster"].unique():
            df_subset = df[df["cluster"] == cluster_idx][DEFAULT_DF_COLUMNS]

            news_cluster_prompt = f"""
            ### NEWS CLUSTER
            keywords: {list(df_subset['keywords'].explode().unique())}
            category: {list(df_subset['category'].explode().unique())}
            """
            for row in df_subset.itertuples():
                news_cluster_prompt += f"""
                - NEWS
                {row.title}
                {row.content}
                """

            news_prompts.append(news_cluster_prompt)
            metadata.append({
                "source_video_urls": [list(df_subset["source_video_url"].unique())],
                "source_channels": [list(df_subset["source_channel"].unique())],
            })

        return news_prompts, metadata