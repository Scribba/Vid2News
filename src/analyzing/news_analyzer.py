from scipy.special.cython_special import fdtri

from src.utils.grist_client import GristClient


class NewsAnalyzer:
    def __init__(self, grist_client: GristClient):
        self.grist_client = grist_client

    def analyze_all(self):
        news_df = self.grist_client.fetch_table()
        df_not_approved = news_df[news_df["approved"] == "not approved"]
