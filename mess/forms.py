# -*- coding: utf-8 -*-
# django import
from django import forms

import models

class MemberForm(forms.ModelForm):
    role_id = forms.ChoiceField(label="অনুমোদন", widget=forms.Select, choices=models.role_list)

    class Meta:
        model = models.Member
        exclude = ('user')

class MealForm(forms.Form):
    member = forms.CharField(widget=forms.HiddenInput)
    breakfast = forms.BooleanField(required=False)
    lunch = forms.BooleanField(required=False)
    supper = forms.BooleanField(required=False)
    extra = forms.FloatField(
        widget=forms.TextInput(attrs={'size': '3'}),
        required=False,
        #max_value=100,
        #min_value=0,
        error_messages={'invalid': 'শুধু সংখ্যা প্রযোজ্য',})# 'max_value': '<= 100', 'min_value': '>= 0'})

    class Meta:
        model = models.Meal
        exclude = ('date')
