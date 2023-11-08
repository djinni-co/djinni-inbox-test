import pytest

from sandbox.models import EnglishLevel, JobPosting
from sandbox.services.threads_scoring import ThreadScoringService, ScoringWeights

mock_jobposting_long_description = """**Responsibilities:**
        Design and develop website for our education platform and internal services;
        Set up interfaces to interact with back-end infrastructure;
        In cooperation with CTO participate in developing system architecture;
        Write efficient, scalable, and maintainable code that will help iterate quickly and safely.

        **Requirements:**
        Fluent knowledge of JavaScript and TypeScript;
        Familiarity with modern frameworks/libraries (ideally both React and Vue);
        Experience working in a team environment (familiarity with Git, habit of writing clean and well-documented code).

        **Will be a plus:**
        Understanding of SSR;
        Familiarity with GraphQL.
        """


@pytest.mark.django_db
def test_gte_calculate_english_level_score(job_posting_factory, candidate_factory):
    # Test case where the candidate_factory's English is equal the requirement level
    job_posting = job_posting_factory(english_level=EnglishLevel.NONE)
    candidate_instance = candidate_factory(english_level=EnglishLevel.NONE)
    service = ThreadScoringService(candidate=candidate_instance, job=job_posting)
    assert service.calculate_english_level_score().raw_score == 1
    # Test case where the candidate_factory's English is greater the requirement level

    job_posting = job_posting_factory(english_level=EnglishLevel.PRE)
    candidate_instance = candidate_factory(english_level=EnglishLevel.INTERMEDIATE)
    service = ThreadScoringService(candidate=candidate_instance, job=job_posting)
    assert service.calculate_english_level_score().raw_score == 1


@pytest.mark.django_db
def test_lt_calculate_english_level_score(job_posting_factory, candidate_factory):
    # Test case where the candidate_factory's English is one level below the requirement
    job_instance = job_posting_factory(english_level=EnglishLevel.BASIC)
    candidate_instance = candidate_factory(english_level=EnglishLevel.NONE)
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    # Assuming a coefficient of 0.2, the score should be 0.8
    assert service.calculate_english_level_score().raw_score == 0.8

    # Test case where the candidate_factory's English is two levels below the requirement
    job_instance = job_posting_factory(english_level=EnglishLevel.INTERMEDIATE)
    candidate_instance = candidate_factory(english_level=EnglishLevel.BASIC)
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    # Assuming a coefficient of 0.2, the score should be 0.6
    assert service.calculate_english_level_score().raw_score == 0.6


@pytest.mark.django_db
def test_location_score_ukraine_region(job_posting_factory, candidate_factory):
    job_instance = job_posting_factory(accept_region=JobPosting.AcceptRegion.UKRAINE)
    candidate_instance = candidate_factory(country_code='UKR', can_relocate=False)
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    assert service.calculate_location_score().raw_score == 1


@pytest.mark.django_db
def test_location_score_europe_region(job_posting_factory, candidate_factory):
    job_instance = job_posting_factory(accept_region=JobPosting.AcceptRegion.EUROPE)
    candidate_instance = candidate_factory(country_code='UKR', can_relocate=False)
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    assert service.calculate_location_score().raw_score == 1


@pytest.mark.django_db
def test_location_score_europe_only_region(job_posting_factory, candidate_factory):
    job_instance = job_posting_factory(accept_region=JobPosting.AcceptRegion.EUROPE_ONLY)
    candidate_instance = candidate_factory(
        country_code='DEU',
        can_relocate=False
    )  # Assuming 'DEU' is a European country code
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    assert service.calculate_location_score().raw_score == 1


@pytest.mark.django_db
def test_location_score_willing_to_relocate(job_posting_factory, candidate_factory):
    job_instance = job_posting_factory(accept_region=JobPosting.AcceptRegion.EUROPE_ONLY)
    candidate_instance = candidate_factory(country_code='USA', can_relocate=True)
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    assert service.calculate_location_score().raw_score == 0.5


@pytest.mark.django_db
def test_location_score_not_willing_to_relocate(job_posting_factory, candidate_factory):
    job_instance = job_posting_factory(accept_region=JobPosting.AcceptRegion.EUROPE_ONLY)
    candidate_instance = candidate_factory(country_code='USA', can_relocate=False)
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    assert service.calculate_location_score().raw_score == 0


@pytest.mark.django_db
def test_location_score_no_match_and_not_willing_to_relocate(job_posting_factory, candidate_factory):
    job_instance = job_posting_factory(accept_region=JobPosting.AcceptRegion.UKRAINE)
    candidate_instance = candidate_factory(country_code='USA', can_relocate=False)
    service = ThreadScoringService(candidate=candidate_instance, job=job_instance)
    assert service.calculate_location_score().raw_score == 0


@pytest.mark.django_db
def test_calculate_experience_score(candidate_factory, job_posting_factory):
    # Create job postings with different experience requirements
    job_posting_no_exp = job_posting_factory(exp_years=JobPosting.Experience.ZERO)
    job_posting_one_year = job_posting_factory(exp_years=JobPosting.Experience.ONE)
    job_posting_three_years = job_posting_factory(exp_years=JobPosting.Experience.THREE)

    # Create candidates with varying years of experience
    candidate_no_exp = candidate_factory(experience_years=0)
    candidate_one_year = candidate_factory(experience_years=1)
    candidate_three_years = candidate_factory(experience_years=3)
    candidate_five_years = candidate_factory(experience_years=5)

    # Test that a candidate with the same or more experience than the job requires gets a full score
    service = ThreadScoringService(candidate=candidate_no_exp, job=job_posting_no_exp)
    assert service.calculate_experience_score().raw_score == 1

    service = ThreadScoringService(candidate=candidate_one_year, job=job_posting_one_year)
    assert service.calculate_experience_score().raw_score == 1

    service = ThreadScoringService(candidate=candidate_three_years, job=job_posting_three_years)
    assert service.calculate_experience_score().raw_score == 1

    service = ThreadScoringService(candidate=candidate_five_years, job=job_posting_three_years)
    assert service.calculate_experience_score().raw_score == 1

    # Test that a candidate with less experience than the job requires does not get a full score
    service = ThreadScoringService(candidate=candidate_no_exp, job=job_posting_one_year)
    assert service.calculate_experience_score().raw_score < 1

    service = ThreadScoringService(candidate=candidate_one_year, job=job_posting_three_years)
    assert service.calculate_experience_score().raw_score < 1


@pytest.mark.django_db
def test_calculate_primary_keyword_score(candidate_factory, job_posting_factory):
    weights = ScoringWeights(primary_keyword=2)  # Assuming a weight of 1 for simplicity
    primary_keyword = "Python"

    # Candidate and job posting with matching primary keywords
    candidate = candidate_factory(primary_keyword=primary_keyword)
    job_posting = job_posting_factory(primary_keyword=primary_keyword)
    service = ThreadScoringService(candidate=candidate, job=job_posting, weights=weights)

    calculated_score = service.calculate_primary_keyword_score()
    assert calculated_score.raw_score == 1.0
    assert calculated_score.weighted_score == 1.0 * weights.primary_keyword

    # Candidate and job posting with non-matching primary keywords
    job_posting = job_posting_factory(primary_keyword="Java")
    service = ThreadScoringService(candidate=candidate, job=job_posting, weights=weights)

    calculated_score = service.calculate_primary_keyword_score()
    assert calculated_score.raw_score == 0.0
    assert calculated_score.weighted_score == 0.0


@pytest.mark.django_db
def test_calculate_secondary_keyword_score(candidate_factory, job_posting_factory):
    weights = ScoringWeights(secondary_keyword=0.5)  # Assuming a weight of 0.5 for simplicity
    secondary_keyword = "Django"

    # Candidate and job posting with matching secondary keywords
    candidate = candidate_factory(secondary_keyword=secondary_keyword)
    job_posting = job_posting_factory(secondary_keyword=secondary_keyword)
    service = ThreadScoringService(candidate=candidate, job=job_posting, weights=weights)

    calculated_score = service.calculate_secondary_keyword_score()
    assert calculated_score.raw_score == 1.0
    assert calculated_score.weighted_score == 1.0 * weights.secondary_keyword

    # Candidate and job posting with non-matching secondary keywords
    job_posting = job_posting_factory(secondary_keyword="Flask")
    service = ThreadScoringService(candidate=candidate, job=job_posting, weights=weights)

    calculated_score = service.calculate_secondary_keyword_score()
    assert calculated_score.raw_score == 0.0
    assert calculated_score.weighted_score == 0.0


@pytest.mark.django_db
def test_calculate_domain_zone_score(candidate_factory, job_posting_factory):
    weights = ScoringWeights(domain_zone=0.5)  # Assuming a weight of 0.5 for simplicity
    domain_zone = "Gambling, Adult"

    # Candidate and job posting with matching domain zone
    candidate = candidate_factory(domain_zones=domain_zone)
    job_posting = job_posting_factory(domain="Adult")
    service = ThreadScoringService(candidate=candidate, job=job_posting, weights=weights)

    calculated_score = service.calculate_domain_zone_score()
    assert calculated_score.raw_score == 1.0
    assert calculated_score.weighted_score == 1.0 * weights.domain_zone

    # Candidate and job posting with non-matching domain zone
    job_posting = job_posting_factory(domain="Gamedev")
    service = ThreadScoringService(candidate=candidate, job=job_posting, weights=weights)

    calculated_score = service.calculate_domain_zone_score()
    assert calculated_score.raw_score == 0.0
    assert calculated_score.weighted_score == 0.0


@pytest.mark.django_db
def test_calculate_company_type_penalty(candidate_factory, job_posting_factory):
    weights = ScoringWeights(uninterested_company_type=0.5)  # Assuming a weight of 0.5 for simplicity
    uninterested_company_type = "startup"

    # Candidate and job posting with matching uninterested company type
    candidate = candidate_factory(uninterested_company_types=uninterested_company_type)
    job_posting = job_posting_factory(company_type="startup")
    service = ThreadScoringService(candidate=candidate, job=job_posting, weights=weights)

    calculated_score = service.calculate_company_type_penalty()
    assert calculated_score.raw_score == -1.0
    assert calculated_score.weighted_score == -1.0 * weights.uninterested_company_type

    # Candidate and job posting with non-matching uninterested company type
    job_posting = job_posting_factory(company_type="corporation")
    service = ThreadScoringService(candidate=candidate, job=job_posting, weights=weights)

    calculated_score = service.calculate_company_type_penalty()
    assert calculated_score.raw_score == 0.0
    assert calculated_score.weighted_score == 0.0


@pytest.mark.django_db
def test_salary_score_within_range(job_posting_factory, candidate_factory):
    # Test when the candidate's expected salary is within the job's salary range
    job_posting = job_posting_factory(salary_min=5000, salary_max=8000)
    candidate_instance = candidate_factory(salary_min=6000)
    service = ThreadScoringService(candidate=candidate_instance, job=job_posting)

    # The candidate's expected salary of 6000 should be within the job's range [5000, 8000],
    # so they should get a full score of 1.0.
    assert service.calculate_salary_score().raw_score == 1.0


@pytest.mark.django_db
def test_salary_score_below_range(job_posting_factory, candidate_factory):
    # Test when the candidate's expected salary is below the job's salary range
    job_posting = job_posting_factory(salary_min=5000, salary_max=8000)
    candidate_instance = candidate_factory(salary_min=3000)
    service = ThreadScoringService(candidate=candidate_instance, job=job_posting)

    # The candidate's expected salary of 4000 is below the job's range [5000, 8000].
    assert service.calculate_salary_score().raw_score == 0.8


@pytest.mark.django_db
def test_salary_score_above_range(job_posting_factory, candidate_factory):
    # Test when the candidate's expected salary is above the job's salary range
    job_posting = job_posting_factory(salary_min=5000, salary_max=8000)
    candidate_instance = candidate_factory(salary_min=9000)
    service = ThreadScoringService(candidate=candidate_instance, job=job_posting)

    # The candidate's expected salary of 9000 is above the job's range [5000, 8000].
    # The score should be reduced based on the percentage over the max salary.
    assert service.calculate_salary_score().raw_score < 1.0


@pytest.mark.django_db
def test_salary_score_no_salary_range(job_posting_factory, candidate_factory):
    # Test when the job posting has no salary range defined
    job_posting = job_posting_factory(salary_min=None, salary_max=None)
    candidate_instance = candidate_factory(salary_min=6000)
    service = ThreadScoringService(candidate=candidate_instance, job=job_posting)

    # When the job posting has no salary range, a default score of 0.8 should be given.
    assert service.calculate_salary_score().raw_score == 0.8


@pytest.mark.django_db
def test_skills_score_match(job_posting_factory, candidate_factory):
    # Test when the candidate's skills partially match the job requirements
    job_posting = job_posting_factory(long_description=mock_jobposting_long_description)

    candidate_instance = candidate_factory(
        skills_cache="""JavaScript
        React
        HTML / CSS / JavaScript / TypeScript"""
    )
    service = ThreadScoringService(candidate=candidate_instance, job=job_posting)

    # Some required skills are present in the candidate's skills cache,
    # so the skill score should be higher than 0.0
    assert service.calculate_skills_score().raw_score > 0.0


@pytest.mark.django_db
def test_skills_score_no_match(job_posting_factory, candidate_factory):
    # Test when the candidate's skills do not match the job requirements
    job_posting = job_posting_factory(long_description=mock_jobposting_long_description)

    candidate_instance = candidate_factory(
        skills_cache="""Python
    Django"""
        )
    service = ThreadScoringService(candidate=candidate_instance, job=job_posting)

    # None of the required skills are present in the candidate's skills cache,
    # so the skills score should be 0.0.
    assert service.calculate_skills_score().raw_score == 0.0
