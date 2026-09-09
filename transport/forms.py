from django import forms
from django.contrib.auth.models import User
from .models import Student, BusPass


class StudentRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Student
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "student_id",
            "phone",
            "department",
            "year",
            "route",
        ]


class BusPassApplicationForm(forms.ModelForm):
    class Meta:
        model = BusPass
        fields = ["valid_from", "valid_until"]
        widgets = {
            "valid_from": forms.DateInput(attrs={"type": "date"}),
            "valid_until": forms.DateInput(attrs={"type": "date"}),
        }