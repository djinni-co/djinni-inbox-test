import abc
from itertools import groupby

from gensim.corpora import Dictionary
from gensim.matutils import cossim
from gensim.models import TfidfModel
from gensim.utils import simple_preprocess

from .models import MessageThread, JobPosting, Candidate
from .utils import cosine_similarity, vectorize


class InboxScorer(abc.ABC):
    def score(self) -> list[tuple[int, float]]:
        pass

    @staticmethod
    def parse_candidate_keywords(candidate: Candidate) -> list[str]:
        keywords = simple_preprocess(candidate.position, deacc=True) + simple_preprocess(candidate.primary_keyword)
        if candidate.skills_cache:
            keywords.extend(simple_preprocess(candidate.skills_cache, deacc=True))
        if candidate.moreinfo:
            keywords.extend(simple_preprocess(candidate.moreinfo, deacc=True))

        return list(set(keywords))

    @staticmethod
    def parse_job_keywords(job: JobPosting) -> list[str]:
        keywords = simple_preprocess(job.position, deacc=True) + simple_preprocess(job.primary_keyword)
        if job.secondary_keyword:
            keywords.extend(simple_preprocess(job.secondary_keyword))

        return list(set(keywords))


class SimilarityInboxScorer(InboxScorer):
    def __init__(self, inbox: list[MessageThread]):
        self._inbox = inbox
        self._jobToThreads: dict[JobPosting, list[MessageThread]] = {}

        for job, threads in groupby(self._inbox, lambda thread: thread.job):
            self._jobToThreads.setdefault(job, []).extend(threads)

    def score(self) -> list[tuple[int, float]]:
        scores: list[tuple[int, float]] = []
        for job, threads in self._jobToThreads.items():
            bow = self.parse_job_keywords(job)
            job_vector = vectorize(bow, bow)

            for thread in threads:
                candidate_vector = vectorize(self.parse_candidate_keywords(thread.candidate), bow)
                print("Relevance score: ", score := cosine_similarity(candidate_vector, job_vector))
                scores.append((thread.id, score))

        return scores


class TfidfInboxScorer(InboxScorer):
    def __init__(self, inbox: list[MessageThread]):
        self._inbox: list[MessageThread] = inbox
        self._jobToThreads: dict[JobPosting, list[MessageThread]] = {}

        for job, threads in groupby(self._inbox, lambda thread: thread.job):
            self._jobToThreads.setdefault(job, []).extend(threads)

    def score(self) -> list[tuple[int, float]]:
        scores: list[tuple[int, float]] = []
        for job, threads in self._jobToThreads.items():
            model, dictionary = self._gather_corpus(job, threads)

            for thread in threads:
                candidate_vector = model[dictionary.doc2bow(self.parse_candidate_keywords(thread.candidate))]
                job_vector = model[dictionary.doc2bow(self.parse_job_keywords(thread.job))]

                score = cossim(candidate_vector, job_vector)
                scores.append((thread.id, score))

        return scores

    def _gather_corpus(self, job: JobPosting, threads: list[MessageThread]) -> tuple[TfidfModel, Dictionary]:
        candidates_keywords = [self.parse_candidate_keywords(thread.candidate) for thread in threads]
        job_keywords = [self.parse_job_keywords(job)]

        corpus = job_keywords + candidates_keywords
        dictionary = Dictionary(corpus)
        model = TfidfModel([dictionary.doc2bow(doc) for doc in corpus], id2word=dictionary)

        return model, dictionary
