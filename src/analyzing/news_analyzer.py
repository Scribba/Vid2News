import os
from pathlib import Path

from scipy.special.cython_special import fdtri
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

from src.utils.grist_client import GristClient
from src.analyzing.prompts import NEWS_ANALYSIS_PROMPT_TEMPLATE


DEFAULT_MODEL_NAME = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.0


class NewsAnalyzerOutput(BaseModel):
    approved: bool = Field(description="Whether or not the news item is approved")
    score: int = Field(description="Quality score of the news item")


class NewsAnalyzer:
    def __init__(self, grist_client: GristClient):
        self.grist_client = grist_client
        self.llm = ChatOpenAI(
            model=DEFAULT_MODEL_NAME,
            temperature=DEFAULT_TEMPERATURE,
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        self.prompt = PromptTemplate(
            input_variables=["title", "content"],
            template=NEWS_ANALYSIS_PROMPT_TEMPLATE,
        )
        self.output_parser = PydanticOutputParser(pydantic_object=NewsAnalyzerOutput)

        self.chain = self.prompt | self.llm | self.output_parser

    def _analyze(self, title, content) -> tuple:
        results = self.chain.invoke({
            "title": title,
            "content": content,
        })
        status = "approved" if results.approved else "not approved"
        return status, results.score

    def analyze_all(self):
        news_df = self.grist_client.fetch_table()
        df_not_approved = news_df[news_df["status"] == "not approved"]

        for row in df_not_approved.iterrows():
            index = row[0]
            title = row[1]["title"]
            content = row[1]["content"]

            is_approved, score = self._analyze(title, content)
            if is_approved:
                updates = [
                    {
                        "id": index + 1,
                        "fields": {
                            "status": "approved",
                            "score": score
                        }
                    }
                ]
                self.grist_client.update_rows(updates)


if __name__ == "__main__":
    from dotenv import load_dotenv
    from src.utils.path_utils import get_repo_root

    repo_root = get_repo_root(Path(__file__))
    load_dotenv(repo_root / ".env")

    analyzer = NewsAnalyzer(grist_client=GristClient(
        document_id="n5DoTVv7Zr4q", table_id="NaGlobalnie"
    ))
    analyzer.analyze_all()
