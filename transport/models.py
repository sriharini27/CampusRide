from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Bus(models.Model):
    BUS_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Maintenance', 'Maintenance'),
        ('Inactive', 'Inactive'),
    ]

    BUS_TYPE_CHOICES = [
        ('Standard', 'Standard Bus'),
        ('AC', 'AC Express Bus'),
        ('Mini', 'Mini Bus'),
        ('Express', 'Super Express'),
    ]

    bus_number = models.CharField(max_length=30, unique=True, help_text="e.g. BUS-101")
    registration_number = models.CharField(max_length=30, unique=True, help_text="e.g. TN-72-AB-1234")
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField(default=50)
    bus_type = models.CharField(max_length=30, choices=BUS_TYPE_CHOICES, default='Standard')
    status = models.CharField(max_length=20, choices=BUS_STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Buses"
        ordering = ['bus_number']

    def __str__(self):
        return f"{self.bus_number} ({self.registration_number}) - Cap: {self.capacity}"

    @property
    def allocated_count(self):
        return self.routeallocation_set.filter(status='Active').count()

    @property
    def available_seats(self):
        return max(0, self.capacity - self.allocated_count)

    @property
    def is_full(self):
        return self.available_seats <= 0

    @property
    def occupancy_percentage(self):
        if self.capacity <= 0:
            return 0
        val = (self.allocated_count / self.capacity) * 100
        return round(val, 1)


class Route(models.Model):
    ROUTE_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    route_name = models.CharField(max_length=120)
    route_code = models.CharField(max_length=30, unique=True, help_text="e.g. R101")
    start_point = models.CharField(max_length=100)
    end_point = models.CharField(max_length=100)
    distance = models.DecimalField(max_digits=6, decimal_places=2, help_text="Distance in km")
    estimated_time = models.CharField(max_length=50, help_text="e.g. 45 Mins")
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True, related_name='routes')
    status = models.CharField(max_length=20, choices=ROUTE_STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['route_code']

    def __str__(self):
        return f"{self.route_code}: {self.route_name} ({self.start_point} to {self.end_point})"

    @property
    def allocated_student_count(self):
        return RouteAllocation.objects.filter(route=self, status='Active').count()


class Stop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    stop_name = models.CharField(max_length=100)
    location = models.CharField(max_length=150)
    stop_order = models.PositiveIntegerField(help_text="Sequence order of stop along the route")
    pickup_time = models.TimeField(help_text="Morning pickup time")
    drop_time = models.TimeField(help_text="Evening drop time")

    class Meta:
        ordering = ['route', 'stop_order']
        unique_together = ('route', 'stop_order')

    def __str__(self):
        return f"{self.route.route_code} - Stop #{self.stop_order}: {self.stop_name} ({self.pickup_time.strftime('%I:%M %p') if self.pickup_time else ''})"


class Student(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    DEPARTMENT_CHOICES = [
        ('Computer Science', 'Computer Science & Engineering'),
        ('Information Technology', 'Information Technology'),
        ('Electronics', 'Electronics & Communication Engg'),
        ('Electrical', 'Electrical & Electronics Engg'),
        ('Mechanical', 'Mechanical Engineering'),
        ('Civil', 'Civil Engineering'),
        ('Artificial Intelligence', 'Artificial Intelligence & Data Science'),
    ]

    YEAR_CHOICES = [
        ('1st Year', '1st Year'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
        ('4th Year', '4th Year'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=30, unique=True, help_text="e.g. 24CSE001")
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    year = models.CharField(max_length=20, choices=YEAR_CHOICES)
    section = models.CharField(max_length=10, default='A')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student_id']

    def __str__(self):
        return f"{self.student_id} - {self.full_name} ({self.department})"

    @property
    def active_allocation(self):
        return getattr(self, 'route_allocation', None)

    @property
    def latest_pass(self):
        return self.bus_passes.order_by('-created_at', '-id').first()


class TransportRegistration(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='transport_registration')
    preferred_route = models.ForeignKey(Route, on_delete=models.CASCADE)
    preferred_stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    registration_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Registration: {self.student.student_id} ({self.status})"


class BusPass(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Expired', 'Expired'),
    ]

    PAYMENT_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Not Required', 'Not Required'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='bus_passes')
    pass_number = models.CharField(max_length=50, unique=True, help_text="e.g. PASS-2026-001")
    application_date = models.DateField(auto_now_add=True)
    valid_from = models.DateField()
    valid_until = models.DateField()
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Paid')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Bus Passes"
        ordering = ['-application_date', '-id']

    def __str__(self):
        return f"{self.pass_number} - {self.student.full_name} ({self.status})"


class RouteAllocation(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='route_allocation')
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    allocated_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    class Meta:
        ordering = ['-allocated_date']

    def __str__(self):
        return f"Allocation: {self.student.student_id} -> {self.route.route_code} ({self.bus.bus_number})"