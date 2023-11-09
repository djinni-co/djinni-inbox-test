import abc
from itertools import groupby

from django.conf import settings
from gensim.corpora import Dictionary
from gensim.matutils import cossim
from gensim.models import TfidfModel
from gensim.utils import simple_preprocess

from .models import MessageThread, JobPosting, Candidate, EnglishLevel
from .utils import cosine_similarity, vectorize, get_choice_index


class InboxScorer(abc.ABC):
    def score(self) -> list[float]:
        pass

    @staticmethod
    def parse_candidate_keywords(candidate: Candidate) -> list[str]:
        dataset: list[str] = [candidate.position, candidate.primary_keyword]
        if candidate.skills_cache:
            dataset.append(candidate.skills_cache)
        if candidate.moreinfo:
            dataset.append(candidate.moreinfo)
        if candidate.looking_for:
            dataset.append(candidate.looking_for)
        if candidate.highlights:
            dataset.append(candidate.highlights)

        return list(set(simple_preprocess(' '.join(dataset), deacc=True)))

    @staticmethod
    def parse_job_keywords(job: JobPosting) -> list[str]:
        dataset: list[str] = [job.position, job.primary_keyword]
        if job.secondary_keyword:
            dataset.append(job.secondary_keyword)

        return list(set(simple_preprocess(' '.join(dataset), deacc=True)))

    @staticmethod
    def base_score(job: JobPosting, candidate: Candidate) -> float:
        score: float = 0.0
        scoring_settings = settings.SCORING_SETTINGS
        candidate_eng = get_choice_index(EnglishLevel, candidate.english_level) + 1
        desired_eng = get_choice_index(EnglishLevel, job.english_level) + 1

        score += (candidate.experience_years - 0 if job.exp_years == JobPosting.Experience.ZERO
                  else int(job.exp_years[:-1])) / 10 * scoring_settings.SCORE_EXP_WEIGHT
        score += (candidate_eng - desired_eng) / 10 * scoring_settings.SCORE_ENG_WEIGHT
        score += -scoring_settings.SCORE_SALARY_WEIGHT if candidate.salary_min > job.salary_max \
            else scoring_settings.SCORE_SALARY_WEIGHT if candidate.salary_min < job.salary_min else 0

        if candidate.uninterested_company_types:
            score -= scoring_settings.SCORE_COMPANY_TYPE_WEIGHT if job.company_type in candidate.uninterested_company_types.split(', ') else 0

        return score


class SimilarityInboxScorer(InboxScorer):
    def __init__(self, inbox: list[MessageThread]):
        self._inbox = inbox

    def score(self) -> list[float]:
        scores: list[float] = []
        for thread in self._inbox:
            bow = self.parse_job_keywords(thread.job)
            job_vector = vectorize(bow, bow)

            candidate_vector = vectorize(self.parse_candidate_keywords(thread.candidate), bow)
            score = cosine_similarity(candidate_vector, job_vector)
            base_score = self.base_score(thread.job, thread.candidate)
            scores.append(max(0, min(1, score + base_score)))

        return scores


class TfidfInboxScorer(InboxScorer):
    def __init__(self, inbox: list[MessageThread]):
        self._inbox: list[MessageThread] = inbox
        self._jobToThreads: dict[JobPosting, list[MessageThread]] = {}

        for job, threads in groupby(self._inbox, lambda thread: thread.job):
            self._jobToThreads.setdefault(job, []).extend(threads)

    def score(self) -> list[float]:
        scores: list[float] = []
        for job, threads in self._jobToThreads.items():
            model, dictionary = self._gather_corpus(job, threads)

            for thread in threads:
                candidate_vector = model[dictionary.doc2bow(self.parse_candidate_keywords(thread.candidate))]
                job_vector = model[dictionary.doc2bow(self.parse_job_keywords(thread.job))]

                score = cossim(candidate_vector, job_vector)
                scores.append(score)

        return scores

    def _gather_corpus(self, job: JobPosting, threads: list[MessageThread]) -> tuple[TfidfModel, Dictionary]:
        candidates_keywords = [self.parse_candidate_keywords(thread.candidate) for thread in threads]
        job_keywords = [self.parse_job_keywords(job)]

        corpus = job_keywords + candidates_keywords
        dictionary = Dictionary(corpus)
        model = TfidfModel([dictionary.doc2bow(doc) for doc in corpus], id2word=dictionary)

        return model, dictionary
