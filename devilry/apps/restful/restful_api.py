from django import forms

from ..simplified.simplified_api import _require_metaattr
import fields



def _create_seachform(cls):
    class SearchForm(forms.Form):
        #format = fields.FormatField()
        query = forms.CharField(required=False)
        limit = fields.PositiveIntegerWithFallbackField(fallbackvalue=50)
        start = fields.PositiveIntegerWithFallbackField()
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=cls._meta.simplified._meta.ordering)
    cls.SearchForm = SearchForm


def _create_editform(cls):
    formfields = []
    model = cls._meta.simplified._meta.model
    for fieldname in cls._meta.simplified._meta.resultfields:
        if fieldname.endswith("__id"):
            formfields.append(fieldname[:-4])
        else:
            formfields.append(fieldname)
    class EditForm(forms.ModelForm):
        class Meta:
            model = cls._meta.simplified._meta.model
            fields = formfields
    cls.EditForm = EditForm


def restful_api(cls):
    meta = cls.Meta
    cls._meta = meta
    _require_metaattr(cls, 'simplified')
    _create_seachform(cls)
    _create_editform(cls)
    return cls