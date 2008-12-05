# -*- coding: utf-8 -*-

# django import
from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy as _

import models

class MessForm(forms.ModelForm):
    class Meta:
        model = models.Mess

class MemberFormAdmin(forms.ModelForm):
    class Meta:
        model = models.Member
        exclude = ('user', 'role_id', )

class MemberForm(forms.ModelForm):
    mess = forms.CharField(label=_('Mess'), widget=forms.HiddenInput)

    class Meta:
        model = models.Member
        exclude = ('user', 'role_id', )

class ManagerForm(forms.Form):
    member = forms.CharField(label=_('Member'), widget=forms.HiddenInput)
    role_id = forms.BooleanField(label=_('Role ID'), required=False)

    class Meta:
        model = models.Member
        include = ('role_id', )

ManagerFormSet = formset_factory(ManagerForm)

class MealForm(forms.Form):
    member = forms.CharField(label=_('Member'), widget=forms.HiddenInput)

    breakfast = forms.BooleanField(label=_('Breakfast'), required=False)
    lunch = forms.BooleanField(label=_('Lunch'), required=False)
    supper = forms.BooleanField(label=_('Supper'), required=False)

    extra = forms.FloatField(
        label=_('Extra'),
        widget=forms.TextInput(attrs={'size': '3'}),
        required=False,
        #max_value=100,
        #min_value=0,
        error_messages={'invalid': _('Only numbers allowed'),})# 'max_value': '<= 100', 'min_value': '>= 0'})

    class Meta:
        model = models.Meal
        exclude = ('date', )

MealFormSet = formset_factory(MealForm)

class BazaarForm(forms.ModelForm):
    amount = forms.FloatField(label=_('Amount'))

    class Meta:
        model = models.Bazaar
        exclude = ('date', 'member', )

class BazaarFormAdmin(forms.ModelForm):
    amount = forms.FloatField(label=_('Amount'))

    class Meta:
        model = models.Bazaar
        exclude = ('date')
