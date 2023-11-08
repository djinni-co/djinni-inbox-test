from django.db.models import Q, Case, When, Value, IntegerField, F
from app.sandbox.models import EnglishLevel


english_level_priorities = Case(
        When(candidate__english_level=EnglishLevel.BASIC, then=Value(1)),
        When(candidate__english_level=EnglishLevel.PRE, then=Value(2)),
        When(candidate__english_level=EnglishLevel.INTERMEDIATE, then=Value(3)),
        When(candidate__english_level=EnglishLevel.UPPER, then=Value(4)),
        When(candidate__english_level=EnglishLevel.FLUENT, then=Value(5)),
        default=Value(0),
        output_field=IntegerField(),
)
position_priorities = Case(
    When(candidate__position=F('job__position'), then=Value(1)),
    default=Value(0),
    output_field=IntegerField(),
)
primary_keyword_priorities = Case(
    When(candidate__primary_keyword=F('job__primary_keyword'), then=Value(1)),
    default=Value(0),
    output_field=IntegerField(),
)
secondary_keyword_priorities = Case(
    When(candidate__secondary_keyword=F('job__secondary_keyword'), then=Value(1)),
    default=Value(0),
    output_field=IntegerField(),
)
skills_priorities = Case(
    When(Q(candidate__skills_cache__contains=F("job__extra_keywords")), then=Value(1)),
    default=Value(0),
    output_field=IntegerField(),
)
location_priorities = Case(
    When(candidate__location=F('job__location'), then=Value(1)),
    default=Value(0),
    output_field=IntegerField(),
)
salary_priorities = Case(
    When(candidate__salary_min=F('job__salary_max'), then=Value(1)),
    When(candidate__salary_min__lt=F('job__salary_max'), then=Value(2)),
    When(candidate__salary_min=F('job__salary_min'), then=Value(3)),
    When(candidate__salary_min__lt=F('job__salary_min'), then=Value(4)),
    default=Value(0),
    output_field=IntegerField(),
)
exp_years_priorities = Case(
    When(candidate__experience_years__gte=1, then=Value(1)),
    When(candidate__experience_years__gte=2, then=Value(2)),
    When(candidate__experience_years__gte=3, then=Value(3)),
    When(candidate__experience_years__gte=5, then=Value(4)),
    default=Value(0),
    output_field=IntegerField(),
)
domain_priorities = Case(
    When(Q(candidate__domain_zones__contains=F("job__domain")), then=Value(1)),
    default=Value(0),
    output_field=IntegerField(),
)
company_type_priorities = Case(
    When(~Q(candidate__uninterested_company_types__contains=F("job__company_type")), then=Value(1)),
    default=Value(0),
    output_field=IntegerField(),
)
candidate_archived_priorities = Case(
    When(candidate_archived=False, then=Value(1)),
    default=Value(0),
    output_field=IntegerField(),
)
recruiter_favorite_priorities = Case(
    When(recruiter_favorite=True, then=Value(1)),
    default=Value(0),
    output_field=IntegerField(),
)
