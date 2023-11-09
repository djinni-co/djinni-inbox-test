import enum


class ThreadsSort(str, enum.Enum):
    RECENT: str = 'recent'
    RELEVANT: str = 'relevant'

    def __str__(self) -> str:
        return self.value
