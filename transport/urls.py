from django.urls import path
from . import views


urlpatterns = [

    path("", views.dashboard, name="dashboard"),

    # Route Management
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

    # Bus Management
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

    # Stop Management
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
    # Route Allocation
path(
    "route-allocation/",
    views.route_allocation,
    name="route_allocation"
),

path(
    "bus-capacity/",
    views.bus_capacity,
    name="bus_capacity"
),
    # Student Registration
    path(
        "students/",
        views.student_list,
        name="student_list"
    ),

    path(
        "students/add/",
        views.student_create,
        name="student_create"
    ),

    # Bus Pass Management
    path(
        "buspasses/",
        views.buspass_list,
        name="buspass_list"
    ),

    path(
        "buspasses/add/",
        views.buspass_create,
        name="buspass_create"
    ),
]