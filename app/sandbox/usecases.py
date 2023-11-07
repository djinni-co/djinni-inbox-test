from typing import Callable, TypedDict, Sequence, Optional, Union

from .models import Candidate, JobPosting
from .utils import calculate_similarity


MATCHED = 0.65
PARTIAL_MATCHED = 0.3


class CandidateJobMappingField(TypedDict):
    candidate: str
    job: str
    coefficient: float
    converter: Optional[Callable]


def year_normalize(value: Union[int, str, float]) -> int:

    if isinstance(value, (int, float)):
        return int(value)

    if value.endswith('y'):
        return int(value.split('y')[0])

    if "no_exp" in value:
        return 0


def skills_normalizer(value: str) -> str:
    return " ".join(value.split("\n")).lower()


COEFFICIENTS_VERSION_1 = (
    CandidateJobMappingField(
        candidate='position', job='position', coefficient=1.2,
        converter=str.lower
    ),
    CandidateJobMappingField(
        candidate='primary_keyword', job='primary_keyword', coefficient=1.3,
        converter=str.lower
    ),
    CandidateJobMappingField(
        candidate='secondary_keyword', job='secondary_keyword',
        coefficient=1,
        converter=str.lower
    ),
    CandidateJobMappingField(
        candidate='salary_min', job='salary_max', coefficient=1,
        converter=lambda x: x
    ),
    CandidateJobMappingField(
        candidate='employment', job='employment', coefficient=0.5,
        converter=str.lower
    ),
    CandidateJobMappingField(
        candidate='experience_years', job='exp_years', coefficient=1.5,
        converter=year_normalize
    ),
    CandidateJobMappingField(
        candidate='english_level', job='english_level', coefficient=1,
        converter=str.lower
    ),
    CandidateJobMappingField(
        candidate='skills_cache', job='extra_keywords', coefficient=1,
        converter=skills_normalizer
    ),
    CandidateJobMappingField(
        candidate='skills_cache', job='primary_keyword', coefficient=0.5,
        converter=skills_normalizer
    )
)


COEFFICIENTS_VERSION_2 = (
    CandidateJobMappingField(
        candidate='position', job='position', coefficient=1.5,
        converter=str.lower
    ),
    CandidateJobMappingField(
        candidate='primary_keyword', job='primary_keyword', coefficient=1.5,
        converter=str.lower
    ),
    CandidateJobMappingField(
        candidate='secondary_keyword', job='secondary_keyword',
        coefficient=1.3,
        converter=str.lower
    ),
    CandidateJobMappingField(
        candidate='salary_min', job='salary_max', coefficient=1.5,
        converter=lambda x: x
    ),
    CandidateJobMappingField(
        candidate='employment', job='employment', coefficient=1,
        converter=str.lower
    ),
    CandidateJobMappingField(
        candidate='experience_years', job='exp_years', coefficient=2,
        converter=year_normalize
    ),
    CandidateJobMappingField(
        candidate='english_level', job='english_level', coefficient=2,
        converter=str.lower
    ),
    CandidateJobMappingField(
        candidate='skills_cache', job='extra_keywords', coefficient=0.5,
        converter=skills_normalizer
    ),
    CandidateJobMappingField(
        candidate='skills_cache', job='primary_keyword', coefficient=0.3,
        converter=skills_normalizer
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

        field_similarity: float = (
                calculate_similarity(
                    converter(candidate_value), converter(job_value)
                ) * weight
        )

        print(f"{job_value=} == {candidate_value=}: SCORE: {field_similarity}")

        similarity_score += field_similarity

    return round((similarity_score - min_score) / (max_score - min_score), 2)
