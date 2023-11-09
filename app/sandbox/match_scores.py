from .models import Candidate, JobPosting


def calculate_match_score(applicant, job_posting):
    # Define weights for match criteria
    weight_relevance = 1.0
    weight_domain = 1.0
    weight_experience = 1.0
    weight_english_level = 1.0
    weight_salary_level = 1.0

    # Calculate the match score based on criteria
    relevance_score = calculate_job_relevance_score(applicant, job_posting)
    domain_score = calculate_domain_relevance_score(applicant, job_posting)
    experience_score = calculate_experience_score(applicant, job_posting)
    english_level_score = calculate_english_level_score(applicant, job_posting)
    salary_score = calculate_salary_score(applicant, job_posting)

    # Calculate the overall match score
    total_weight = (
        weight_relevance + weight_domain + weight_experience + weight_english_level + weight_salary_level
    )
    match_score = (
        (weight_relevance * relevance_score +
         weight_domain * domain_score +
         weight_experience * experience_score +
         weight_english_level * english_level_score +
         weight_salary_level * salary_score)
        / total_weight
    )

    return match_score


def calculate_job_relevance_score(applicant: Candidate, job_posting: JobPosting):
    if applicant.primary_keyword.lower() == job_posting.primary_keyword.lower():
        return 1
    else:
        return -1


def calculate_domain_relevance_score(applicant: Candidate, job_posting: JobPosting):
    not_interested = applicant.domain_zones.lower().split(", ") if applicant.domain_zones else ""
    job_domain = job_posting.domain.lower() if job_posting.domain else ""

    if job_domain not in not_interested:
        return 1
    else:
        return -1


def calculate_experience_score(applicant: Candidate, job_posting: JobPosting):
    experience_levels = {
        "no_exp": 0,
        "1y": 1,
        "2y": 2,
        "3y": 3,
        "5y": 4,
    }
    applicant_experience = applicant.experience_years
    job_experience = experience_levels.get(job_posting.exp_years, 0)

    experience_difference = applicant_experience - job_experience

    # Here option when we search candidate with the closest experience level
    return 1 - abs(0.1 * experience_difference)

    # Here option where we find the most experienced one among all
    # return 0.1 * experience_difference


def calculate_english_level_score(applicant: Candidate, job_posting: JobPosting):
    english_levels = {
        "no_english": 0,
        "basic": 1,
        "pre": 2,
        "intermediate": 3,
        "upper": 4,
        "fluent": 5,
    }
    applicant_english_level = english_levels.get(applicant.english_level, 0)
    job_english_level = english_levels.get(job_posting.english_level, 0)

    experience_difference = applicant_english_level - job_english_level
    return 0.1 * experience_difference


def calculate_salary_score(applicant: Candidate, job_posting: JobPosting):
    candidate_min_salary = applicant.salary_min
    job_min_salary = job_posting.salary_min
    job_max_salary = job_posting.salary_max

    # Option when we are searching for the closest salary range
    median_job_salary = (job_max_salary + job_min_salary) / 2
    salary_difference = candidate_min_salary - median_job_salary
    return 0.1 * (salary_difference / 1000)

    # if job_max_salary >= candidate_min_salary >= job_min_salary:
    #     return 1
    # return -1
