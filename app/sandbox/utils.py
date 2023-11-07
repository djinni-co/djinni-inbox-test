import spacy
from typing import Union

__all__ = ("calculate_similarity", "compare_numbers")


nlp = spacy.load("en_core_web_sm")


def compare_numbers(
        candidate_number: Union[int, float],
        job_number: Union[int, float],
        max_difference: float
    ) -> float:

    difference = abs(candidate_number - job_number)
    score = max(0, 1 - (difference / max_difference))
    return score


def calculate_similarity(
        value1: Union[int, float, str], value2: Union[int, float, str]
) -> float:

    str1 = nlp(value1.lower())
    str2 = nlp(value2.lower())

    return str1.similarity(str2)
