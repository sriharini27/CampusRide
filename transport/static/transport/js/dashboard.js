/* ==========================================================
   CampusRide - Dashboard Chart.js Integration
========================================================== */

function initAdminCharts(data) {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not loaded.');
        return;
    }

    // Chart 1: Students by Route
    const ctxRoute = document.getElementById('chartStudentsByRoute');
    if (ctxRoute && data.routeLabels) {
        new Chart(ctxRoute, {
            type: 'bar',
            data: {
                labels: JSON.parse(data.routeLabels),
                datasets: [{
                    label: 'Allocated Students',
                    data: JSON.parse(data.routeData),
                    backgroundColor: 'rgba(79, 70, 229, 0.75)',
                    borderColor: '#4f46e5',
                    borderWidth: 1.5,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { precision: 0 } }
                }
            }
        });
    }

    // Chart 2: Bus Capacity vs Allocated
    const ctxBus = document.getElementById('chartBusCapacity');
    if (ctxBus && data.busLabels) {
        new Chart(ctxBus, {
            type: 'bar',
            data: {
                labels: JSON.parse(data.busLabels),
                datasets: [
                    {
                        label: 'Total Capacity',
                        data: JSON.parse(data.busCapacity),
                        backgroundColor: 'rgba(203, 213, 225, 0.7)',
                        borderColor: '#94a3b8',
                        borderWidth: 1
                    },
                    {
                        label: 'Allocated Seats',
                        data: JSON.parse(data.busAllocated),
                        backgroundColor: 'rgba(16, 185, 129, 0.85)',
                        borderColor: '#059669',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, ticks: { precision: 0 } }
                }
            }
        });
    }

    // Chart 3: Bus Pass Application Status
    const ctxPass = document.getElementById('chartPassStatus');
    if (ctxPass && data.passLabels) {
        new Chart(ctxPass, {
            type: 'doughnut',
            data: {
                labels: JSON.parse(data.passLabels),
                datasets: [{
                    data: JSON.parse(data.passData),
                    backgroundColor: ['#f59e0b', '#10b981', '#ef4444', '#94a3b8'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    // Chart 4: Department-wise Distribution
    const ctxDept = document.getElementById('chartDepartment');
    if (ctxDept && data.deptLabels) {
        new Chart(ctxDept, {
            type: 'pie',
            data: {
                labels: JSON.parse(data.deptLabels),
                datasets: [{
                    data: JSON.parse(data.deptData),
                    backgroundColor: ['#6366f1', '#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }
}
