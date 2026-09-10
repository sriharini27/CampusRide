from django import forms
from .models import Student, BusPass


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["name", "register_number", "department", "year", "phone"]


class BusPassForm(forms.ModelForm):
    class Meta:
        model = BusPass
        fields = ["student", "route"]