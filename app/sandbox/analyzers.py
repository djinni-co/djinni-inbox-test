from abc import abstractmethod
import math


class MatchAnalyzer:

    def __init__(self,
                 weight,
                 default_min_weight=0,
                 add_extra_weight=False,
                 extra_weight_per_unit=None,
                 ):
        self.weight = weight
        self.extra_weight_per_unit = extra_weight_per_unit
        self.default_min_weight = default_min_weight
        self.add_extra_weight = add_extra_weight

    def calculate_and_add_extra_weight(self, min_v, search_vector):
        delta = abs(search_vector - min_v)
        extra_weight = (delta / 10 ** int(math.log10(delta))) * self.extra_weight_per_unit
        return extra_weight + self.weight

    @abstractmethod
    def score(self, search_query, search_vector):
        pass


class IntEqualityAnalyzer(MatchAnalyzer):

    def score(self, search_query, search_vector):
        if search_query == search_vector:
            return self.weight
        if search_query < search_vector:
            if self.add_extra_weight:
                return self.calculate_and_add_extra_weight(search_query, search_vector)
            return self.weight
        return self.default_min_weight


class StrEqualityAnalyzer(MatchAnalyzer):

    def score(self, search_query, search_vector):
        if search_query.lower() == search_vector.lower():
            return self.weight
        return self.default_min_weight


class RangeMatchAnalyzer(MatchAnalyzer):

    def score(self, search_query, search_vector):
        min_v, max_v = search_query
        if min_v <= search_vector <= max_v or min_v > search_vector:
            return self.weight
        elif min_v > search_vector:
            if self.add_extra_weight:
                return self.calculate_and_add_extra_weight(min_v, search_vector)
            return self.weight
        return self.default_min_weight


class StringInListAnalyzer(MatchAnalyzer):
    def score(self, search_query, search_vector):
        search_vector = [word.strip().lower() for word in search_vector.split(',')]
        search_query = search_query.lower()
        if search_query not in search_vector:
            return self.default_min_weight
        return self.weight

