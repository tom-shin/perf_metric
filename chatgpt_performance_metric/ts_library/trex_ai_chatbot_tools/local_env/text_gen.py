from scipy import spatial


def relevancy_score(e1: list[float], e2: list[float]) -> float:
    return spatial.distance.cosine(e1, e2)
