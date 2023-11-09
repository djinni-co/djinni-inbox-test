from abc import abstractmethod


class ScoreAlgorithm:
    def __init__(self):
        self.score = 0
        self.rules = []

    def add(self, rule):
        self.rules.append(rule)

    def calculate(self):
        return sum([condition.execute() for condition in self.rules])

    def calculation_plan(self):
        return [f"{i}. {condition.describe()}" for (i, condition) in enumerate(self.rules, 1)]


class Rule:

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def describe(self):
        pass


class SimpleRule(Rule):

    def __init__(self, score, description=None):
        self.score = score
        self.description = description

    def execute(self):
        return self.score

    def describe(self):
        return f"{self.description + ':' or ''} Add {self.score} to total scoring"


class IterableRule(Rule):
    def __init__(self, score_per_item, iterable, description=None):
        self.per_item_score = score_per_item
        self.iterable = iterable
        self.description = description

    def execute(self):
        return sum([self.per_item_score for _ in self.iterable])

    def describe(self):
        return f"{self.description + ':' or ''} Add {self.per_item_score} to total scoring per " \
               f"each item in collection: {self.iterable}"


class LogicalRule(Rule):
    def __init__(self, score, when, description=None, otherwise=0):
        self.score = score
        self.condition = when
        self.description = description
        self.otherwise = otherwise

    def execute(self):
        return self.score if self.condition else self.otherwise

    def describe(self):
        return f"Add {self.score} to total scoring when condition {self.description or self.condition} is met."
