from typing import Callable

import pytest
from model_bakery import baker

from sandbox.models import MessageThread

__all__ = ['message_thread']


@pytest.fixture
def message_thread(recruiter, job_posting, candidate) -> Callable[..., MessageThread]:
    def _message_thread(**kwargs) -> MessageThread:
        kwargs['recruiter'] = kwargs.pop('recruiter', recruiter())
        kwargs['job_posting'] = kwargs.pop('job_posting', job_posting())
        kwargs['candidate'] = kwargs.pop('candidate', candidate())
        return baker.make('sandbox.MessageThread', **kwargs)

    return _message_thread
