from functools import reduce
from typing import Type

from .enums import ScoreConfig
from .scoring_settings import SCORING_FIELDS_CONFIG


class ConfigParser:
    def __init__(self, config: dict):
        self.config = config

    @property
    def get_base_score_settings(self):
        return map(lambda value: self.config.get(value, 0), (
            ScoreConfig.WEIGHT, ScoreConfig.ADD_EXTRA_WEIGHT, ScoreConfig.DEFAULT_MIN_WEIGHT,
            ScoreConfig.EXTRA_WEIGHT_PER_UNIT, ScoreConfig.NAME))

    @property
    def get_scoring_data(self):
        search_q_info, search_v_info, analyzer, validator = map(
            lambda value: self.config.get(value, 0), (ScoreConfig.SEARCH_QUERY, ScoreConfig.SEARCH_VECTOR,
                                                      ScoreConfig.MATCH_ANALYZER, ScoreConfig.VALIDATOR))
        search_q_field, search_q_adapter = map(search_q_info.get, (ScoreConfig.FIELD, ScoreConfig.ADAPTER))
        search_v_field, search_v_adapter = map(search_v_info.get, (ScoreConfig.FIELD, ScoreConfig.ADAPTER))

        return search_q_field, search_q_adapter, search_v_field, search_v_adapter, analyzer, validator


class ScoreAnalyzer:
    __slots__ = ('scoring_settings', 'job', 'candidate', 'config_parser')

    def __init__(self, job, candidate, scoring_settings, config_parser: Type[ConfigParser]):
        self.scoring_settings = scoring_settings
        self.job = job
        self.candidate = candidate
        self.config_parser = config_parser

    @staticmethod
    def get_instance_data(search_field, obj):
        if isinstance(search_field, str):
            return getattr(obj, search_field)
        search_field_1, search_field_2 = search_field
        return getattr(obj, search_field_1), getattr(obj, search_field_2)

    def calculate_score_for_single_unit(self, config):

        # scoring  settings
        weight, add_extra_weight, default_min_weight, extra_weight_per_unit, name = (
            self.config_parser(config).get_base_score_settings
        )

        search_q_field, search_q_adapter, search_v_field, search_v_adapter, analyzer, validator = (
            self.config_parser(config).get_scoring_data
        )

        if validator and not validator(candidate=self.candidate, job=self.job).is_valid():
            return {name: default_min_weight}

        search_q_data = self.get_instance_data(search_q_field, self.job)
        search_v_data = self.get_instance_data(search_v_field, self.candidate)

        if not search_q_data or not search_v_data:
            return {name: default_min_weight}

        adapted_search_q_data = search_q_adapter(
            search_q_data).convert() if search_q_adapter else search_q_data
        adapted_search_v_data = search_v_adapter(
            search_v_data).convert() if search_v_adapter else search_v_data

        score = analyzer(
            weight=weight,
            add_extra_weight=add_extra_weight,
            extra_weight_per_unit=extra_weight_per_unit,
            default_min_weight=default_min_weight
        ).score(search_query=adapted_search_q_data, search_vector=adapted_search_v_data)
        return {name: score}

    def calculate_score(self):
        """
            builds dict next structure {'english': <score>, 'salary': <score>}
        """
        return reduce(lambda acc, config: {**acc, **self.calculate_score_for_single_unit(config)},
                      self.scoring_settings, {})


class ThreadScore:

    @staticmethod
    def score_thread(thread):
        job, candidate = thread.job, thread.candidate
        candidate_score = ScoreAnalyzer(
            job=job, candidate=candidate, scoring_settings=SCORING_FIELDS_CONFIG, config_parser=ConfigParser
        ).calculate_score()
        thread.scores = candidate_score
        return thread


class BulkThreadScore(ThreadScore):
    def bulk_score(self, threads):
        from .models import MessageThread
        update_threads = list(map(self.score_thread, threads))
        MessageThread.objects.bulk_update(update_threads, ['scores'])
