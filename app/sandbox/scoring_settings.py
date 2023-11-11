from .enums import ScoreConfig
from .analyzers import RangeMatchAnalyzer, IntEqualityAnalyzer, StrEqualityAnalyzer, StringInListAnalyzer
from .adapters import EnglishLevelAdapter, ExpAdapter
from .validators import BaseValidator


SALARY_CONFIG = {
    ScoreConfig.NAME: "salary",
    ScoreConfig.SEARCH_QUERY: {
        ScoreConfig.FIELD: ["salary_min", "salary_max"]
    },

    ScoreConfig.SEARCH_VECTOR: {
        ScoreConfig.FIELD: "salary_min"
    },
    ScoreConfig.MATCH_ANALYZER: RangeMatchAnalyzer,
    ScoreConfig.WEIGHT: 1,
    ScoreConfig.ADD_EXTRA_WEIGHT: True,
    ScoreConfig.EXTRA_WEIGHT_PER_UNIT: 0.2,
    ScoreConfig.VALIDATOR: BaseValidator
}

EXPERIENCE_CONFIG = {
    ScoreConfig.NAME: "experience",
    ScoreConfig.SEARCH_QUERY: {
        ScoreConfig.FIELD: "exp_years",
        ScoreConfig.ADAPTER: ExpAdapter
    },

    ScoreConfig.SEARCH_VECTOR: {
        ScoreConfig.FIELD: "experience_years"
    },
    ScoreConfig.MATCH_ANALYZER: IntEqualityAnalyzer,
    ScoreConfig.WEIGHT: 1.3,
    ScoreConfig.ADD_EXTRA_WEIGHT: True,
    ScoreConfig.EXTRA_WEIGHT_PER_UNIT: 0.2
}

ENGLISH_LEVEL_CONFIG = {
    ScoreConfig.NAME: "english",
    ScoreConfig.SEARCH_QUERY: {
        ScoreConfig.FIELD: "english_level",
        ScoreConfig.ADAPTER: EnglishLevelAdapter
    },

    ScoreConfig.SEARCH_VECTOR: {
        ScoreConfig.FIELD: "english_level",
        ScoreConfig.ADAPTER: EnglishLevelAdapter

    },
    ScoreConfig.MATCH_ANALYZER: IntEqualityAnalyzer,
    ScoreConfig.WEIGHT: 1,
    ScoreConfig.ADD_EXTRA_WEIGHT: True,
    ScoreConfig.EXTRA_WEIGHT_PER_UNIT: 0.1
}

POSITION_CONFIG = {
    ScoreConfig.NAME: "position",
    ScoreConfig.SEARCH_QUERY: {
        ScoreConfig.FIELD: "position"
    },

    ScoreConfig.SEARCH_VECTOR: {
        ScoreConfig.FIELD: "position"
    },
    ScoreConfig.MATCH_ANALYZER: StrEqualityAnalyzer,
    ScoreConfig.WEIGHT: 0.2
}

PRIMARY_KEYWORDS_CONFIG = {
    ScoreConfig.NAME: "primary_keywords",
    ScoreConfig.SEARCH_QUERY: {
        ScoreConfig.FIELD: "primary_keyword"
    },

    ScoreConfig.SEARCH_VECTOR: {
        ScoreConfig.FIELD: "primary_keyword"
    },
    ScoreConfig.MATCH_ANALYZER: StrEqualityAnalyzer,
    ScoreConfig.WEIGHT: 1
}

SECONDARY_KEYWORDS_CONFIG = {
    ScoreConfig.NAME: "secondary_keywords",
    ScoreConfig.SEARCH_QUERY: {
        ScoreConfig.FIELD: "secondary_keyword"
    },

    ScoreConfig.SEARCH_VECTOR: {
        ScoreConfig.FIELD: "secondary_keyword"
    },
    ScoreConfig.MATCH_ANALYZER: StrEqualityAnalyzer,
    ScoreConfig.WEIGHT: 0.7
}

LOCATION_CONFIG = {
    ScoreConfig.NAME: "location",
    ScoreConfig.SEARCH_QUERY: {
        ScoreConfig.FIELD: "location"
    },

    ScoreConfig.SEARCH_VECTOR: {
        ScoreConfig.FIELD: "location"
    },
    ScoreConfig.MATCH_ANALYZER: StrEqualityAnalyzer,
    ScoreConfig.WEIGHT: 0.3
}

DOMAIN_CONFIG = {
    ScoreConfig.NAME: "domain",
    ScoreConfig.SEARCH_QUERY: {
        ScoreConfig.FIELD: "domain"
    },

    ScoreConfig.SEARCH_VECTOR: {
        ScoreConfig.FIELD: "domain_zones"
    },
    ScoreConfig.MATCH_ANALYZER: StringInListAnalyzer,
    ScoreConfig.WEIGHT: 0.5
}

SCORING_FIELDS_CONFIG = [
    SALARY_CONFIG, EXPERIENCE_CONFIG, ENGLISH_LEVEL_CONFIG, POSITION_CONFIG, PRIMARY_KEYWORDS_CONFIG,
    SECONDARY_KEYWORDS_CONFIG, LOCATION_CONFIG, DOMAIN_CONFIG
]
