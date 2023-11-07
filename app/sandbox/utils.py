import spacy
from typing import Union

__all__ = ("calculate_similarity", )


nlp = spacy.load("en_core_web_sm")


def _compare_experience(
        candidate_exp: Union[int, float],
        job_exp: Union[int, float],
        max_difference: float = 5.0
) -> float:

    if candidate_exp > job_exp:
        return 1.0

    difference = abs(candidate_exp - job_exp)
    score = max(0, 1 - (difference / max_difference))
    return score


def calculate_similarity(
        value1: Union[int, float, str], value2: Union[int, float, str]
) -> float:

    if isinstance(value1, (int, float)) or isinstance(value2, (int, float)):
        return _compare_experience(float(value1), float(value2))

    str1 = nlp(value1.lower())
    str2 = nlp(value2.lower())

    return str1.similarity(str2)
