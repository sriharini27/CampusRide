from django.contrib import admin
from .models import Bus, Route, Stop, Student, TransportRegistration, BusPass, RouteAllocation


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('bus_number', 'registration_number', 'driver_name', 'driver_phone', 'capacity', 'allocated_count', 'available_seats', 'bus_type', 'status')
    search_fields = ('bus_number', 'registration_number', 'driver_name')
    list_filter = ('status', 'bus_type')
    ordering = ('bus_number',)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('route_code', 'route_name', 'start_point', 'end_point', 'distance', 'estimated_time', 'bus', 'status')
    search_fields = ('route_code', 'route_name', 'start_point', 'end_point')
    list_filter = ('status',)
    ordering = ('route_code',)


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ('stop_name', 'route', 'stop_order', 'location', 'pickup_time', 'drop_time')
    search_fields = ('stop_name', 'location', 'route__route_name', 'route__route_code')
    list_filter = ('route',)
    ordering = ('route', 'stop_order')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'email', 'phone', 'department', 'year', 'section', 'gender', 'created_at')
    search_fields = ('student_id', 'full_name', 'email', 'phone', 'department')
    list_filter = ('department', 'year', 'gender')
    ordering = ('student_id',)


@admin.register(TransportRegistration)
class TransportRegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'preferred_route', 'preferred_stop', 'registration_date', 'status')
    search_fields = ('student__student_id', 'student__full_name', 'preferred_route__route_code')
    list_filter = ('status', 'preferred_route')


@admin.register(BusPass)
class BusPassAdmin(admin.ModelAdmin):
    list_display = ('pass_number', 'student', 'route', 'stop', 'valid_from', 'valid_until', 'status', 'payment_status', 'application_date')
    search_fields = ('pass_number', 'student__student_id', 'student__full_name', 'route__route_code')
    list_filter = ('status', 'payment_status', 'route')
    ordering = ('-application_date',)


@admin.register(RouteAllocation)
class RouteAllocationAdmin(admin.ModelAdmin):
    list_display = ('student', 'route', 'bus', 'stop', 'allocated_date', 'status')
    search_fields = ('student__student_id', 'student__full_name', 'route__route_code', 'bus__bus_number')
    list_filter = ('status', 'route', 'bus')
    ordering = ('-allocated_date',)