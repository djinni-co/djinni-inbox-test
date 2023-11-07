from django.db.models import Func, ExpressionWrapper
from django.db import models


class Epoch(Func):
    template = 'EXTRACT(epoch FROM %(expressions)s)::INTEGER'
    output_field = models.IntegerField()


