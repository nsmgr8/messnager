# -*- coding: utf-8 -*-

# django import
from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy as _

import models

class MemberForm(forms.ModelForm):
    class Meta:
        model = models.Member
        exclude = ('user', 'role_id')

class ManagerForm(forms.Form):
    member = forms.CharField(widget=forms.HiddenInput)
    role_id = forms.BooleanField(required=False)

    class Meta:
        model = models.Member
        include = ('role_id')

ManagerFormSet = formset_factory(ManagerForm)

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
        error_messages={'invalid': _('Only numbers allowed'),})# 'max_value': '<= 100', 'min_value': '>= 0'})

    class Meta:
        model = models.Meal
        exclude = ('date')

MealFormSet = formset_factory(MealForm)
