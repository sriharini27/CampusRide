from django.db import models
from django.contrib.auth.models import User


class Route(models.Model):
    route_number = models.CharField(max_length=20, unique=True)
    route_name = models.CharField(max_length=100)
    start_point = models.CharField(max_length=100)
    end_point = models.CharField(max_length=100)

    def __str__(self):
        return self.route_number + " - " + self.route_name


class Stop(models.Model):
    stop_name = models.CharField(max_length=100)
    location = models.CharField(max_length=150)

    def __str__(self):
        return self.stop_name


class Bus(models.Model):
    bus_number = models.CharField(max_length=30, unique=True)
    registration_number = models.CharField(max_length=30, unique=True)
    capacity = models.PositiveIntegerField()

    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.bus_number


class RouteStop(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE
    )
    stop = models.ForeignKey(
        Stop,
        on_delete=models.CASCADE
    )
    stop_order = models.PositiveIntegerField()

    class Meta:
        ordering = ['stop_order']

    def __str__(self):
        return self.route.route_number + " - " + self.stop.stop_name


# =========================
# MODULE 2
# Student Registration
# =========================

class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    student_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    year = models.PositiveIntegerField()

    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.student_id + " - " + self.user.get_full_name()


# =========================
# MODULE 2
# Bus Pass Management
# =========================

class BusPass(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE
    )

    applied_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    valid_from = models.DateField(
        null=True,
        blank=True
    )

    valid_until = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.student.student_id + " - " + self.status