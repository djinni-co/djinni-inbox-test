import re

import pycountry
from django_jinja import library

from typing import Type
from django.db.models.query import QuerySet
from sandbox.models import Candidate, MessageThread, Message, Recruiter, JobPosting, COUNTRY_CHOICES

from sandbox.infrastructure.traits_levels_ordered import english_levels_ordered, experience_levels_ordered

import regex
from regex import *
from re import *


def check_interested(thread: MessageThread)-> bool:
    job = thread.job
    candidate = thread.candidate
    candidate_uniterested_in = candidate.uninterested_company_types
    if candidate_uniterested_in:
        for company_type in candidate_uniterested_in.split():
            if re.search(company_type, job.company_type, IGNORECASE):
                return False
    return True

def check_cover_letter_availability_if_needed(thread: MessageThread)-> bool:
    job = thread.job

    if job.requires_cover_letter:
        thread_messages = Message.objects.filter(thread=thread)
        cover_letter_re = regex.compile("(?:(\p{L}{1,45})+[^\p{L}]+){35,}")
        cover_letter_availability = None
        for message in thread_messages:
            body = message.body if message.body else ""
            if cover_letter_re.search(body):
                cover_letter_availability = True
                break
        cover_letter_availability = False

        return cover_letter_availability

    else: return True

def contains_remote(remote_type_str: str)-> bool:
    return bool(re.search("remote", remote_type_str, IGNORECASE))

def check_location_appropriate(thread: MessageThread)-> bool:
    candidate = thread.candidate
    job = thread.job

    if candidate.can_relocate:
        return True

    if contains_remote(candidate.employment) and contains_remote(job.remote_type):
        if job.is_ukraine_only:
            if candidate.country_code == pycountry.countries.search_fuzzy("Ukraine")[0].alpha_3:
                return True

        else: return True

    else:
        if job.location:
            if candidate.city:
                try:
                    if re.search(candidate.city, job.location, IGNORECASE):
                        return True
                except Exception:
                    return True
        else: return True

    return False


def check_employment_options_appropriate(thread: MessageThread)->bool:
    candidate = thread.candidate
    candidate_employment = candidate.employment
    job = thread.job

    parttime_ok = None
    remote_ok = None

    if job.is_parttime:
        parttime_ok = re.search("parttime", candidate_employment, IGNORECASE)

    else: parttime_ok = True

    remote_pattern = "remote"
    if contains_remote(candidate_employment):
        remote_ok = contains_remote(job.remote_type)

    elif contains_remote(job.remote_type):
        remote_ok = contains_remote(candidate_employment)

    else: remote_ok = True

    return parttime_ok and remote_ok


def check_experience_appropriate(thread: MessageThread)-> bool:
    candidate = thread.candidate
    job = thread.job
    return candidate.experience_years >= experience_levels_ordered[job.exp_years]

def check_salary_appropriate(thread: MessageThread)-> bool:
    candidate = thread.candidate
    job = thread.job
    return candidate.salary_min <= job.salary_max

def check_english_appropriate(thread: MessageThread)-> bool:
    candidate = thread.candidate
    job = thread.job
    return english_levels_ordered.index(candidate.english_level) >= english_levels_ordered.index(job.english_level)

def sort_threads_by_score(threads: list[Type[MessageThread]])-> list[Type[MessageThread]]:

    final_score_sorted_threads = []
    if threads:
        experience_sorted_threads = sorted(threads, key=lambda  thd: thd.candidate.experience_years)
        salary_sorted_threads = sorted(threads, key=lambda thd: thd.candidate.salary_min, reverse=True)
        english_level_sorted_threads = sorted(threads, key=lambda thd: english_levels_ordered.index(thd.candidate.english_level))

        final_score_sorted_threads =\
            sorted(
                threads, key=lambda thd:
                (experience_sorted_threads.index(thd) +
                 salary_sorted_threads.index(thd) +
                 english_level_sorted_threads.index(thd)), reverse=True)

    return final_score_sorted_threads

class JobThreadsScored:
    def __init__(self, threads: QuerySet[Type[MessageThread]]):
        self.privileged = []
        self.fully_matched = []
        self.particularly_matched = []
        self.irrelevant = []
        for thread in threads:
            if thread.recruiter_favorite: #TODO: consider candidate_favourite check
                self.privileged.append(thread)

            elif thread.notified_notinterested or\
                    thread.candidate_archived \
                    or not check_location_appropriate(thread)\
                    or not check_employment_options_appropriate(thread)\
                    or not check_cover_letter_availability_if_needed(thread)\
                    or not check_interested(thread):
                self.irrelevant.append(thread)

            elif not check_experience_appropriate(thread) or not\
                    check_english_appropriate(thread) or not\
                    check_salary_appropriate(thread):
                self.particularly_matched.append(thread)

            else:
                self.fully_matched.append(thread)

        self.fully_matched_score_sorted = sort_threads_by_score(self.fully_matched)
        self.particularly_matched_sorted = sort_threads_by_score(self.particularly_matched)

        self.scored = self.privileged + self.fully_matched_score_sorted + self.particularly_matched_sorted + self.irrelevant

def shuffled_by_jobs_and_score_threads_list(*jobs_threads_scored: list[Type[JobThreadsScored]],
                                            no_job_threads: list[Type[MessageThread]])\
        -> list[Type[MessageThread]]:

    result = []
    for item in jobs_threads_scored:
        result.extend(item.privileged)

    for item in jobs_threads_scored:
        result.extend(item.fully_matched_score_sorted)

    for item in jobs_threads_scored:
        result.extend(item.particularly_matched_sorted)

    result.extend(no_job_threads)

    for item in jobs_threads_scored:
        result.extend(item.irrelevant)

    return result

@library.filter("sort_shuffle_threads_by_score_and_by_job_filter")
def sort_shuffle_threads_by_score_and_by_job_filter(threads: QuerySet[Type[MessageThread]])\
        -> QuerySet[Type[MessageThread]]:
    recruiter: Recruiter = threads[0].recruiter

    jobs_threads_scored = []

    jobs: QuerySet[JobPosting] = JobPosting.objects.filter(recruiter=recruiter)
    for job in jobs:
        job_threads = MessageThread.objects.filter(job=job)
        job_threads_scored = JobThreadsScored(job_threads)
        jobs_threads_scored.append(job_threads_scored)

    no_job_threads = threads.filter(job=None)

    shuffled_jobs_threads = shuffled_by_jobs_and_score_threads_list(*jobs_threads_scored, no_job_threads=no_job_threads)

    return shuffled_jobs_threads




