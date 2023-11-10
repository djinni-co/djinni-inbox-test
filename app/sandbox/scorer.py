import abc
from typing import Final

from django.conf import settings
from gensim.utils import simple_preprocess

from .models import JobPosting, Candidate, EnglishLevel
from .utils import cosine_similarity, vectorize, get_choice_index

SCORE_MIN: Final[float] = 0.0
SCORE_MAX: Final[float] = 1.0


class CandidateScorer(abc.ABC):
    def compute(self, candidate: Candidate, job: JobPosting) -> float:
        pass


class SimilarityCandidateScorer(CandidateScorer):
    def compute(self, candidate: Candidate, job: JobPosting) -> float:
        bow = self.parse_job_keywords(job)
        job_vector = vectorize(bow, bow)
        candidate_vector = vectorize(self.parse_candidate_keywords(candidate), bow)

        return cosine_similarity(candidate_vector, job_vector)

    @staticmethod
    def parse_candidate_keywords(candidate: Candidate) -> list[str]:
        dataset: list[str] = [candidate.position, candidate.primary_keyword]
        if candidate.skills_cache:
            dataset.append(candidate.skills_cache)
        if candidate.moreinfo:
            dataset.append(candidate.moreinfo)
        if candidate.looking_for:
            dataset.append(candidate.looking_for)
        if candidate.highlights:
            dataset.append(candidate.highlights)

        return list(set(simple_preprocess(' '.join(dataset), deacc=True)))

    @staticmethod
    def parse_job_keywords(job: JobPosting) -> list[str]:
        dataset: list[str] = [job.position, job.primary_keyword]
        if job.secondary_keyword:
            dataset.append(job.secondary_keyword)

        return list(set(simple_preprocess(' '.join(dataset), deacc=True)))


class WeightCandidateScorer(CandidateScorer):
    def __init__(self, settings_: settings.SCORING_SETTINGS):
        self._exp_weight: float = settings_.SCORE_EXP_WEIGHT
        self._eng_weight: float = settings_.SCORE_ENG_WEIGHT
        self._salary_weight: float = settings_.SCORE_SALARY_WEIGHT
        self._company_type_weight: float = settings_.SCORE_COMPANY_TYPE_WEIGHT

    def compute(self, candidate: Candidate, job: JobPosting) -> float:
        score = SCORE_MIN

        score += self._compute_experience(candidate.experience_years, job.get_job_experience())
        score += self._compute_english(candidate.english_level, job.english_level)
        score += self._compute_salary(candidate.salary_min, job.salary_min, job.salary_max)

        if candidate.uninterested_company_types:
            score += self._compute_company_type(job.company_type, candidate.uninterested_company_types.split(', '))

        return score

    def _compute_experience(self, candidate_exp: float, job_exp: float):
        return (candidate_exp - job_exp) / 10 * self._exp_weight

    def _compute_english(self, candidate_eng: str, job_eng: str):
        candidate_eng = get_choice_index(EnglishLevel, candidate_eng) + 1
        job_eng = get_choice_index(EnglishLevel, job_eng) + 1

        return (candidate_eng - job_eng) / 10 * self._eng_weight

    def _compute_salary(self, candidate_salary: int, job_salary_min: int, job_salary_max: int):
        return -self._salary_weight if candidate_salary > job_salary_max else self._salary_weight if candidate_salary < job_salary_min else 0

    def _compute_company_type(self, company_type: str, exclude_company_types: list[str]):
        return -self._company_type_weight if company_type in exclude_company_types else 0
