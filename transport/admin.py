from django.contrib import admin
from .models import Route, Bus, Stop, RouteStop


admin.site.register(Route)
admin.site.register(Bus)
admin.site.register(Stop)
admin.site.register(RouteStop)