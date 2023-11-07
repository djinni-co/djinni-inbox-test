from typing import Callable, TypedDict, Sequence, Optional, Union

from .models import Candidate, JobPosting
from .utils import calculate_similarity, compare_numbers


MATCHED = 0.65
PARTIAL_MATCHED = 0.3


class CandidateJobMappingField(TypedDict):
    candidate: str
    job: str
    coefficient: float
    converter: Optional[Callable]
    compare_func: Optional[Callable]


def year_normalize(value: Union[int, str, float]) -> int:

    if isinstance(value, (int, float)):
        return int(value)

    if value.endswith('y'):
        return int(value.split('y')[0])

    if "no_exp" in value:
        return 0


def skills_normalizer(value: str) -> str:
    return ",".join(value.split("\n")).lower()


def compare_exp(
        candidate_number: Union[int, float],
        job_number: Union[int, float],
        max_difference: float = 5.0
) -> float:

    if candidate_number > job_number:
        return 1.0

    return compare_numbers(candidate_number, job_number, max_difference)


def compare_salary(
        candidate_number: Union[int, float],
        job_number: Union[int, float],
        max_difference: float = 500.0
) -> float:

    if job_number > candidate_number:
        return 1.0

    return compare_numbers(candidate_number, job_number, max_difference)


COEFFICIENTS_VERSION_1 = (
    CandidateJobMappingField(
        candidate='position', job='position', coefficient=1.2,
        converter=str.lower, compare_func=calculate_similarity
    ),
    CandidateJobMappingField(
        candidate='primary_keyword', job='primary_keyword', coefficient=1.3,
        converter=str.lower, compare_func=calculate_similarity
    ),
    CandidateJobMappingField(
        candidate='secondary_keyword', job='secondary_keyword',
        coefficient=1, converter=str.lower, compare_func=calculate_similarity
    ),
    CandidateJobMappingField(
        candidate='salary_min', job='salary_max', coefficient=1,
        converter=lambda x: x, compare_func=compare_salary
    ),
    CandidateJobMappingField(
        candidate='employment', job='employment', coefficient=0.5,
        converter=str.lower, compare_func=calculate_similarity
    ),
    CandidateJobMappingField(
        candidate='experience_years', job='exp_years', coefficient=1.5,
        converter=year_normalize, compare_func=compare_exp
    ),
    CandidateJobMappingField(
        candidate='english_level', job='english_level', coefficient=1,
        converter=str.lower, compare_func=calculate_similarity
    ),
    CandidateJobMappingField(
        candidate='skills_cache', job='extra_keywords', coefficient=1,
        converter=skills_normalizer, compare_func=calculate_similarity
    ),
    CandidateJobMappingField(
        candidate='skills_cache', job='primary_keyword', coefficient=0.5,
        converter=skills_normalizer, compare_func=calculate_similarity
    )
)


COEFFICIENTS_VERSION_2 = (
    CandidateJobMappingField(
        candidate='position', job='position', coefficient=1.5,
        converter=str.lower, compare_func=calculate_similarity
    ),
    CandidateJobMappingField(
        candidate='primary_keyword', job='primary_keyword', coefficient=1.5,
        converter=str.lower, compare_func=calculate_similarity
    ),
    CandidateJobMappingField(
        candidate='secondary_keyword', job='secondary_keyword',
        coefficient=1, converter=str.lower, compare_func=calculate_similarity
    ),
    CandidateJobMappingField(
        candidate='salary_min', job='salary_max', coefficient=1,
        converter=lambda x: x, compare_func=compare_salary
    ),
    CandidateJobMappingField(
        candidate='employment', job='employment', coefficient=0.5,
        converter=str.lower, compare_func=calculate_similarity
    ),
    CandidateJobMappingField(
        candidate='experience_years', job='exp_years', coefficient=1.5,
        converter=year_normalize, compare_func=compare_exp
    ),
    CandidateJobMappingField(
        candidate='english_level', job='english_level', coefficient=1.2,
        converter=str.lower, compare_func=calculate_similarity
    ),
    CandidateJobMappingField(
        candidate='skills_cache', job='extra_keywords', coefficient=1,
        converter=skills_normalizer, compare_func=calculate_similarity
    ),
    CandidateJobMappingField(
        candidate='skills_cache', job='primary_keyword', coefficient=0.3,
        converter=skills_normalizer, compare_func=calculate_similarity
    )
)


def find_similarities(
        candidate: Candidate,
        job: JobPosting,
        weightings: Sequence[CandidateJobMappingField]
) -> float:
    similarity_score = 0

    min_score = 0
    max_score = sum([v.get('coefficient') for v in weightings])

    for field_obj in weightings:
        candidate_field = field_obj.get("candidate")
        job_field = field_obj.get("job")

        candidate_value = getattr(candidate, candidate_field, None)
        job_value = getattr(job, job_field, None)

        if not candidate_value or not job_value:
            continue

        weight: float = field_obj.get("coefficient")
        converter: Callable = field_obj.get("converter", lambda x: x)
        compare_func: Callable = field_obj.get("compare_func", lambda x: x)

        field_similarity: float = (
                compare_func(
                    converter(candidate_value), converter(job_value)
                ) * weight
        )

        print(f"{job_value=} == {candidate_value=}: SCORE: {field_similarity}")

        similarity_score += field_similarity

    return round((similarity_score - min_score) / (max_score - min_score), 2)
