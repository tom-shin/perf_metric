from numpy import dot
from numpy.linalg import norm


def relevancy_score(e1: list[float], e2: list[float]) -> float:
    return 1 - dot(e1, e2) / (norm(e1) * norm(e2))
