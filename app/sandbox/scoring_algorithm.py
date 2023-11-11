import re

from .models import MessageThread, JobPosting, Candidate, EnglishLevel

ALGORITHMS = []

def register_algorithm(fn):
    ALGORITHMS.append(fn)
    return fn


def calc_score(thread: MessageThread):
    job, candidate = thread.job, thread.candidate
    return round(sum(fn(job, candidate) for fn in ALGORITHMS), 1)


FIB_SEQ = (1, 2, 3, 5, 8, 13)
LEN_FIB_SEQ = len(FIB_SEQ)
MAX_FIB_SEQ_INDEX = LEN_FIB_SEQ - 1
ENGLISH_TO_INDEX = {
    EnglishLevel.NONE: 0,
    EnglishLevel.BASIC: 1,
    EnglishLevel.PRE: 2,
    EnglishLevel.INTERMEDIATE: 3,
    EnglishLevel.UPPER: 4,
    EnglishLevel.FLUENT: 5,
}
EXPERIENCE_TO_YEARS = {
    JobPosting.Experience.ZERO: 0,
    JobPosting.Experience.ONE: 1,
    JobPosting.Experience.TWO: 2,
    JobPosting.Experience.THREE: 3,
    JobPosting.Experience.FIVE: 5,
}
RE_NON_WORD = re.compile(r'[^a-zA-Z0-9 ]+')
RE_WHITESPACE = re.compile(r'\s+')


def clean_text(text):
    if not text:
        return ''

    return RE_WHITESPACE.sub(
        ' ',  # it's important to leave space firstly, ex: "Junior/Middle" or "Lviv,Kyiv" ¯\_(ツ)_/¯
        RE_NON_WORD.sub(' ', text.lower())
    )


@register_algorithm
def english_level(job: JobPosting, candidate: Candidate):
    """
    Considers score from English level

    Subtracts score if candidate has English level below required by job
    Adds score if candidate has English level same or above required by job

    Example #1: Required by job is Pre-Intermediate, but candidate has Fluent level
    Difference equals to 3, but score will be 1.6 = 8/5, where 5 is fourth fibonacci element (starting from second 1)

    Example #2: Required by job is Upper-Intermediate, but candidate has Basic level
    Difference equals to -3, but score will be -6 = -2*3, where 3 is third fibonacci element (starting from second 1)
    """
    if not job.english_level:
        return 0

    diff = ENGLISH_TO_INDEX[candidate.english_level or EnglishLevel.NONE] - ENGLISH_TO_INDEX[job.english_level]
    if diff >= 0:
        return 8 / FIB_SEQ[diff]
    else:
        return -2 * FIB_SEQ[-diff - 1]


@register_algorithm
def experience(job: JobPosting, candidate: Candidate):
    """
    Considers score from years of experience

    Subtracts score if candidate has fewer years of experience, than required by job
    Adds score if candidate has years of experience equals or more than required by job

    Example: Job requires 1 year of experience, but candidate has 2 years
    Difference equals to 1, but score will be 10 = 5/2, where 2 is second fibonacci element (starting from second 1)

    Example #2: Job requires 3 years of experience, but candidate has 1 year
    Difference equals to -2, but score will be -3 = -1.5*2, where 2 is second fibonacci element (starting from second 1)
    """
    if not job.exp_years:
        return 0

    diff = int(candidate.experience_years - EXPERIENCE_TO_YEARS[job.exp_years])
    if diff >= 0:
        diff_index = min(diff, MAX_FIB_SEQ_INDEX)
        return 5 / FIB_SEQ[diff_index]
    else:
        return -1.5 * FIB_SEQ[-diff - 1]


@register_algorithm
def position(job: JobPosting, candidate: Candidate):
    """ Add scores if candidate has the same position as required by job """

    if clean_text(candidate.position) == clean_text(job.position):
        return 5
    else:
        return 0


@register_algorithm
def keyword(job: JobPosting, candidate: Candidate):
    """
    Add scores if candidate has the same primary keyword as required by job

    Extra scores if secondary keyword also matches
    """
    job_primary_keyword = clean_text(job.primary_keyword)
    if not job_primary_keyword:
        return 0

    candidate_primary_keyword = clean_text(candidate.primary_keyword)
    if not candidate_primary_keyword:
        return -1

    if candidate_primary_keyword != job_primary_keyword:
        return -2

    job_secondary_keyword = clean_text(job.secondary_keyword)
    if not job_secondary_keyword:
        return 5

    candidate_secondary_keyword = clean_text(candidate.secondary_keyword)
    if not candidate_secondary_keyword:
        return 5

    if candidate_secondary_keyword == job_secondary_keyword:
        return 8

    return 3


@register_algorithm
def salary(job: JobPosting, candidate: Candidate):
    """
    Considers score from salary expectations

    Subtracts score if candidate has bigger minimum salary expectations, than maximum salary expectations in job
    Adds score if candidate has minimum salary expectations between minimum and maximum salary expectations in job
    Subtracts score if candidate has smaller minimum salary expectations, than minimum salary expectations in job
    """

    diff_with_max = round((candidate.salary_min - job.salary_max) / 250)
    if diff_with_max >= 0:
        diff_index = min(diff_with_max, MAX_FIB_SEQ_INDEX)
        return -2 * FIB_SEQ[diff_index]

    min_max_part = (job.salary_max - job.salary_min) / LEN_FIB_SEQ
    diff_with_min = round((candidate.salary_min - job.salary_min) / min_max_part)
    if diff_with_min >= 0:
        return 8 / FIB_SEQ[diff_with_min]
    else:
        diff_index = min(diff_with_min, MAX_FIB_SEQ_INDEX)
        return -1 * FIB_SEQ[diff_index]


@register_algorithm
def description(job: JobPosting, candidate: Candidate):
    not_interested_list = clean_text(f'{candidate.domain_zones} {candidate.uninterested_company_types}').split()
    job_description = clean_text(job.long_description)
    job_company_type = clean_text(job.company_type)

    for not_interested in not_interested_list:
        if not_interested in job_description:
            return -13

    for not_interested in not_interested_list:
        if not_interested in job_company_type:
            return -8

    skills_list = clean_text(candidate.skills_cache).split()
    scores = 0
    for skill in skills_list:
        if skill in job_description:
            scores += 1

    return scores


@register_algorithm
def location(job: JobPosting, candidate: Candidate):
    if job.is_ukraine_only and candidate.country_code != 'UKR':
        return -13

    if candidate.can_relocate and job.relocate_type != JobPosting.RelocateType.NO_RELOCATE:
        if job.relocate_type == JobPosting.RelocateType.CANDIDATE_PAID:
            return 13
        elif job.relocate_type == JobPosting.RelocateType.COMPANY_PAID:
            return 8

    job_location = clean_text(job.location)
    if not job_location:
        return 13

    candidate_countries = clean_text(f'{candidate.location} {candidate.get_country_code_display()}').split()
    if not candidate_countries:
        return 3

    for country in candidate_countries:
        if country not in job_location:
            continue

        candidate_cities = clean_text(f'{candidate.city} {candidate.get_city_display()}').strip()
        for city in candidate_cities:
            if city in job_location:
                return 13

        return 8

    return 5
