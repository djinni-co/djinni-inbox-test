from typing import Callable

import pytest
from model_bakery import baker

from sandbox.models import MessageThread

__all__ = ['message_thread_factory']


@pytest.fixture
def message_thread_factory(recruiter_factory, job_posting_factory, candidate_factory) -> Callable[..., MessageThread]:
    def _message_thread(**kwargs) -> MessageThread:
        kwargs['recruiter_factory'] = kwargs.pop('recruiter_factory', recruiter_factory())
        kwargs['job_posting'] = kwargs.pop('job_posting', job_posting_factory())
        kwargs['candidate_factory'] = kwargs.pop('candidate_factory', candidate_factory())
        return baker.make('sandbox.MessageThread', **kwargs)

    return _message_thread
