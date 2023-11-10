from django.test import TestCase
import os
from django import setup


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
setup()

from .models import Candidate, EnglishLevel, JobPosting, LegacyUACity, MessageThread
from .views import (
    _calculate_prog_lang_coefficient,
    _calculate_salary_coefficient,
    _calculate_location_coefficient,
    _calculate_english_level_coefficient,
    _calculate_experiance_coefficient,
    _calculate_candidate_suitability,
)


# Create your tests here.
class ProgrammingLanguageCalculationTests(TestCase):
    def setUp(self):
        self.candidate = Candidate()
        self.job = JobPosting()

    def test_calculate_prog_lang_coefficient_same_keywords(self) -> None:
        self.candidate.primary_keyword = "Python"
        self.job.primary_keyword = "Python"

        coeff = _calculate_prog_lang_coefficient(self.candidate, self.job)
        assert coeff == 0.75

    def test_calculate_prog_lang_coefficient_different_keywords(self) -> None:
        self.candidate.primary_keyword = "Python"
        self.job.primary_keyword = "Java"

        coeff = _calculate_prog_lang_coefficient(self.candidate, self.job)
        assert coeff == 0.5

    def test_calculate_prog_lang_coefficient_vacancy_secondary_keyword(self) -> None:
        self.candidate.primary_keyword = "Python"
        self.job.primary_keyword = "Java"
        self.job.secondary_keyword = "Golang"

        coeff = _calculate_prog_lang_coefficient(self.candidate, self.job)
        assert coeff == 0.375

    def test_calculate_prog_lang_coefficient_vacancy_matched_secondary_keyword(
        self,
    ) -> None:
        self.candidate.primary_keyword = "Python"
        self.candidate.secondary_keyword = "Golang"
        self.job.primary_keyword = "Java"
        self.job.secondary_keyword = "Golang"

        coeff = _calculate_prog_lang_coefficient(self.candidate, self.job)
        assert coeff == 0.625

    def test_calculate_prog_lang_coefficient_vacancy_fully_matched(
        self,
    ) -> None:
        self.candidate.primary_keyword = "Python"
        self.candidate.secondary_keyword = "Golang"
        self.job.primary_keyword = "Python"
        self.job.secondary_keyword = "Golang"

        coeff = _calculate_prog_lang_coefficient(self.candidate, self.job)
        assert coeff == (0.5 + 0.25 + 0.125)


class SalaryCalculationTests(TestCase):
    def setUp(self):
        self.candidate = Candidate()
        self.job = JobPosting()

    def test_calculate_salary_coefficient(self) -> None:
        self.candidate.salary_min = 1600
        self.job.salary_min = 1
        self.job.salary_max = 2000

        assert _calculate_salary_coefficient(self.candidate, self.job) == 1.0

    def test_calculate_salary_coefficient_candidate_wants_too_much(self) -> None:
        self.candidate.salary_min = 16000
        self.job.salary_min = 1
        self.job.salary_max = 2000

        self.assertEqual(_calculate_salary_coefficient(self.candidate, self.job), 0.5)


class LocationCalculationTests(TestCase):
    def setUp(self):
        self.candidate = Candidate()
        self.job = JobPosting()

    def test_same_location(self) -> None:
        self.candidate.location = LegacyUACity.DNIPRO
        self.job.location = LegacyUACity.DNIPRO

        self.assertEqual(
            _calculate_location_coefficient(self.candidate.location, self.job.location),
            1.0,
        )

    def test_different_location(self) -> None:
        self.candidate.location = LegacyUACity.DNIPRO
        self.job.location = LegacyUACity.KHARKIV

        self.assertEqual(
            _calculate_location_coefficient(self.candidate.location, self.job.location),
            0.5,
        )


class EnglishLevelCalculationTests(TestCase):
    def setUp(self):
        self.candidate = Candidate()
        self.job = JobPosting()

    def test_same_level(self) -> None:
        self.candidate.english_level = EnglishLevel.PRE
        self.job.english_level = EnglishLevel.PRE

        self.assertEqual(
            _calculate_english_level_coefficient(
                self.candidate.english_level, self.job.english_level
            ),
            1.0,
        )

    def test_candidate_one_level_lower_than_required(self) -> None:
        self.candidate.english_level = EnglishLevel.BASIC
        self.job.english_level = EnglishLevel.PRE

        self.assertEqual(
            _calculate_english_level_coefficient(
                self.candidate.english_level, self.job.english_level
            ),
            0.9,
        )

    def test_candidate_two_level_lower_than_required(self) -> None:
        self.candidate.english_level = EnglishLevel.NONE
        self.job.english_level = EnglishLevel.PRE

        self.assertEqual(
            _calculate_english_level_coefficient(
                self.candidate.english_level, self.job.english_level
            ),
            0.8,
        )

    def test_candidate_higher_than_required(self) -> None:
        self.candidate.english_level = EnglishLevel.INTERMEDIATE
        self.job.english_level = EnglishLevel.BASIC

        self.assertEqual(
            _calculate_english_level_coefficient(
                self.candidate.english_level, self.job.english_level
            ),
            1.2,
        )


class ExperianceCalculationTests(TestCase):
    def setUp(self):
        self.candidate = Candidate()
        self.job = JobPosting()

    def test_experiance(self) -> None:
        self.candidate.experience_years = 3.0
        self.job.exp_years = "3y"

        self.assertEqual(
            _calculate_experiance_coefficient(
                self.candidate.experience_years, self.job.exp_years
            ),
            1.0,
        )

    def test_candidate_has_six_month_more_exp(self) -> None:
        self.candidate.experience_years = 3.5
        self.job.exp_years = "3y"

        self.assertEqual(
            _calculate_experiance_coefficient(
                self.candidate.experience_years, self.job.exp_years
            ),
            1.06,
        )

    def test_candidate_has_six_month_less_exp(self) -> None:
        self.candidate.experience_years = 2.5
        self.job.exp_years = "3y"

        self.assertEqual(
            _calculate_experiance_coefficient(
                self.candidate.experience_years, self.job.exp_years
            ),
            0.94,
        )


class CalculateSuitabilityTest(TestCase):
    def setUp(self):
        self.candidate = Candidate()
        self.job = JobPosting()
        self.thread = MessageThread(job=self.job, candidate=self.candidate)

    def test_calculate_suitability_with_defaut_category_weights(self) -> None:
        coeff = _calculate_candidate_suitability(self.thread)
        self.assertEqual(coeff, 4.75)

    def test_calculate_suitability_with_custom_category_weights(self) -> None:
        self.thread.job.primary_keyword_weight = 1.2
        self.thread.job.english_level_weight = 1.3


        coeff = _calculate_candidate_suitability(self.thread)
        self.assertEqual(coeff, 5.2)