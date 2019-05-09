import datetime

from django import forms
from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker

class datetimeform(forms.Form):
    Date_From = forms.DateTimeField(
        widget=DateTimePicker(
            options={
                'minDate': (
                    datetime.date.today() + datetime.timedelta(days=1)
                ).strftime(
                    '%Y-%m-%d'
                ),  # Tomorrow
                'useCurrent': True,
                'collapse': False,
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
    )

    Date_To = forms.DateTimeField(
        widget=DateTimePicker(
            options={
                'minDate': (
                    datetime.date.today() + datetime.timedelta(days=1)
                ).strftime(
                    '%Y-%m-%d'
                ),  # Tomorrow
                'useCurrent': True,
                'collapse': False,
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
    )
