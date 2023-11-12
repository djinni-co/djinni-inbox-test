"""
Module: scoring_calculator.py

Provides a scoring mechanism to evaluate the compatibility between a candidate and a job opportunity.

- ScoringCalculator: Calculates a matching score based on English proficiency, work experience, salary expectations,
 keyword matching, and location alignment.

Enums:
- EnglishLevel: Enumerates various levels of English proficiency.
- JobExperience: Enumerates various levels of work experience.
"""
from enum import Enum


class EnglishLevel(Enum):
    NONE = 0
    BASIC = 1
    PRE = 2
    INTERMEDIATE = 3
    UPPER = 4
    FLUENT = 5


class JobExperience(Enum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FIVE = 5


class ScoringCalculator:
    def __init__(self, candidate, job):
        self.candidate = candidate
        self.job = job

    def calculate_score(self):
        score = 0.0

        if self.job is None or self.candidate is None:
            return score

        score += self.calculate_english_level_score()
        score += self.calculate_experience_level_score()
        score += self.calculate_calary_score()
        score += self.keyword_score()
        score += self.location_score()

        return score

    def calculate_english_level_score(self):
        eng_score = 0.0
        job_english_level = self.english_level_mapping.get(self.job.english_level, 0)
        candidate_english_level = self.english_level_mapping.get(self.candidate.english_level, 0)

        if candidate_english_level == job_english_level:
            eng_score += 0.5
        elif candidate_english_level > job_english_level:
            eng_score += 1.0

        return eng_score

    def calculate_experience_level_score(self):
        exp_score = 0.0
        candidat_exp_years = self.candidate.experience_years
        job_exp = self.experience_level_mapping.get(self.job.exp_years, 0)

        if candidat_exp_years == job_exp:
            exp_score += 0.5
        elif candidat_exp_years > job_exp:
            exp_score += 1

        return exp_score

    def calculate_calary_score(self):
        calary_score = 0.0
        job_calary = self.job.salary_max
        candidat_calary = self.candidate.salary_min

        if job_calary >= candidat_calary:
            calary_score += 1

        return calary_score

    def keyword_score(self):
        keyword_score = 0.0
        keyword_job = self.job.primary_keyword

        if self.candidate.skills_cache is not None:
            skill_candidat = self.candidate.skills_cache.split()
            if keyword_job.lower() in [skill.lower() for skill in skill_candidat]:
                keyword_score += 1.0

        return keyword_score

    def location_score(self):
        location_score = 0.0
        job_country = self.job.country
        job_city = self.job.location
        candidat_country = self.candidate.country_code
        candidat_city = self.candidate.city

        if job_country == candidat_country:
            location_score += 0.5
        if job_city == candidat_city:
            location_score += 0.5

        return location_score

    @property
    def english_level_mapping(self):
        return {
            "no_english": EnglishLevel.NONE.value,
            "basic": EnglishLevel.BASIC.value,
            "pre": EnglishLevel.PRE.value,
            "intermediate": EnglishLevel.INTERMEDIATE.value,
            "upper": EnglishLevel.UPPER.value,
            "fluent": EnglishLevel.FLUENT.value,
        }

    @property
    def experience_level_mapping(self):
        return {
            "no_exp": JobExperience.ZERO.value,
            "1y": JobExperience.ONE.value,
            "2y": JobExperience.TWO.value,
            "3y": JobExperience.THREE.value,
            "5y": JobExperience.FIVE.value,
        }
