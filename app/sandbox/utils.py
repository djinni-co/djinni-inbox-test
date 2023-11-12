from dataclasses import dataclass

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db.models import Case, F, Func, TextField, Value, When, Window
from django.db.models.expressions import RawSQL
from django.db.models.functions import PercentRank
from django.http import HttpRequest

from .forms import ThreadForm
from .models import MessageThread, Recruiter


@dataclass
class ScoringWeight:
    language: float
    salary: float
    experience: float
    skills: float


SCORE_WEIGHTS = ScoringWeight(**settings.SCORING_WEIGHTS)

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528


ENGLISH_LEVELS_EXPRESSION = Case(
When(candidate__english_level='basic', then=Value(1)),
       When(candidate__english_level='pre', then=Value(2)),
       When(candidate__english_level='intermediate', then=Value(3)),
       When(candidate__english_level='upper', then=Value(4)),
       When(candidate__english_level='fluent', then=Value(5)),
       default=Value(0)
)


def get_score_queryset(recruiter: Recruiter):
    return (MessageThread.objects.filter(recruiter=recruiter).select_related(
        'candidate', 'job'
    ).annotate(english_level_int=ENGLISH_LEVELS_EXPRESSION
    ).annotate(
        required_skills=Func(F('job__extra_keywords'), Value('\n'), function='regexp_split_to_array',
                             output_field=ArrayField(base_field=TextField()))
    ).annotate(
        skills=Func(F('candidate__skills_cache'), Value('\n'), function='regexp_split_to_array',
                    output_field=ArrayField(base_field=TextField()))
    ).annotate(
        salary_score=Window(expression=PercentRank(), partition_by='job', order_by=F('candidate__salary_min').asc())
    ).annotate(
        experience_score=Window(expression=PercentRank(), partition_by='job',
                                order_by=F('candidate__experience_years').asc())
    ).annotate(
        english_level_score=Window(PercentRank(), partition_by='job', order_by=F('english_level_int').asc())
    ).annotate(
        skills_match_score=Window(
            expression=PercentRank(),
            partition_by='job',
            order_by=RawSQL(
                "SELECT COUNT(*) FROM (SELECT regexp_split_to_table(extra_keywords, E'\n') INTERSECT SELECT regexp_split_to_table(skills_cache, E'\n'))",
                (),
            ).asc())
    ).annotate(
        total_score=F('salary_score') * SCORE_WEIGHTS.salary
                    + F('experience_score') * SCORE_WEIGHTS.experience
                    + F('english_level_score') * SCORE_WEIGHTS.language
                    + F('skills_match_score') * SCORE_WEIGHTS.skills
    ))


def get_context(request: HttpRequest):
    recruiter = Recruiter.objects.get(id=RECRUITER_ID)
    thread_form = ThreadForm(request.POST, recruiter=recruiter)
    if 'submit' in thread_form.data and thread_form.is_valid():
        threads = get_score_queryset(recruiter)
        for value in thread_form.cleaned_data:
            if value == 'english_level':
                threads = threads.filter(english_level_int__gte=thread_form.cleaned_data['english_level'])
            elif value == 'job':
                threads = threads.filter(job=thread_form.cleaned_data['job'])
        threads = threads.order_by('-total_score')
    else:
        thread_form = ThreadForm(recruiter=recruiter)
        threads = MessageThread.objects.filter(recruiter=recruiter).select_related(
            'candidate', 'job'
         ).order_by('created')
    return {
            'title': 'Djinni - Inbox',
            'recruiter': recruiter,
            'threads': threads,
            'thread_form': thread_form
    }
