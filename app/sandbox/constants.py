import re

class paging:
    INBOX = 5

class templates:
    class html:
        class id:
            CHAT_LIST = 'chat-list'
            ADVANCED_SORTING_TOOL = 'adv-sorting-tool'

        class name:
            JOB_FILTER = 'job-filter'

class sorting:
    class id:
        RECENT   = 'recent'
        ADVANCED = 'adv'

    class text:
        RECENT   = 'Most Recent First'
        ADVANCED = 'Advanced Sorting'

class inbox:
    class html:
        class id:
            CHAT_LIST  = templates.html.id.CHAT_LIST
            ADVANCED_SORTING_TOOL = templates.html.id.ADVANCED_SORTING_TOOL

    class http:
        class param:
            SORTING = 'so'
            PAGING = 'p'
            JOB_FILTER = templates.html.name.JOB_FILTER

            # AST - Advanced Sorting Tool
            class ast:
                SALARY     = 'ast-salary'
                EXPERIENCE = 'ast-experience'
                SKILLS     = 'ast-skills'
                ENGLISH    = 'ast-english'

    class paging:
        PER_PAGE = paging.INBOX

    class sorting:
        class recent:
            id   = sorting.id.RECENT
            text = sorting.text.RECENT

        class advanced:
            id   = sorting.id.ADVANCED
            text = sorting.text.ADVANCED

        DEFAULT = recent
        AVAILABLE_METHODS = [
            recent,
            advanced,
        ]

        @classmethod
        def str2obj (cls, string):
            for sort_order in cls.AVAILABLE_METHODS:
                if string in [sort_order.id, sort_order.text]:
                    return sort_order

            return None
