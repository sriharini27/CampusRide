from django.db import models


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

class Student(models.Model):
    name = models.CharField(max_length=100)
    register_number = models.CharField(max_length=30, unique=True)
    department = models.CharField(max_length=100)
    year = models.IntegerField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.register_number + " - " + self.name


class BusPass(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    application_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    def __str__(self):
        return self.student.name + " - " + self.status