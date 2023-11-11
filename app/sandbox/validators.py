from abc import abstractmethod


class BaseValidator:
    def __init__(self, candidate, job):
        self.candidate = candidate
        self.job = job

    @abstractmethod
    def is_valid(self):
        return True
