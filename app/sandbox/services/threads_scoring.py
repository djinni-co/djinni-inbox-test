import dataclasses
from typing import Optional, Dict

from django.conf import settings

from sandbox.models import Candidate, JobPosting, EnglishLevel


@dataclasses.dataclass
class ScoringWeights:
    english_level: float = 0.5
    location: float = 0.5
    experience_years: float = 1.0
    primary_keyword: float = 1.0
    secondary_keyword: float = 1.0
    uninterested_company_type: float = 1.0
    domain_zone: float = 0.5
    salary: float = 1
    skills: float = 1


@dataclasses.dataclass
class CalculatedScore:
    raw_score: Optional[float]
    weighted_score: float


@dataclasses.dataclass
class TotalScore:
    total_score: float
    score_description: Dict[str, Optional[float]]


class ThreadScoringService:

    def __init__(self, candidate: Candidate, job: JobPosting, weights: Optional[ScoringWeights] = None):
        self.weights = weights or ScoringWeights()
        self.candidate = candidate
        self.job = job

    def calculate_english_level_score(self) -> CalculatedScore:
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
        if candidate_level < job_required_level:
            # If candidate_factory's level is less than required, the difference affects the score.
            # The score is reduced by a coefficient based on the level gap.
            # For instance, a coefficient of 0.2 reduces the score by 20% per level gap.
            coefficient = 0.2
            score = max(0, 1 - coefficient * (job_required_level - candidate_level))
        else:
            # If the candidate_factory's level is equal to or greater than the required level, it's a perfect score.
            score = 1.0
        return CalculatedScore(raw_score=score, weighted_score=score * self.weights.english_level)

    def calculate_location_score(self) -> CalculatedScore:
        if not self.job.accept_region:
            # worldwide
            score = 1.0
        elif (self.candidate.country_code == 'UKR' and
              self.job.accept_region in [JobPosting.AcceptRegion.UKRAINE, JobPosting.AcceptRegion.EUROPE]):
            score = 1.0
        elif (self.job.accept_region == JobPosting.AcceptRegion.EUROPE_ONLY and
              self.candidate.country_code in settings.EUROPEAN_COUNTRIES):
            score = 1.0
        elif self.candidate.can_relocate:
            # If the job's region is not fits and the candidate_factory is not from the accepted region,
            # but the candidate_factory is willing to relocate, you might still want to give some score.
            score = 0.5
        else:
            score = 0.0
            # If there is no match and the candidate_factory is not willing to relocate, no points are awarded.
        return CalculatedScore(raw_score=score, weighted_score=score * self.weights.location)

    def calculate_experience_score(self) -> CalculatedScore:
        # Convert job posting experience requirement to a numerical value
        experience_requirements: Dict[str, int] = {
            JobPosting.Experience.ZERO: 0,
            JobPosting.Experience.ONE: 1,
            JobPosting.Experience.TWO: 2,
            JobPosting.Experience.THREE: 3,
            JobPosting.Experience.FIVE: 5,
        }
        required_experience = experience_requirements.get(self.job.exp_years, 0)
        candidate_experience = self.candidate.experience_years

        # If the candidate's experience is equal to or greater than the required experience, full score is given.
        if candidate_experience >= required_experience:
            score = 1.0
        else:
            # If candidate's experience is less than required, the score is reduced proportionally.
            # You can adjust the coefficient based on how strict you want to be about experience.
            coefficient = 0.2  # A smaller coefficient means less penalty for experience gap.
            experience_gap = max(0, required_experience - candidate_experience)
            score = max(0, 1 - coefficient * experience_gap)
        return CalculatedScore(raw_score=score, weighted_score=score * self.weights.experience_years)

    def calculate_domain_zone_score(self) -> CalculatedScore:
        if not self.candidate.domain_zones:
            return CalculatedScore(raw_score=None, weighted_score=0)
        domain_zones = self.candidate.domain_zones.split(', ')
        domain_zones = [zone.lower() for zone in domain_zones]
        score = 0.0
        if self.job.domain.lower() in domain_zones:
            score = 1
        return CalculatedScore(raw_score=score, weighted_score=score * self.weights.domain_zone)

    def calculate_company_type_penalty(self) -> CalculatedScore:
        """
        Assuming uninterested_company_types is a comma-separated string
        return: must return float <0 if a candidate is not interested in the company type
        """
        if not self.candidate.uninterested_company_types:
            return CalculatedScore(raw_score=None, weighted_score=0)
        uninterested_types = self.candidate.uninterested_company_types.split(', ')
        penalty = 0.0
        if self.job.company_type in uninterested_types:
            penalty = -1.0  # This represents a full
        return CalculatedScore(raw_score=penalty, weighted_score=penalty * self.weights.uninterested_company_type)

    def calculate_primary_keyword_score(self) -> CalculatedScore:
        # Assuming exact match for simplicity
        if not self.candidate.primary_keyword:
            return CalculatedScore(raw_score=None, weighted_score=0)
        score = 0.0
        if self.candidate.primary_keyword.lower() == self.job.primary_keyword.lower():
            score = 1.0
        return CalculatedScore(raw_score=score, weighted_score=score * self.weights.primary_keyword)

    def calculate_secondary_keyword_score(self) -> CalculatedScore:
        # Assuming exact match for simplicity
        if not self.candidate.secondary_keyword:
            return CalculatedScore(raw_score=None, weighted_score=0)
        score = 0.0
        if self.candidate.secondary_keyword and self.job.secondary_keyword:
            if self.candidate.secondary_keyword.lower() == self.job.secondary_keyword.lower():
                score = 1.0
        return CalculatedScore(raw_score=score, weighted_score=score * self.weights.secondary_keyword)

    def calculate_salary_score(self) -> CalculatedScore:
        candidate_salary_min = self.candidate.salary_min
        job_salary_min = self.job.salary_min
        job_salary_max = self.job.salary_max

        # If the job has no salary range defined, you might want to return a default score
        if job_salary_min is None or job_salary_max is None:
            score = 0.8
            return CalculatedScore(raw_score=score, weighted_score=score * self.weights.salary)

        # Full score if the candidate's salary expectation is within the job's salary range
        if job_salary_min <= candidate_salary_min <= job_salary_max:
            score = 1
            return CalculatedScore(raw_score=score, weighted_score=score * self.weights.salary)

        # If the candidate's expected salary is less than the job's range, it's a potential bargain
        if candidate_salary_min < job_salary_min:
            return CalculatedScore(raw_score=0.8, weighted_score=0.8 * self.weights.salary)

        # Deduct points if the candidate's expected salary is higher than the job's range
        if candidate_salary_min > job_salary_max:
            # Calculate the percentage the candidate is over the max salary
            excess_percentage = (candidate_salary_min - job_salary_max) / job_salary_max
            # Deduct more points as the candidate's expected salary goes higher over the max salary
            deduction = min(excess_percentage, 1)  # Cap the deduction at 100% of the score
            score = max(0, 1.0 - deduction)
            return CalculatedScore(raw_score=score, weighted_score=score * self.weights.salary)

        return CalculatedScore(raw_score=0, weighted_score=0)

    def calculate_skills_score(self) -> CalculatedScore:
        """
        Calculate the score based on the candidate's skills.
        This is a very simple implementation that only counts the number of matching skills.
        In general, it's a bad idea to use a simple matching algorithm like this.
        If the description says "We don't need Java", this algorithm will still match "Java" as a skill.
        """
        if not self.candidate.skills_cache:
            return CalculatedScore(raw_score=None, weighted_score=0)
        job_description_tokens = set(self.job.long_description.lower().split())
        candidate_skills_tokens = set(self.candidate.skills_cache.lower().split("\n"))
        matching_skills = job_description_tokens.intersection(candidate_skills_tokens)
        score = len(matching_skills) * 0.3
        return CalculatedScore(raw_score=score, weighted_score=score * self.weights.skills)

    def calculate_candidate_score(self) -> TotalScore:
        english_score = self.calculate_english_level_score()
        location_score = self.calculate_location_score()
        experience_score = self.calculate_experience_score()
        primary_keyword_score = self.calculate_primary_keyword_score()
        secondary_keyword_score = self.calculate_secondary_keyword_score()
        domain_zone_score = self.calculate_domain_zone_score()
        company_type_penalty = self.calculate_company_type_penalty()
        salary_score = self.calculate_salary_score()
        skills_score = self.calculate_skills_score()

        weighted_score = (
            english_score.weighted_score +
            location_score.weighted_score +
            experience_score.weighted_score +
            primary_keyword_score.weighted_score +
            secondary_keyword_score.weighted_score +
            domain_zone_score.weighted_score +
            company_type_penalty.weighted_score +
            salary_score.weighted_score +
            skills_score.weighted_score
        )
        score_description = {
            'english_score': english_score.raw_score,
            'location_score': location_score.raw_score,
            'experience_score': experience_score.raw_score,
            'primary_keyword_score': primary_keyword_score.raw_score,
            'secondary_keyword_score': secondary_keyword_score.raw_score,
            'domain_zone_score': domain_zone_score.raw_score,
            'company_type_penalty': company_type_penalty.raw_score,
            'salary_score': salary_score.raw_score,
            'skills_score': skills_score.raw_score,
        }
        return TotalScore(total_score=weighted_score, score_description=score_description)
