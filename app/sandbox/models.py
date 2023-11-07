import enum
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Q, Case, When, Value, FloatField, F, ExpressionWrapper, DateTimeField, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.db.models.functions import Abs
from .utils import Epoch
from django.utils import timezone

import pycountry

COUNTRY_CHOICES: list[tuple[str, str]] = sorted(
    ((c.alpha_3, c.name) for c in pycountry.countries),
    key=lambda c: c[1],
)


class CustomManager(models.Manager):
    def get_ordered_by_best_match(self, job: "JobPosting"):
        english_level_choices = list(EnglishLevel)
        job_post_eng_idx = english_level_choices.index(job.english_level)

        position_search_vector = SearchVector('candidate__position', weight='D', config='english')
        position_search_query = SearchQuery(job.position, search_type='phrase')

        secondary_keyword_search_vector = SearchVector('candidate__secondary_keyword', weight='B', config='english')
        secondary_keyword_search_query = SearchQuery(job.secondary_keyword)

        primary_keyword_search_vector = SearchVector('candidate__primary_keyword', weight='A', config='english') + \
                                        SearchVector('candidate__skills_cache',  weight='D', config='english')

        primary_keyword_search_query = SearchQuery(job.primary_keyword)

        domain_search_vector = SearchVector('candidate__domain_zones', weight='B', config='english')
        domain_search_query = SearchQuery(job.domain)

        return self.filter(job=job).select_related('candidate', 'job').annotate(
            # Let's convert job postings exp years into float, so it would be easier to search best match
            job_post_exp_converted_to_float=Case(
                When(job__exp_years=JobPosting.Experience.ZERO, then=Value(0.0)),
                When(job__exp_years=JobPosting.Experience.ONE, then=Value(1.0)),
                When(job__exp_years=JobPosting.Experience.TWO, then=Value(2.0)),
                When(job__exp_years=JobPosting.Experience.THREE, then=Value(3.0)),
                When(job__exp_years=JobPosting.Experience.FIVE, then=Value(5.0)),
            ),
            candidate_english_level_converted_to_int=Case(
                When(candidate__english_level=EnglishLevel.NONE, then=Value(0)),
                When(candidate__english_level=EnglishLevel.BASIC, then=Value(1)),
                When(candidate__english_level=EnglishLevel.PRE, then=Value(2)),
                When(candidate__english_level=EnglishLevel.INTERMEDIATE, then=Value(3)),
                When(candidate__english_level=EnglishLevel.UPPER, then=Value(4)),
                When(candidate__english_level=EnglishLevel.FLUENT, then=Value(5)),
            ),
            salary_match=Case(
                    When(candidate__salary_min__range=(job.salary_min, job.salary_max), then=Value(1.0)),
                    default=Value(0.0),
                    output_field=FloatField(),
            ),
            english_level_match=Case(
                When(candidate_english_level_converted_to_int=job_post_eng_idx, then=Value(1.0)),
                When(candidate_english_level_converted_to_int__gt=job_post_eng_idx, then=Value(1.5)),
                default=Value(0.0),
                output_field=FloatField(),
            ),
            exp_match=Case(
                When(candidate__experience_years=F('job_post_exp_converted_to_float'), then=Value(1.0)),
                When(candidate__experience_years__gt=F('job_post_exp_converted_to_float'), then=Value(1.5)),
                default=Value(0.0),
                output_field=FloatField(),
            ),
            location_match=Case(
                When(candidate__location=job.location, then=Value(0.5)),
                default=Value(0.0),
                output_field=FloatField(),
            ),
            position_match=SearchRank(position_search_vector, position_search_query),
            secondary_keyword_match=Coalesce(
                SearchRank(secondary_keyword_search_vector, secondary_keyword_search_query), Value(0.0)),
            primary_keyword_match=Coalesce(
                SearchRank(primary_keyword_search_vector, primary_keyword_search_query), Value(0.0)),
            domain_match=Coalesce(SearchRank(domain_search_vector, domain_search_query), Value(0.0)),

            score=F("salary_match") + F("english_level_match") + F("exp_match") + F("position_match") +
                  F('secondary_keyword_match') + F('primary_keyword_match') + F('domain_match') + F('location_match')
        ).order_by('-score')

    def get_ordered_by_newest_message(self, job: "JobPosting"):
        current_time = timezone.now()

        subquery = Message.objects.filter(
            thread=OuterRef('pk'),
        ).annotate(
            closest_created_at=Abs(Epoch(ExpressionWrapper(
                current_time - F('created'),
                output_field=DateTimeField()
            )))

        ).order_by('closest_created_at')

        return self.filter(job=job).annotate(
            closest_message=Subquery(subquery.values('closest_created_at')[:1])
        ).order_by('closest_message')


class LegacyUACity(models.TextChoices):
    """used in jobs/candidate"""
    KYIV = "Київ", _("Kyiv")
    VINNYTSIA = "Вінниця", _("Vinnytsia")
    DNIPRO = "Дніпро", _("Dnipro")
    FRANKIVSK = "Івано-Франківськ", _("Ivano-Frankivsk")
    ZHYTOMYR = "Житомир", _("Zhytomyr")
    ZAPORIZHZHIA = "Запоріжжя", _("Zaporizhzhia")
    LVIV = "Львів", _("Lviv")
    MYKOLAIV = "Миколаїв", _("Mykolaiv")
    ODESA = "Одеса", _("Odesa")
    TERNOPIL = "Тернопіль", _("Ternopil")
    KHARKIV = "Харків", _("Kharkiv")
    KHMELNYTSKYI = "Хмельницький", _("Khmelnytskyi")
    CHERKASY = "Черкаси", _("Cherkasy")
    CHERNIHIV = "Чернігів", _("Chernihiv")
    CHERNIVTSI = "Чернівці", _("Chernivtsi")
    UZHHOROD = "Ужгород", _("Uzhhorod")

class EnglishLevel(models.TextChoices):
    NONE = ("no_english", "No English")
    BASIC = ("basic", "Beginner/Elementary")
    PRE = ("pre", "Pre-Intermediate")
    INTERMEDIATE = ("intermediate", "Intermediate")
    UPPER = ("upper", "Upper-Intermediate")
    FLUENT = ("fluent", "Advanced/Fluent")

class Candidate(models.Model):
    USERTYPE = "candidate"

    class EmploymentOption(models.TextChoices):
        FULLTIME = 'fulltime', _('Office')
        PARTTIME = 'parttime', _('Part-time')
        REMOTE = 'remote', _('Remote work')
        FREELANCE = 'freelance', _('candidate.freelance_one_time_projects')
        RELOCATE = 'relocate', _('Relocate to another country')
        MOVE = 'move', _('candidate.profile.move_to_other_city')

    name = models.CharField(max_length=255, blank=True, default="")
    email = models.EmailField(blank=False, db_index=True, unique=True)
    picture_url = models.CharField(max_length=255, blank=True, default='', null=True)

    # Profile fields
    position = models.CharField(max_length=255, blank=False, default="")
    primary_keyword = models.CharField(
        max_length=80,
        db_index=True,
        blank=True,
        default="",
    )
    secondary_keyword = models.CharField(
        max_length=80, db_index=True, blank=True, default="", null=True
    )
    salary_min = models.IntegerField(blank=True, default=0, db_index=True)
    employment = models.CharField(max_length=80, blank=False, default="fulltime remote")
    experience_years = models.FloatField(blank=True, default=0.0)
    english_level = models.CharField(
        max_length=80, blank=True, default="", choices=EnglishLevel.choices
    )
    skills_cache = models.TextField(blank=True, default="")
    location = models.CharField(max_length=255, blank=True, default="", null=True)
    country_code = models.CharField(
        max_length=3,
        blank=True,
        default="",
        choices=COUNTRY_CHOICES,
        db_index=True,
    )
    city = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        default="",
        db_index=True,
        choices=LegacyUACity.choices,
    )
    can_relocate = models.BooleanField(default=False)
    moreinfo = models.TextField(blank=True, default="")
    looking_for = models.TextField(blank=True, default="")
    highlights = models.TextField(blank=True, default="")
    domain_zones = models.TextField(default="", blank=True)
    uninterested_company_types = models.TextField(default="", blank=True)
    question = models.TextField(blank=True, default="", null=True)

    # Profile settings
    lang = models.CharField(max_length=10, blank=True, default='EN')

    # Meta fields
    last_modified = models.DateTimeField(blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True, db_index=True)
    signup_date = models.DateTimeField(auto_now_add=True)


class Recruiter(models.Model):
    USERTYPE = "recruiter"

    name = models.CharField(max_length=255, blank=True, default='')
    email = models.EmailField(blank=False, db_index=True, unique=True)
    picture_url = models.CharField(max_length=255, blank=True, default='', null=True)

    # Profile settings
    lang = models.CharField(max_length=10, blank=True, default='EN')

    # Meta fields
    last_updated = models.DateTimeField(blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True, db_index=True)
    signup_date = models.DateTimeField(auto_now_add=True)


class JobPosting(models.Model):
    class Experience(models.TextChoices):
        ZERO = "no_exp", _("No experience")
        ONE = "1y", _("1 year")
        TWO = "2y", _("2 years")
        THREE = "3y", _("3 years")
        FIVE = "5y", _("5 years")

    class RemoteType(models.TextChoices):
        OFFICE = "office", _("Office Work")
        PARTLY_REMOTE = "partly_remote", _("Hybrid Remote")
        FULL_REMOTE = "full_remote", _("Full Remote")
        CANDIDATE_CHOICE = "candidate_choice", _("Office/Remote of your choice")

    class RelocateType(models.TextChoices):
        NO_RELOCATE = "no_relocate", _("No relocation")
        CANDIDATE_PAID = "candidate_paid", _("Covered by candidate")
        COMPANY_PAID = "company_paid", _("Covered by company")

    class AcceptRegion(models.TextChoices):
        EUROPE = "europe", _("Ukraine + Europe")
        EUROPE_ONLY = "europe_only", _("Only Europe")
        UKRAINE = "ukraine", _("Only Ukraine")
        __empty__ = _("Worldwide")

    # Job description fields
    position = models.CharField(max_length=250, blank=False, default='')
    primary_keyword = models.CharField(max_length=50, blank=True, default="")
    secondary_keyword = models.CharField(max_length=50, blank=True, default="")
    long_description = models.TextField(blank=True, default='')
    # Skills
    extra_keywords = models.CharField(max_length=250, blank=True, default="")
    location = models.CharField(max_length=250, blank=True, default="")
    country = models.CharField(max_length=250, blank=True, default="")
    salary_min = models.IntegerField(blank=True, null=True, default=0)
    salary_max = models.IntegerField(blank=True, null=True, default=0)
    exp_years = models.CharField(
        max_length=10, blank=True, default="", choices=Experience.choices
    )
    english_level = models.CharField(
        max_length=15, blank=True, default="", choices=EnglishLevel.choices
    )
    domain = models.CharField(max_length=20, blank=True, default="")
    is_parttime = models.BooleanField(default=False, db_index=True)
    has_test = models.BooleanField(default=False, db_index=True)
    requires_cover_letter = models.BooleanField(default=False, db_index=True)
    is_ukraine_only = models.BooleanField(default=False, db_index=True)
    accept_region = models.CharField(
        max_length=20, blank=True, default="", choices=AcceptRegion.choices
    )
    company_type = models.CharField(max_length=20, blank=True, default="", null=True)
    remote_type = models.CharField(max_length=20, blank=True, default="", null=True)
    relocate_type = models.CharField(
        max_length=20, blank=True, default="", choices=RelocateType.choices
    )

    # Counts
    unread_count = models.IntegerField(blank=False, default=0)
    search_count = models.IntegerField(blank=False, default=0)  # unused, how many candidates for this job
    views_count = models.IntegerField(blank=False, default=0)
    applications_count = models.IntegerField(blank=False, default=0)
    sent_count = models.IntegerField(blank=False, default=0)

    # Meta fields
    recruiter = models.ForeignKey('Recruiter', on_delete=models.CASCADE, db_index=True)

    last_modified = models.DateTimeField(blank=True, null=True, auto_now=True, db_index=True)
    published = models.DateTimeField(blank=True, null=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

class Action(str, enum.Enum):
    MESSAGE = ''

    ACCEPT = "accept"
    APPLY = "apply"
    DECLINE = "decline"
    FLAGGED = "flagged"
    HIRED = "hired"
    NOHIRE = "nohire"
    NOTLOOKING = "notlooking"
    PEEK = "peek"
    POKE = "poke"
    SHADOW_POKE = "shadowpoke"


class Action(models.TextChoices):
    ACCEPT = "accept"
    APPLY = "apply"
    PEEK = "peek"
    POKE = "poke"
    SHADOW_POKE = "shadowpoke"

class Bucket(str, enum.Enum):
    """Bucket is the current state of the message thread"""
    ARCHIVE = 'archive'
    INBOX = 'inbox'
    NOTINTERESTED = 'notinterested'
    POKES = 'pokes'
    SHORTLIST = 'shortlist'  # TODO: looks deprecated by recruiter_favorite & candidate_favorite
    UNREAD = 'unread'  # TODO: for recruiter we use INBOX bucket with `last_seen_recruiter`

class Message(models.Model):
    class Sender(models.TextChoices):
        CANDIDATE = "candidate", _("Candidate")
        RECRUITER = "recruiter", _("Recruiter")

    body = models.TextField(default="")
    action = models.CharField(max_length=40, blank=True, default="", choices=Action.choices)
    sender = models.CharField(max_length=40, blank=False, choices=Sender.choices)

    created = models.DateTimeField(db_index=True)
    notified = models.DateTimeField(blank=True, null=True, db_index=True)
    edited = models.DateTimeField(blank=True, null=True, db_index=True)

    recruiter = models.ForeignKey("Recruiter", on_delete=models.CASCADE)
    candidate = models.ForeignKey("Candidate", on_delete=models.CASCADE)
    job = models.ForeignKey(
        "JobPosting", on_delete=models.SET_NULL, null=True, blank=True
    )
    thread = models.ForeignKey(
        "MessageThread", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ('created',)


class MessageThread(models.Model):
    class MatchReason(models.TextChoices):
        MATCHED = "matched_v1"
        RECRUITER_POKED = "recruiter_poked"
        RECRUITER_SHORTLISTED = "recruiter_shortlisted"
        RECRUITER_ANSWERED = "recruiter_answered"
        RECRUITER_ARCHIVED = "recruiter_archived"
        NO_RELATED_JOB = "no_related_job"
        ACCEPTED = "accepted"
        DECLINED = "declined"

    is_anonymous = models.BooleanField(default=True)
    iou_bonus = models.IntegerField(blank=True, default=0)
    last_sender = models.CharField(
        max_length=40, blank=False, choices=Message.Sender.choices
    )
    first_message = models.CharField(max_length=16, blank=False, choices=Action.choices)
    bucket = models.CharField(max_length=40, default=Bucket.INBOX, db_index=True)

    candidate_archived = models.BooleanField(blank=True, default=False)
    candidate_favorite = models.BooleanField(blank=True, null=True, db_index=True)
    feedback_candidate = models.CharField(max_length=20, blank=True, default="")

    recruiter_favorite = models.BooleanField(blank=True, null=True, db_index=True)
    feedback_recruiter = models.CharField(max_length=20, blank=True, default="")
    notified_notinterested = models.DateTimeField(blank=True, null=True, db_index=True)

    job = models.ForeignKey("JobPosting", on_delete=models.SET_NULL, null=True, blank=True)
    candidate = models.ForeignKey("Candidate", on_delete=models.CASCADE)
    recruiter = models.ForeignKey("Recruiter", on_delete=models.CASCADE)

    last_updated = models.DateTimeField(blank=False, db_index=True)
    last_seen_recruiter = models.DateTimeField(null=True)
    last_seen_candidate = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = CustomManager()

    @property
    def last_message(self):
        return self.message_set.last()

    class Meta:
        ordering = ("-last_updated",)
        unique_together = (Message.Sender.CANDIDATE, Message.Sender.RECRUITER)

