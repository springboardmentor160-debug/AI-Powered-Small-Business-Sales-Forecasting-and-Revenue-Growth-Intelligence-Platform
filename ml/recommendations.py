"""M3: Collaborative Filtering (customer-product matrix + cosine similarity)."""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from common import load_online, product_names

TOP_PRODUCTS = 1500   # keep the matrix dense enough to be useful and small enough to be fast


def build_matrix(df, top_n=TOP_PRODUCTS):
    pop = df.groupby("StockCode")["InvoiceNo"].nunique().nlargest(top_n).index
    d = df[df["StockCode"].isin(pop)]
    return d.pivot_table(index="CustomerID", columns="StockCode", values="InvoiceNo", aggfunc="nunique", fill_value=0)


class CFRecommender:
    def __init__(self, matrix, names=None, n_neighbors=20):
        self.m, self.names, self.k = matrix, names or {}, n_neighbors
        self.index = {c: i for i, c in enumerate(matrix.index)}
        self.vals = matrix.values.astype("float32")
        self.sim = cosine_similarity(self.vals).astype("float32")
        np.fill_diagonal(self.sim, 0)

    def recommend(self, customer_id, top_n=3):
        i = self.index[customer_id]
        nb = np.argpartition(-self.sim[i], self.k)[: self.k]
        scores = self.sim[i, nb] @ (self.vals[nb] > 0)          # similarity-weighted votes of look-alike customers
        scores[self.vals[i] > 0] = -1                             # never recommend what they already bought
        top = np.argsort(-scores)[:top_n]
        return [{"code": self.m.columns[j], "name": self.names.get(self.m.columns[j], self.m.columns[j]),
                 "score": round(float(scores[j]), 3)} for j in top if scores[j] > 0]


if __name__ == "__main__":
    df = load_online()
    rec = CFRecommender(build_matrix(df), product_names(df))
    cid = df["CustomerID"].iloc[0]
    print(cid, rec.recommend(cid))
