import re

class paging:
    INBOX = 5

class sorting:
    class id:
        RECENT   = 'recent'
        ADVANCED = 'adv'

        SALARY_LOW_HIGH = 'sal-lh'
        SALARY_HIGH_LOW = 'sal-hl'

        EXPERIENCE_LOW_HIGH = 'exp-lh'
        EXPERIENCE_HIGH_LOW = 'exp-hl'

    class text:
        RECENT   = 'Most Recent First'
        ADVANCED = 'Advanced Sorting'

        SALARY_LOW_HIGH = 'Salary Low-High'
        SALARY_HIGH_LOW = 'Salary High-Low'

        EXPERIENCE_LOW_HIGH = 'Experience Low-High'
        EXPERIENCE_HIGH_LOW = 'Experience High-Low'

class inbox:
    class http:
        class param:
            SORTING = 's'
            PAGING = 'p'

    class paging:
        PER_PAGE = paging.INBOX

    class sorting:
        class recent:
            id   = sorting.id.RECENT
            text = sorting.text.RECENT

        class salary_low_high:
            id   = sorting.id.SALARY_LOW_HIGH
            text = sorting.text.SALARY_LOW_HIGH

        class salary_high_low:
            id   = sorting.id.SALARY_HIGH_LOW
            text = sorting.text.SALARY_HIGH_LOW

        class experience_low_high:
            id   = sorting.id.EXPERIENCE_LOW_HIGH
            text = sorting.text.EXPERIENCE_LOW_HIGH

        class experience_high_low:
            id   = sorting.id.EXPERIENCE_HIGH_LOW
            text = sorting.text.EXPERIENCE_HIGH_LOW

        class advanced:
            id   = sorting.id.ADVANCED
            text = sorting.text.ADVANCED

        DEFAULT = recent
        LIST = [
            recent,
            salary_low_high,
            salary_high_low,
            experience_low_high,
            experience_high_low,
            advanced,
        ]
