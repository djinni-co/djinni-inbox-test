import pytest

from sandbox.models import EnglishLevel, JobPosting
from sandbox.services.threads_scoring import ThreadScoringService


@pytest.mark.django_db
def test_gte_calculate_english_level_score(job_posting_factory, candidate_factory):
    # Test case where the candidate_factory's English is equal the requirement level
    job_posting = job_posting_factory(english_level=EnglishLevel.NONE)
    candidate_instance = candidate_factory(english_level=EnglishLevel.NONE)
    service = ThreadScoringService(candidate=candidate_instance, job=job_posting)
    assert service.calculate_english_level_score() == 1
    # Test case where the candidate_factory's English is greater the requirement level

    job_posting = job_posting_factory(english_level=EnglishLevel.PRE)
    candidate_instance = candidate_factory(english_level=EnglishLevel.INTERMEDIATE)
    service = ThreadScoringService(candidate=candidate_instance, job=job_posting)
    assert service.calculate_english_level_score() == 1


@pytest.mark.django_db
def test_lt_calculate_english_level_score(job_posting_factory, candidate_factory):
    # Test case where the candidate_factory's English is one level below the requirement
    job_instance = job_posting_factory(english_level=EnglishLevel.BASIC)
    candidate_instance = candidate_factory(english_level=EnglishLevel.NONE)
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    # Assuming a coefficient of 0.2, the score should be 0.8
    assert service.calculate_english_level_score() == 0.8

    # Test case where the candidate_factory's English is two levels below the requirement
    job_instance = job_posting_factory(english_level=EnglishLevel.INTERMEDIATE)
    candidate_instance = candidate_factory(english_level=EnglishLevel.BASIC)
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    # Assuming a coefficient of 0.2, the score should be 0.6
    assert service.calculate_english_level_score() == 0.6


@pytest.mark.django_db
def test_location_score_ukraine_region(job_posting_factory, candidate_factory):
    job_instance = job_posting_factory(accept_region=JobPosting.AcceptRegion.UKRAINE)
    candidate_instance = candidate_factory(country_code='UKR', can_relocate=False)
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    assert service.calculate_location_score() == 1


@pytest.mark.django_db
def test_location_score_europe_region(job_posting_factory, candidate_factory):
    job_instance = job_posting_factory(accept_region=JobPosting.AcceptRegion.EUROPE)
    candidate_instance = candidate_factory(country_code='UKR', can_relocate=False)
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    assert service.calculate_location_score() == 1


@pytest.mark.django_db
def test_location_score_europe_only_region(job_posting_factory, candidate_factory):
    job_instance = job_posting_factory(accept_region=JobPosting.AcceptRegion.EUROPE_ONLY)
    candidate_instance = candidate_factory(
        country_code='DEU',
        can_relocate=False
        )  # Assuming 'DEU' is a European country code
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    assert service.calculate_location_score() == 1


@pytest.mark.django_db
def test_location_score_willing_to_relocate(job_posting_factory, candidate_factory):
    job_instance = job_posting_factory(accept_region=JobPosting.AcceptRegion.EUROPE_ONLY)
    candidate_instance = candidate_factory(country_code='USA', can_relocate=True)
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    assert service.calculate_location_score() == 0.5


@pytest.mark.django_db
def test_location_score_not_willing_to_relocate(job_posting_factory, candidate_factory):
    job_instance = job_posting_factory(accept_region=JobPosting.AcceptRegion.EUROPE_ONLY)
    candidate_instance = candidate_factory(country_code='USA', can_relocate=False)
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    assert service.calculate_location_score() == 0


@pytest.mark.django_db
def test_location_score_no_match_and_not_willing_to_relocate(job_posting_factory, candidate_factory):
    job_instance = job_posting_factory(accept_region=JobPosting.AcceptRegion.UKRAINE)
    candidate_instance = candidate_factory(country_code='USA', can_relocate=False)
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    assert service.calculate_location_score() == 0
