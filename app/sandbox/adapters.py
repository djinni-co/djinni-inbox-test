from abc import abstractmethod


class Adapter:
    def __init__(self, value):
        self.value = value

    @abstractmethod
    def convert(self):
        pass


class EnglishLevelAdapter(Adapter):

    def convert(self):
        from .models import EnglishLevel
        eng_map = {
            EnglishLevel.NONE: 0,
            EnglishLevel.BASIC: 1,
            EnglishLevel.PRE: 2,
            EnglishLevel.INTERMEDIATE: 3,
            EnglishLevel.UPPER: 3,
            EnglishLevel.FLUENT: 4,
        }
        return eng_map.get(self.value)


class ExpAdapter(Adapter):
    def convert(self):
        from .models import JobPosting
        exp_map = {
            JobPosting.Experience.ZERO: 0.0,
            JobPosting.Experience.ONE: 1.0,
            JobPosting.Experience.TWO: 2.0,
            JobPosting.Experience.THREE: 3.0,
            JobPosting.Experience.FIVE: 5.0,
        }
        return exp_map.get(self.value)
