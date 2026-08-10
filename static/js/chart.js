document.addEventListener("DOMContentLoaded", function () {

    console.log("Admin dashboard chart.js loaded");


    // ==========================================
    // BOOKING STATISTICS
    // ==========================================

    const bookingCanvas = document.getElementById("bookingChart");

    if (bookingCanvas) {

        const approved =
            Number(window.bookingStats?.approved || 0);

        const pending =
            Number(window.bookingStats?.pending || 0);

        const rejected =
            Number(window.bookingStats?.rejected || 0);


        new Chart(bookingCanvas, {

            type: "doughnut",

            data: {

                labels: [
                    "Approved",
                    "Pending",
                    "Rejected"
                ],

                datasets: [

                    {

                        data: [
                            approved,
                            pending,
                            rejected
                        ],

                        backgroundColor: [

                            "#22c55e",
                            "#eab308",
                            "#ef4444"

                        ],

                        borderWidth: 0,

                        hoverOffset: 8

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                cutout: "65%",

                plugins: {

                    legend: {

                        position: "bottom",

                        labels: {

                            padding: 20,

                            usePointStyle: true

                        }

                    },

                    tooltip: {

                        enabled: true

                    }

                }

            }

        });

    }


    // ==========================================
    // VEHICLE STATISTICS
    // ==========================================

    const vehicleCanvas =
        document.getElementById("vehicleChart");


    if (vehicleCanvas) {

        const available =
            Number(window.vehicleStats?.available || 0);

        const booked =
            Number(window.vehicleStats?.booked || 0);

        const pending =
            Number(window.vehicleStats?.pending || 0);

        const approved =
            Number(window.vehicleStats?.approved || 0);


        new Chart(vehicleCanvas, {

            type: "doughnut",

            data: {

                labels: [

                    "Available",
                    "Booked",
                    "Pending Approval",
                    "Approved"

                ],

                datasets: [

                    {

                        data: [

                            available,
                            booked,
                            pending,
                            approved

                        ],

                        backgroundColor: [

                            "#22c55e",
                            "#ef4444",
                            "#f59e0b",
                            "#3b82f6"

                        ],

                        borderWidth: 0,

                        hoverOffset: 8

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                cutout: "65%",

                plugins: {

                    legend: {

                        position: "bottom",

                        labels: {

                            padding: 20,

                            usePointStyle: true

                        }

                    },

                    tooltip: {

                        enabled: true

                    }

                }

            }

        });

    }

});