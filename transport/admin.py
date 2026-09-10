from django.contrib import admin
from .models import Route, Bus, Stop, RouteStop,Student,BusPass


admin.site.register(Route)
admin.site.register(Bus)
admin.site.register(Stop)
admin.site.register(RouteStop)
admin.site.register(Student)
admin.site.register(BusPass)