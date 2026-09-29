from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Student, Bus, Route, Stop, BusPass, RouteAllocation, TransportRegistration


class StudentRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username for login'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = Student
        fields = [
            'student_id', 'full_name', 'email', 'phone',
            'department', 'year', 'section', 'gender',
            'address', 'emergency_contact'
        ]
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 24CSE001'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A / B / C'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Full Residential Address'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency Contact Number'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Student.objects.filter(email=email).exists() or User.objects.filter(email=email).exists():
            raise ValidationError("Email is already registered.")
        return email

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if Student.objects.filter(student_id=student_id).exists():
            raise ValidationError("Student ID already exists.")
        return student_id

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        confirm_pwd = cleaned_data.get('confirm_password')

        if pwd and confirm_pwd and pwd != confirm_pwd:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'full_name', 'email', 'phone', 'department',
            'year', 'section', 'gender', 'address', 'emergency_contact'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = ['bus_number', 'registration_number', 'driver_name', 'driver_phone', 'capacity', 'bus_type', 'status']
        widgets = {
            'bus_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. BUS-101'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. TN-72-AB-1234'}),
            'driver_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Driver Full Name'}),
            'driver_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Driver Phone'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'bus_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')
        if capacity is not None and capacity <= 0:
            raise ValidationError("Capacity must be greater than 0.")
        return capacity


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['route_name', 'route_code', 'start_point', 'end_point', 'distance', 'estimated_time', 'bus', 'status']
        widgets = {
            'route_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Route Name'}),
            'route_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. R101'}),
            'start_point': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Start Location'}),
            'end_point': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destination Location'}),
            'distance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'estimated_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 45 Mins'}),
            'bus': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class StopForm(forms.ModelForm):
    class Meta:
        model = Stop
        fields = ['route', 'stop_name', 'location', 'stop_order', 'pickup_time', 'drop_time']
        widgets = {
            'route': forms.Select(attrs={'class': 'form-select'}),
            'stop_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Stop Name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Landmark / Area'}),
            'stop_order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'pickup_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'drop_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def clean_stop_order(self):
        stop_order = self.cleaned_data.get('stop_order')
        if stop_order is not None and stop_order <= 0:
            raise ValidationError("Stop order must be positive integer.")
        return stop_order


class BusPassApplicationForm(forms.ModelForm):
    class Meta:
        model = BusPass
        fields = ['route', 'stop', 'valid_from', 'valid_until']
        widgets = {
            'route': forms.Select(attrs={'class': 'form-select', 'id': 'id_route'}),
            'stop': forms.Select(attrs={'class': 'form-select', 'id': 'id_stop'}),
            'valid_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        route = cleaned_data.get('route')
        stop = cleaned_data.get('stop')
        valid_from = cleaned_data.get('valid_from')
        valid_until = cleaned_data.get('valid_until')

        if valid_from and valid_until and valid_until < valid_from:
            self.add_error('valid_until', "Valid until date must be after or equal to valid from date.")

        if route and stop:
            if stop.route_id != route.id:
                self.add_error('stop', f"The stop '{stop.stop_name}' does not belong to the selected route '{route.route_name}'.")

            # Check capacity if bus assigned
            if route.bus:
                bus = route.bus
                if bus.is_full:
                    raise ValidationError(f"Bus capacity is full for Route {route.route_code} ({bus.bus_number}). Applications temporarily paused.")

        return cleaned_data


class RouteAllocationForm(forms.ModelForm):
    class Meta:
        model = RouteAllocation
        fields = ['student', 'route', 'bus', 'stop', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'route': forms.Select(attrs={'class': 'form-select', 'id': 'alloc_route'}),
            'bus': forms.Select(attrs={'class': 'form-select', 'id': 'alloc_bus'}),
            'stop': forms.Select(attrs={'class': 'form-select', 'id': 'alloc_stop'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        route = cleaned_data.get('route')
        bus = cleaned_data.get('bus')
        stop = cleaned_data.get('stop')

        if stop and route and stop.route_id != route.id:
            self.add_error('stop', "Selected stop does not belong to the selected route.")

        if bus and bus.is_full:
            # Check if this student is already allocated to this bus
            existing_alloc = RouteAllocation.objects.filter(student=student, bus=bus, status='Active').exists()
            if not existing_alloc:
                raise ValidationError(f"Allocation failed: Bus '{bus.bus_number}' capacity is full ({bus.allocated_count}/{bus.capacity}).")

        return cleaned_data


class PassReviewForm(forms.Form):
    ACTION_CHOICES = [
        ('Approve', 'Approve Application'),
        ('Reject', 'Reject Application'),
    ]
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.RadioSelect(attrs={'class': 'form-check-input'}))
    payment_status = forms.ChoiceField(
        choices=BusPass.PAYMENT_CHOICES,
        initial='Paid',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Remarks / Reason (Optional)'})
    )