import numpy as np
from numpy.linalg import norm


def cosine_similarity(vector1, vector2):
    return np.dot(vector1, vector2) / (norm(vector1) * norm(vector2))


def vectorize(keywords: list[str], bow: list[str]):
    return [keywords.count(i) for i in bow]
