from typing import Callable

import pytest
from model_bakery import baker

from sandbox.models import Candidate

__all__ = ['candidate']


@pytest.fixture
def candidate() -> Callable[..., Candidate]:
    def _candidate(**kwargs) -> Candidate:
        return baker.make('sandbox.Candidate', **kwargs)

    return _candidate
