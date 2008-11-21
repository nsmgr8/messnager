# django import
from django import newforms as forms
from google.appengine.ext.db import djangoforms

import models

class MemberForm(djangoforms.ModelForm):
    role_id = forms.ChoiceField(label="Role",
                                widget=forms.Select,
                                choices=models.role_list)#[('0','Member'),('1','Manager')])

    class Meta:
        model = models.Member
        exclude = ('user')

class MealForm(djangoforms.ModelForm):
    member = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = models.Meal
        exclude = ('date')
