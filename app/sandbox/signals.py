from django.db.models.signals import pre_save
from django.dispatch import receiver
from typing import Type, Any
from .models import MessageThread
from .usecases import (
    find_similarities, COEFFICIENTS_VERSION_1, COEFFICIENTS_VERSION_2
)


@receiver(pre_save)
def calculate_matching_score(
        _: Type[MessageThread],
        instance: MessageThread,
        *args: list[Any],
        **kwargs: Any
):
    recruiter_id: int = instance.job.recruiter.id
    coefficient = (
        COEFFICIENTS_VERSION_1
        if recruiter_id % 2 == 0 else
        COEFFICIENTS_VERSION_2
    )

    score: float = find_similarities(
        instance.candidate, instance.job, coefficient
    )
    instance.matching_score = score
