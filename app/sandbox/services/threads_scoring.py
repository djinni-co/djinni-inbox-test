import dataclasses
from typing import Optional, Dict

from django.conf import settings

from sandbox.models import Candidate, JobPosting, EnglishLevel


@dataclasses.dataclass
class ScoringWeights:
    english_level: float = 0.5
    location: float = 0.5


class ThreadScoringService:

    def __init__(self, candidate: Candidate, job: JobPosting, weights: Optional[ScoringWeights] = None):
        self.weights = weights or ScoringWeights()
        self.candidate = candidate
        self.job = job

    def calculate_english_level_score(self) -> float:
        english_levels: Dict[str, int] = {
            EnglishLevel.NONE: 0,
            EnglishLevel.BASIC: 1,
            EnglishLevel.PRE: 2,
            EnglishLevel.INTERMEDIATE: 3,
            EnglishLevel.UPPER: 4,
            EnglishLevel.FLUENT: 5
        }
        candidate_level = english_levels.get(self.candidate.english_level, 0)
        job_required_level = english_levels.get(self.job.english_level, 0)
        # If the candidate_factory's level is equal to or greater than the required level, it's a perfect score.
        if candidate_level >= job_required_level:
            return 1.0
        # If candidate_factory's level is less than required, the difference affects the score.
        # The score is reduced by a coefficient based on the level gap.
        # For instance, a coefficient of 0.2 reduces the score by 20% per level gap.
        coefficient = 0.2
        score = max(0, 1 - coefficient * (job_required_level - candidate_level))
        return score

    def calculate_location_score(self) -> float:
        if (self.candidate.country_code == 'UKR' and
            self.job.accept_region in [JobPosting.AcceptRegion.UKRAINE, JobPosting.AcceptRegion.EUROPE]):
            return 1
        if (self.job.accept_region == JobPosting.AcceptRegion.EUROPE_ONLY and
            self.candidate.country_code in settings.EUROPEAN_COUNTRIES):
            return 1

        # If the job's region is not fits and the candidate_factory is not from the accepted region,
        # but the candidate_factory is willing to relocate, you might still want to give some score.
        if self.candidate.can_relocate:
            # You can tweak this score based on how much you value the willingness to relocate.
            return 0.5

        # If there is no match and the candidate_factory is not willing to relocate, no points are awarded.
        return 0

    def calculate_candidate_score(self) -> float:
        total_score = 0.0
        total_score += self.calculate_english_level_score() * self.weights.english_level
        total_score += self.calculate_location_score() * self.weights.location
        return total_score
