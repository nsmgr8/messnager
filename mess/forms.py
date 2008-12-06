# -*- coding: utf-8 -*-

# The MIT License
# 
# Copyright (c) 2008 M. Nasimul Haque
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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
