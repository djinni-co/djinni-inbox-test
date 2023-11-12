import enum


class ScoreConfig(enum.Enum):
    SEARCH_QUERY = 'search_query'
    SEARCH_VECTOR = 'search_vector'
    ADAPTER = 'adapter'
    FIELD = 'field'
    MATCH_ANALYZER = 'match_analyzer'
    WEIGHT = 'weight'
    ADD_EXTRA_WEIGHT = 'add_extra_weight'
    EXTRA_WEIGHT_PER_UNIT = 'extra_weight_per_unit'
    DEFAULT_MIN_WEIGHT = 'default_min_weight'
    NAME = 'name'
    VALIDATOR = 'validator'
