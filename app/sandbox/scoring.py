from datetime import datetime, timezone

from .models import EnglishLevel, JobPosting, Message
from .score_algorithm import ScoreAlgorithm, LogicalRule, SimpleRule, IterableRule

ENGLISH_WEIGTH = {
    EnglishLevel.NONE: 0.2,
    EnglishLevel.BASIC: 0.5,
    EnglishLevel.PRE: 1,
    EnglishLevel.INTERMEDIATE: 1.5,
    EnglishLevel.UPPER: 2,
    EnglishLevel.FLUENT: 2.5
}

EXPERIENCE_WEIGTH = {
    JobPosting.Experience.ZERO: 0,
    JobPosting.Experience.ONE: 1,
    JobPosting.Experience.TWO: 2,
    JobPosting.Experience.THREE: 3,
    JobPosting.Experience.FIVE: 4
}

DATE_WEIGTH = 15


def score_thread(thread):
    scoring = ScoreAlgorithm()

    candidate = thread.candidate
    job = thread.job

    candidate_full_info = ((candidate.moreinfo or '') + ' ' +
                           (candidate.looking_for or '') + ' ' +
                           (candidate.highlights or ''))
    clear_candidate_full_info = clear_text(candidate_full_info.lower())

    clear_job_description = clear_text(job.long_description.lower()).split()
    job_candidate_desc_occurs = set(clear_candidate_full_info.split()).intersection(clear_job_description)

    scoring.add(LogicalRule(score=1,
                            when=(datetime.now(timezone.utc) - thread.last_updated).days < 7
                                 and thread.last_message.sender == Message.Sender.CANDIDATE,
                            description="Increase score if candidate respond within last 7 days"))

    scoring.add(LogicalRule(score=0.2,
                            when=candidate.primary_keyword.lower() in job.primary_keyword.lower(),
                            description='Candidate primary keyword must exist in job primary keyword'))

    scoring.add(IterableRule(score_per_item=0.02,
                             iterable=job_candidate_desc_occurs,
                             description="Occurrences between candidate full info and job description"))

    scoring.add(LogicalRule(score=0.5,
                            when=job.primary_keyword.lower() in clear_candidate_full_info,
                            description='Job primary keyword must exist in candidate full information'))

    scoring.add(SimpleRule(score=closest_date(datetime.now(timezone.utc), thread.last_updated) * DATE_WEIGTH,
                           description=f"Considering thread date"))

    if job.english_level and candidate.english_level:
        scoring.add(LogicalRule(score=ENGLISH_WEIGTH.get(candidate.english_level),
                                when=ENGLISH_WEIGTH.get(candidate.english_level) >= ENGLISH_WEIGTH.get(
                                    job.english_level),
                                description="Add score if candidate English level greater than job required level"))

    if job.location and candidate.location:
        scoring.add(LogicalRule(score=2,
                                when=job.location.lower() == candidate.location.lower(),
                                description='Job location must equal to candidate location'))

    if job.country and candidate.country_code:
        scoring.add(LogicalRule(score=2,
                                when=job.country.lower() == candidate.country_code.lower(),
                                description='Job country must equal to candidate country'))
        scoring.add(LogicalRule(score=0.5,
                                when=(candidate.can_relocate and job.country.lower() != candidate.country_code.lower()),
                                description='Score when candidate can relocate but country is different'))

    if job.secondary_keyword:
        scoring.add(LogicalRule(score=0.2,
                                when=job.secondary_keyword.lower() in clear_candidate_full_info,
                                description='Job secondary keyword must exist in candidate full information'))

    if candidate.experience_years:
        scoring.add(SimpleRule(score=lower_distance(EXPERIENCE_WEIGTH.get(job.exp_years), candidate.experience_years),
                               description="Consider candidate experience"))

    if candidate.secondary_keyword and job.secondary_keyword:
        scoring.add(LogicalRule(score=0.2,
                                when=candidate.secondary_keyword.lower() in job.secondary_keyword.lower(),
                                description='Candidate secondary keyword must exist in job secondary keyword'))

    if candidate.domain_zones:
        domain_zones = clear_text(candidate.domain_zones).lower().split()
        domain_zones_description_occurs = set(domain_zones).intersection(clear_job_description)
        scoring.add(IterableRule(score_per_item=-0.3,
                                 iterable=domain_zones_description_occurs,
                                 description="Decrease score if candidate domain zones occur in description"))

    if candidate.uninterested_company_types:
        uninterested_company_types = clear_text(candidate.uninterested_company_types).lower().split()
        uninterested_company_types_occurs = set(uninterested_company_types).intersection(clear_job_description)
        scoring.add(IterableRule(score_per_item=-0.3,
                                 iterable=uninterested_company_types_occurs,
                                 description="Decrease score if candidate unwanted company types occur in description"))

    candidate_skills = candidate.skills_cache
    if candidate_skills:
        clear_candidate_skills = clear_text(candidate_skills.lower()).split()
        job_candidate_skills_occurs = set(clear_candidate_skills).intersection(clear_job_description)

        scoring.add(IterableRule(score_per_item=0.5,
                                 iterable=job_candidate_skills_occurs,
                                 description="Occurrences between skills and job description"))

        scoring.add(LogicalRule(score=0.2,
                                when=job.primary_keyword.lower() in candidate_skills.lower(),
                                description='Job primary keyword must exist in candidate skills'))

        if job.secondary_keyword:
            scoring.add(LogicalRule(score=0.1,
                                    when=job.secondary_keyword.lower() in candidate_skills.lower(),
                                    description='Job secondary keyword must exist in candidate skills'))

    thread.score = scoring.calculate()
    return thread


def clear_text(text):
    """ Clear text from unwanted characters to be easily analyzed"""
    return text.replace('/', ' ').replace(',', ' ').replace('-', ' ')


def closest_date(date1, date2):
    """ Lower distance between two dates returns higher number"""
    time_difference = date1 - date2
    days_difference = time_difference.days
    return 1.0 / (1.0 + days_difference)


def lower_distance(number1, number2):
    """ Lower distance between two number returns higher number """
    absolute_difference = abs(number1 - number2)
    return 1.0 / (1.0 + absolute_difference)
