from django.test import TestCase
import os
from django import setup


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
setup()

from .models import Candidate, JobPosting
from .views import _calcualte_prog_lang_coefficient


# Create your tests here.
class InboxTests(TestCase):
    def setUp(self):
        self.candidate = Candidate()
        self.job = JobPosting()

    def test_calcualte_prog_lang_coefficient_same_keywords(self) -> None:
        self.candidate.primary_keyword = "Python"
        self.job.primary_keyword = "Python"

        coeff = _calcualte_prog_lang_coefficient(self.candidate, self.job)
        assert coeff == 1

    def test_calcualte_prog_lang_coefficient_different_keywords(self) -> None:
        self.candidate.primary_keyword = "Python"
        self.job.primary_keyword = "Java"

        coeff = _calcualte_prog_lang_coefficient(self.candidate, self.job)
        assert coeff == 0.5

    def test_calculate_prog_lang_coefficient_vacancy_secondary_keyword(self) -> None:
        self.candidate.primary_keyword = "Python"
        self.job.primary_keyword = "Java"
        self.job.secondary_keyword = "Golang"

        coeff = _calcualte_prog_lang_coefficient(self.candidate, self.job)
        assert coeff == 0.9

    # def test_calculate_prog_lang_coefficient_vacancy_secondary_keyword(self) -> None:
    #     self.candidate.primary_keyword = "Python"
    #     self.job.primary_keyword = "Java"
    #     self.job.secondary_keyword = "Golang"

    #     coeff = _calcualte_prog_lang_coefficient(self.candidate, self.job)
    #     assert coeff == 0.9
