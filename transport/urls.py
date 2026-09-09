from django.urls import path
from . import views


urlpatterns = [

    path("", views.dashboard, name="dashboard"),

    path("routes/", views.route_list, name="route_list"),

    path(
        "routes/add/",
        views.route_create,
        name="route_create"
    ),

    path(
        "routes/edit/<int:id>/",
        views.route_update,
        name="route_update"
    ),

    path(
        "routes/delete/<int:id>/",
        views.route_delete,
        name="route_delete"
    ),
    path("buses/", views.bus_list, name="bus_list"),

path(
    "buses/add/",
    views.bus_create,
    name="bus_create"
),

path(
    "buses/edit/<int:id>/",
    views.bus_update,
    name="bus_update"
),

path(
    "buses/delete/<int:id>/",
    views.bus_delete,
    name="bus_delete"
),
 path("stops/", views.stop_list, name="stop_list"),

    path(
        "stops/add/",
        views.stop_create,
        name="stop_create"
    ),

    path(
        "stops/edit/<int:id>/",
        views.stop_update,
        name="stop_update"
    ),

    path(
        "stops/delete/<int:id>/",
        views.stop_delete,
        name="stop_delete"
    ),
    # Route - Stop Management

path(
    "route-stops/",
    views.route_stop_list,
    name="route_stop_list"
),

path(
    "route-stops/add/",
    views.route_stop_create,
    name="route_stop_create"
),

    # Module 2 - Student Registration

    path(
        "student/register/",
        views.student_register,
        name="student_register"
    ),

    path(
    "student/login/",
    views.student_login,
    name="student_login"
),

path(
    "student/dashboard/",
    views.student_dashboard,
    name="student_dashboard"
),

path(
    "student/bus-pass/apply/",
    views.apply_bus_pass,
    name="apply_bus_pass"
),

path(
    "student/logout/",
    views.student_logout,
    name="student_logout"
),
# Module 3 - Route Allocation & Dashboard

path(
    "route-allocation/",
    views.route_allocation,
    name="route_allocation"
),

path(
    "transport-dashboard/",
    views.transport_dashboard,
    name="transport_dashboard"
),
]