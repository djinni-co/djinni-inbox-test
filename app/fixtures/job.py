from typing import Callable

import pytest
from model_bakery import baker

from sandbox.models import Recruiter, JobPosting

__all__ = ['recruiter_factory', 'job_posting_factory']


@pytest.fixture
def recruiter_factory() -> Callable[..., Recruiter]:
    def _recruiter(**kwargs) -> Recruiter:
        return baker.make('sandbox.Recruiter', **kwargs)

    return _recruiter


@pytest.fixture
def job_posting_factory(recruiter_factory) -> Callable[..., JobPosting]:
    def _job_posting(**kwargs) -> JobPosting:
        kwargs['recruiter'] = kwargs.pop('recruiter', recruiter_factory())
        return baker.make('sandbox.JobPosting', **kwargs)

    return _job_posting
