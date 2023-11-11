from functools import reduce

from .enums import ScoreConfig
from .scoring_settings import SCORING_FIELDS_CONFIG


class ScoreAnalyzer:
    __slots__ = ('scoring_settings', 'job', 'candidate')

    def __init__(self, job, candidate, scoring_settings):
        self.scoring_settings = scoring_settings
        self.job = job
        self.candidate = candidate

    @staticmethod
    def get_search_data(search_field, obj):
        if isinstance(search_field, str):
            return getattr(obj, search_field)
        search_field_1, search_field_2 = search_field
        return getattr(obj, search_field_1), getattr(obj, search_field_2)

    def calculate_score_for_single_unit(self, scoring_data):
        search_query = scoring_data.get(ScoreConfig.SEARCH_QUERY)
        search_vector = scoring_data.get(ScoreConfig.SEARCH_VECTOR)
        match_analyzer = scoring_data.get(ScoreConfig.MATCH_ANALYZER)
        validator = scoring_data.get(ScoreConfig.VALIDATOR)

        # Scoring settings #
        weight = scoring_data.get(ScoreConfig.WEIGHT)
        add_extra_weight = scoring_data.get(ScoreConfig.ADD_EXTRA_WEIGHT, False)
        default_min_weight = scoring_data.get(ScoreConfig.DEFAULT_MIN_WEIGHT, 0)
        extra_weight_per_unit = scoring_data.get(ScoreConfig.EXTRA_WEIGHT_PER_UNIT, 0)
        name = scoring_data.get(ScoreConfig.NAME)

        if validator and not validator(candidate=self.candidate, job=self.job).is_valid():
            return {name: default_min_weight}

        search_query_field = search_query.get(ScoreConfig.FIELD)
        search_query_adapter = search_query.get(ScoreConfig.ADAPTER)

        search_vector_field = search_vector.get(ScoreConfig.FIELD)
        search_vector_adapter = search_vector.get(ScoreConfig.ADAPTER)

        search_query_data = self.get_search_data(search_query_field, self.job)
        search_vector_data = self.get_search_data(search_vector_field, self.candidate)

        if not search_query_data or not search_vector_data:
            return {name: default_min_weight}

        adapted_search_query_data = search_query_adapter(
            search_query_data).convert() if search_query_adapter else search_query_data
        adapted_search_vector_data = search_vector_adapter(
            search_vector_data).convert() if search_vector_adapter else search_vector_data

        score = match_analyzer(

            weight=weight,
            add_extra_weight=add_extra_weight,
            extra_weight_per_unit=extra_weight_per_unit,
            default_min_weight=default_min_weight

        ).score(
            search_query=adapted_search_query_data, search_vector=adapted_search_vector_data
        )
        return {name: score}

    def calculate_score(self):
        """
            builds dict next structure {'english': <score>, 'salary': <score>}
        """
        return reduce(lambda acc, item: {**acc, **self.calculate_score_for_single_unit(item)},
                      self.scoring_settings, {})


class ThreadScore:

    @staticmethod
    def score_thread(thread):
        job, candidate = thread.job, thread.candidate
        candidate_score = ScoreAnalyzer(
            job=job, candidate=candidate, scoring_settings=SCORING_FIELDS_CONFIG
        ).calculate_score()
        thread.scores = candidate_score
        return thread


class BulkThreadScore(ThreadScore):
    def bulk_score(self, threads):
        from .models import MessageThread
        update_threads = list(map(self.score_thread, threads))
        MessageThread.objects.bulk_update(update_threads, ['scores'])
