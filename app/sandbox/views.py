from django.http import HttpResponse
from django.db.models import Count, Q
from django.shortcuts import render


from .models import Candidate, JobPosting, Recruiter, MessageThread

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528


def inbox(request) -> HttpResponse:
    recruiter = Recruiter.objects.get(id=RECRUITER_ID)
    threads = MessageThread.objects.filter(recruiter=recruiter).select_related(
        "candidate", "job"
    )
    for thread in threads:
        thread.candidate_suitability = _calculate_candidate_suitability(thread)

    _context = {
        "title": "Djinni - Inbox",
        "recruiter": recruiter,
        "threads": threads,
    }

    return render(request, "inbox/chats.html", _context)


def inbox_thread(request, pk):
    thread = MessageThread.objects.get(id=pk)
    messages = thread.message_set.all().order_by("created")

    candidate_score: float = _calculate_candidate_suitability(thread)

    _context = {
        "pk": pk,
        "title": "Djinni - Inbox",
        "thread": thread,
        "messages": messages,
        "candidate": thread.candidate,
        "candidate_score": candidate_score,
    }

    return render(request, "inbox/thread.html", _context)


def _calculate_candidate_suitability(thread: MessageThread) -> float:
    prog_lang: float = _calcualte_prog_lang_coefficient(thread.candidate, thread.job)
    exp: float = _calculate_experiance_value(
        thread.candidate.experience_years, thread.job.exp_years
    )
    english_level: float = _calculate_english_level_coefficient(
        thread.candidate.english_level, thread.job.english_level
    )
    salary: float = _calculate_salary_coefficient(
        thread.candidate.salary_min, thread.job
    )
    location: float = _calculate_location_coefficient(
        thread.job.location, thread.candidate.location
    )
    # JobPosting model could be updated
    # Recruiter could choose up to 10 different categories and their `weight`
    default_coeff = 1.0
    # coeff times category weight
    return round(
        sum(
            [
                prog_lang * thread.job.primary_keyword_weight or default_coeff,
                exp * thread.job.exp_years_weight or default_coeff,
                salary * thread.job.salary_weight or default_coeff,
                english_level * thread.job.english_level_weight or default_coeff,
                location * thread.job.location_weight or default_coeff,
            ]
        ),
        2,
    )


def _calculate_experiance_value(c_exp: float, required_exp: str) -> float:
    """Experiance coefficint calculation."""
    job_exp_map = {
        "no_exp": 0,
        "1y": 12,
        "2y": 24,
        "3y": 36,
        "5y": 60,
    }

    required_job_experince_in_month = job_exp_map.get(required_exp, 0)
    candidate_experince_in_month = int(c_exp * 12)
    job_and_candidate_exp_gap = (
        required_job_experince_in_month - candidate_experince_in_month
    )
    coeff = 1.0
    if job_and_candidate_exp_gap < 0:
        coeff = round(1.0 + (abs(job_and_candidate_exp_gap) * 0.01), 2)
    elif job_and_candidate_exp_gap > 0:
        coeff = round(1.0 - (job_and_candidate_exp_gap * 0.01), 2)
    elif not required_job_experince_in_month and candidate_experince_in_month:
        coeff = 1.0

    return coeff


def _calcualte_prog_lang_coefficient(candidate: Candidate, job: JobPosting) -> float:
    primary_keyword: bool = job.primary_keyword == candidate.primary_keyword
    secondary_keyword: bool = job.secondary_keyword == candidate.secondary_keyword
 
    if job.secondary_keyword:
        if secondary_keyword:
            return 1.1
        else:
            return 0.9

    return 1.0 if primary_keyword else 0.5


def _calculate_salary_coefficient(candidate: int, job: JobPosting) -> float:
    if candidate not in [job.salary_min, job.salary_max]:
        # means that candidate wants more that vacancy can offer
        return 0.5
    return 1.0


def _calculate_location_coefficient(v_loc: str, c_loc: str) -> float:
    return 1.0 if v_loc == c_loc else 0.5


def _calculate_english_level_coefficient(
    candidate_level: str, vacancy_level: str
) -> float:
    english_level_map = {
        "no_english": 0,
        "basic": 1,
        "pre": 2,
        "intermediate": 3,
        "upper": 4,
        "fluent": 5,
    }
    v_level: int = english_level_map.get(vacancy_level, 0)
    c_level: int = english_level_map.get(candidate_level, 0)
    # if candidate level it bigger that vacancy requires
    # candidate should recieve extra points per level and vice verse
    if c_level > v_level:
        return 1.0 + (c_level - v_level) * 0.1
    elif c_level < v_level:
        return 1.0 - (v_level - c_level) * 0.1
    else:
        return 1.0
