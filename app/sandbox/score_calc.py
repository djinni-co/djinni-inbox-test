import re
from .models import EnglishLevel

regex = re.compile('[^a-zA-Z\s/]')


def make_skills_set(sentence: str) -> set:
    """
    :returns: set of skills
    cleans sentences from non-chars symbols and splits them into words.
    """
    words = regex.sub('', sentence)
    words = set(words.replace('/', ' ').split(' '))
    for item in ['a', 'the', 'in', 'for', 'and', 'to', 'of', 'with', 'well', 'team', 'will', 'help', 'up', 'that', '', 'our', 'both']:
        words.discard(item)
    return words


class ScoreCalc:
    def __init__(self, candidate, job):
        self.candidate = candidate
        self.job = job

    @property
    def by_keyword(self):
        """
        represents score by primary_keyword and secondary_keyword
        if keywords are equal it gives +1 to the score and 0 in the versa case
        """
        score = 0.0
        if self.candidate.primary_keyword:
            score += 1.0 if self.candidate.primary_keyword.lower() == self.job.primary_keyword.lower() else 0.0
        if self.candidate.secondary_keyword and self.job.secondary_keyword:
            score += 1.0 if self.candidate.secondary_keyword.lower() == self.job.secondary_keyword.lower() else 0.0
        return score

    @property
    def by_skills(self):
        """
        represents a skill score.
        parses the job description and candidate's  skills,
        searches for intersections, and gives +1 for each match
        """
        score = 0.0
        if not self.candidate.skills_cache:
            return score
        job_requirements = self.job.long_description.lower().split('.')
        candidate_skills = self.candidate.skills_cache.lower()
        skills = make_skills_set(candidate_skills)
        categories = {'requirements': 1.0, 'will be a plus': 0.5}
        for category in categories.keys():
            for sentence in job_requirements:
                if category in sentence:
                    score += categories.get(category) * len(make_skills_set(sentence.split(':')[1]).intersection(skills))
        return score

    @property
    def by_english_level(self):
        """
        represents an english level score.
        if candidate_level greater than required_level returns 1.0 and -0.5 for each level lower the required
        """
        levels = {
            EnglishLevel.NONE: 0,
            EnglishLevel.BASIC: 1,
            EnglishLevel.PRE: 2,
            EnglishLevel.INTERMEDIATE: 3,
            EnglishLevel.UPPER: 4,
            EnglishLevel.FLUENT: 5
        }
        candidate_level = levels.get(self.candidate.english_level, 0)
        required_level = levels.get(self.job.english_level, 0)
        return 1.0 if candidate_level >= required_level else (required_level-candidate_level)/2

    @property
    def by_experience_years(self):
        """
        represents experience score
        if candidate experience more then the vacancy required returns 1.0 and -0.5 for each year lower the required
        """
        search_res = re.findall('\d+', self.job.exp_years)
        job_exp_years = float(search_res[0] if search_res else 0)
        candidate_experience_years = float(self.candidate.experience_years)
        score = 1.0 if candidate_experience_years >= job_exp_years else (candidate_experience_years - job_exp_years)/2
        return score

    @property
    def by_company_type(self):
        score = 0.0
        if not self.candidate.uninterested_company_types:
            return score
        uninterested_company_types = self.candidate.uninterested_company_types.split(', ')
        if self.job.company_type in uninterested_company_types:
            score -= 1.0
        return score

    def get_score(self):
        total_score = self.by_keyword +\
                      self.by_skills + \
                      self.by_english_level + \
                      self.by_experience_years + \
                      self.by_company_type
        return total_score
