/* ==========================================================
   CampusRide - Main JavaScript Module
========================================================== */

document.addEventListener('DOMContentLoaded', function () {
    // Dynamic Route -> Stop Selection Handling
    const routeSelect = document.getElementById('id_route');
    const stopSelect = document.getElementById('id_stop');

    if (routeSelect && stopSelect) {
        routeSelect.addEventListener('change', function () {
            const routeId = this.value;
            if (!routeId) {
                stopSelect.innerHTML = '<option value="">-- Select Stop --</option>';
                return;
            }

            stopSelect.innerHTML = '<option value="">Loading stops...</option>';

            fetch(`/api/route-stops/${routeId}/`)
                .then(response => response.json())
                .then(data => {
                    stopSelect.innerHTML = '<option value="">-- Select Stop --</option>';
                    if (data.stops && data.stops.length > 0) {
                        data.stops.forEach(stop => {
                            const option = document.createElement('option');
                            option.value = stop.id;
                            option.textContent = `${stop.stop_name} (${stop.location}) - Pickup: ${stop.pickup_time}`;
                            stopSelect.appendChild(option);
                        });
                    } else {
                        stopSelect.innerHTML = '<option value="">No stops found for this route</option>';
                    }
                })
                .catch(error => {
                    console.error('Error fetching stops:', error);
                    stopSelect.innerHTML = '<option value="">Error loading stops</option>';
                });
        });
    }

    // Auto dismiss Django alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Function to print bus pass or report
function printPass() {
    window.print();
}
