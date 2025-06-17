from django import forms
from .models import Voter, PARTY_CHOICES
from django.db.models import Q

YEARS = [("", "Any")] + [(y, y) for y in range(1920, 2007)]  # adjust as needed
SCORES = [("", "Any")] + [(i, i) for i in range(6)]

class VoterFilterForm(forms.Form):
    party          = forms.ChoiceField(choices=[("", "Any")] + PARTY_CHOICES, required=False)
    dob_min        = forms.ChoiceField(choices=YEARS, required=False, label="Born after")
    dob_max        = forms.ChoiceField(choices=YEARS, required=False, label="Born before")
    voter_score    = forms.ChoiceField(choices=SCORES, required=False)

    v20state   = forms.BooleanField(required=False, label="2020 State")
    v21town    = forms.BooleanField(required=False, label="2021 Town")
    v21primary = forms.BooleanField(required=False, label="2021 Primary")
    v22general = forms.BooleanField(required=False, label="2022 General")
    v23town    = forms.BooleanField(required=False, label="2023 Town")

    def apply_filters(self, qs):
        cd = self.cleaned_data

        if cd["party"]:
            qs = qs.filter(party__exact=cd["party"])

        if cd["dob_min"]:
            qs = qs.filter(dob__year__gte=int(cd["dob_min"]))
        if cd["dob_max"]:
            qs = qs.filter(dob__year__lte=int(cd["dob_max"]))

        if cd["voter_score"]:
            qs = qs.filter(voter_score=int(cd["voter_score"]))

        # turnout checkboxes
        for field in ["v20state","v21town","v21primary","v22general","v23town"]:
            if cd[field]:
                qs = qs.filter(**{field: True})

        return qs
