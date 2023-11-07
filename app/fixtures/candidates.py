from typing import Callable

import pytest
from model_bakery import baker

from sandbox.models import Candidate

__all__ = ['candidate_factory']


@pytest.fixture
def candidate_factory() -> Callable[..., Candidate]:
    def _candidate(**kwargs) -> Candidate:
        return baker.make('sandbox.Candidate', **kwargs)

    return _candidate
