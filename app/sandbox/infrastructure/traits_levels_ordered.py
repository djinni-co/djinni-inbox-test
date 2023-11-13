from sandbox.models import EnglishLevel, JobPosting

english_levels_ordered = [EnglishLevel.NONE,
                          EnglishLevel.BASIC,
                          EnglishLevel.PRE,
                          EnglishLevel.INTERMEDIATE,
                          EnglishLevel.UPPER,
                          EnglishLevel.FLUENT]

position_levels_ordered = []

experience = JobPosting.Experience
experience_levels_ordered = {experience.ZERO: 0,
                             experience.ONE: 1,
                             experience.TWO: 2,
                             experience.THREE: 3,
                             experience.FIVE: 5}

