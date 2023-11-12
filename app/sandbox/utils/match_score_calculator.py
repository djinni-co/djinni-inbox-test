from sandbox.models import Candidate, JobPosting
import re

class MatchScoreCalculator:
    def __init__(self, candidate, job_posting):
        self.candidate = candidate
        self.job_posting = job_posting
        self.english_levels = ['no_english', 'basic', 'pre', 'intermediate', 'upper', 'fluent']

    def get_metrics(self):
        return {
            'Skills': self.calculate_skills_score(),
            'Experience': self.calculate_experience_score(),
            'Salary': self.calculate_salary_score(),
            'EnglishLevel': self.calculate_english_score(),
            'Location': self.calculate_location_score(),
            'Relocation': self.calculate_relocation_score(),
            'Domain': self.calculate_domain_score(),
            'UninterestedCompanyTypes': self.calculate_uninterested_company_types_score(),
            'Uniqueness': self.calculate_uniqueness_score()
        }

    def calculate_skills_score(self):
        candidate_skills = self.parse_skills(self.candidate.skills_cache) | {self.candidate.primary_keyword, self.candidate.secondary_keyword}
        job_skills = set(filter(None, [self.job_posting.primary_keyword, self.job_posting.secondary_keyword]))
        matches = job_skills.intersection(candidate_skills)
        return len(matches) / len(job_skills) if matches else 0

    def calculate_experience_score(self):
        candidate_exp = self.candidate.experience_years
        job_exp = self.convert_exp_to_float(self.job_posting.exp_years)
        return 1 if candidate_exp >= job_exp else candidate_exp / job_exp

    def calculate_salary_score(self):
        if self.job_posting.salary_min <= self.candidate.salary_min <= self.job_posting.salary_max:
            return 1
        else:
            return self.job_posting.salary_max / self.candidate.salary_min

    def calculate_english_score(self):
        candidate_level = self.english_levels.index(self.candidate.english_level)
        job_level = self.english_levels.index(self.job_posting.english_level)
        return 1 if candidate_level >= job_level else candidate_level / job_level

    def calculate_location_score(self):
        if self.job_posting.remote_type == 'candidate_choice':
            return 1
        if self.candidate.country_code == self.job_posting.country:
            if (self.candidate.location, self.candidate.country_code) == (self.job_posting.location, self.job_posting.country):
                return 1
            elif self.job_posting.location is None:
                return 1
            elif self.candidate.location != self.job_posting.location:
                return 0.5
        return 0

    def calculate_relocation_score(self):
        return 1 if self.job_posting.relocate_type != 'no_relocate' and self.candidate.can_relocate else 0

    def calculate_domain_score(self):
        candidate_domains_set = self.parse_skills(self.candidate.domain_zones) if self.candidate.domain_zones else set()
        return -1 if self.job_posting.domain in candidate_domains_set else 0

    def calculate_uninterested_company_types_score(self):
        candidate_uninterested_company_types = self.candidate.uninterested_company_types
        job_company_type = self.job_posting.company_type
        uninterested_set = self.parse_skills(candidate_uninterested_company_types) if candidate_uninterested_company_types else set()
        return -1 if job_company_type in uninterested_set else 0

    def calculate_uniqueness_score(self):
        return 1 / (self.job_posting.applications_count) if self.job_posting.applications_count > 0 else 1

    def parse_skills(self, skills_cache):
        if skills_cache is None:
            return set()
        return set(re.split(r'[;,\s\/]\s*', skills_cache))

    def convert_exp_to_float(self, exp_years):
        return 0 if exp_years == 'no_exp' else float(exp_years.rstrip('y'))
