from django import forms
from django.db.models import Count

from .models import JobPosting


LANG_CHOICES = (
    (1, "Basic"),
    (2, "Pre-Intermediate"),
    (3, "Intermediate"),
    (4, "Upper-Intermediate"),
    (5, "Fluent"),
)


class ThreadForm(forms.Form):
    english_level = forms.ChoiceField(choices=LANG_CHOICES, label="Minimum english level", required=False)
    job = forms.ModelChoiceField(JobPosting.objects.none(), required=False)

    def __init__(self, *args, recruiter, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["job"].queryset = (
            JobPosting.objects.filter(recruiter=recruiter)
            .annotate(applies_count=Count("messagethread"))
            .order_by("-published")
        )
        self.fields["job"].label_from_instance = (
            lambda job: f"{job.primary_keyword} | {job.position} | Applicants: {job.applies_count}"
        )
        self.fields["job"].widget.attrs = {"style": "width:200px"}
