import os
import json
from typing import Optional

import umap
import hdbscan
from openai import OpenAI
import pandas as pd
import numpy as np

from src.utils.logger import logger
from src.extracting.utils import News


class NewsClusteringEngine:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.df = None

    def get_clusters(
        self,
        news: list[News],
        json_save_path: Optional[str] = None,
        dim_red_n_neighbors: int = 5,
        dim_red_n_components: int = 10,
        min_cluster_size: int = 2,
        min_samples: int = 1,
        cluster_selection_method: str = "eom",
        cluster_distance_metric: str = "euclidean",
    ):
        self.df = pd.DataFrame([n.to_dict() for n in news])
        self.df["text_for_embedding"] = self.df.apply(self._prepare_text_for_embedding, axis=1)

        texts = self.df["text_for_embedding"].tolist()
        embeddings = self._get_embeddings(texts)
        embeddings_array = np.array(embeddings)

        umap_reducer_clustering = umap.UMAP(
            n_neighbors=dim_red_n_neighbors,
            n_components=dim_red_n_components,
            min_dist=0.0,
            metric="cosine",
            random_state=42
        )
        embeddings_reduced_clustering = umap_reducer_clustering.fit_transform(embeddings_array)

        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric=cluster_distance_metric,
            cluster_selection_method=cluster_selection_method,
            prediction_data=True
        )
        logger.info("Clustering...")
        cluster_labels = clusterer.fit_predict(embeddings_reduced_clustering)

        self.df["cluster"] = cluster_labels

        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        logger.info(f"Number of clusters found: {n_clusters}")
        logger.info(f"\nCluster distribution: %s", self.df["cluster"].value_counts().sort_index())

        if json_save_path:
            grouped = (
                self.df
                .groupby("cluster")
                .apply(lambda g: g.to_dict(orient="records"))
                .to_dict()
            )

            with open(json_save_path, "w", encoding="utf-8") as f:
                json.dump(grouped, f, ensure_ascii=False, indent=2)

        return self.df

    @staticmethod
    def _prepare_text_for_embedding(row: pd.Series) -> str:
        """Combine relevant fields into a single text for embedding."""
        parts = [
            f"Title: {row['title']}",
            f"Summary: {row['summary']}",
            f"Content: {row['content']}",
            f"Keywords: {', '.join(row['keywords'])}",
            f"Category: {row['category']}",
        ]
        return "\n".join(parts)

    def _get_embeddings(self, texts: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
        """Get embeddings for a list of texts using OpenAI API."""
        response = self.client.embeddings.create(
            input=texts,
            model=model
        )
        return [item.embedding for item in response.data]


if __name__ == "__main__":
    from dotenv import load_dotenv
    from pathlib import Path
    from src.utils.path_utils import get_repo_root

    repo_root = get_repo_root(Path(__file__))
    load_dotenv(repo_root / ".env")

    with open(repo_root / "src" / "extracting" / "news.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    news = []
    for item in data["news_items"]:
        news.append(News.from_dict(item))

    clustering_engine = NewsClusteringEngine()
    cluster_df = clustering_engine.get_clusters(news=news, json_save_path="clusters.json")