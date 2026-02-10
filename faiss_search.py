# faiss_search.py
import faiss
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import os

class NCOSemanticSearch:
    def __init__(self, assets_dir="faiss_assets"):
        self.assets_dir = assets_dir

        self.index = faiss.read_index(
            os.path.join(assets_dir, "nco_faiss.index")
        )

        self.df = pd.read_csv(
            os.path.join(assets_dir, "index_df_canonical.csv")
        ).fillna("")

        self.model = SentenceTransformer(
            os.path.join(assets_dir, "sbert_nco_finetuned")
        )

    def search(self, query, k=3):
        emb = self.model.encode(
            [query],
            normalize_embeddings=True
        )

        D, I = self.index.search(
            np.array(emb).astype("float32"), k
        )

        results = []
        for score, idx in zip(D[0], I[0]):
            row = self.df.iloc[idx]
            results.append({
                "score": float(score),
                "NCO_Code": row["NCO_Code"],
                "Title": row["Title"],
                "Description": row.get("Description", "")
            })
        return results

