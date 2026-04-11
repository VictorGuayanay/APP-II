/**
 * dashboard-core.js
 * Centralized logic for all dashboard-style pages in Carrocería Alvarado.
 * Handles sidebar, authentication, logout, notifications, and user profile.
 */

(function() {
    // Utility to get the current script context or global variables
    const getApiBaseUrl = () => {
        return (window.CONFIG && window.CONFIG.API_BASE_URL) ? window.CONFIG.API_BASE_URL : 'http://127.0.0.1:5001';
    };

    /**
     * Auth Guard: Redirects to login if token is missing
     */
    const checkAuth = () => {
        const token = localStorage.getItem('token');
        const publicPages = ['index.html', 'register.html', 'reset_pass.html', 'new_pass.html'];
        const isPublic = publicPages.some(page => window.location.pathname.endsWith(page));

        if (!token && !isPublic) {
            console.warn('Dashboard Core: No token found. Redirecting to login.');
            window.location.href = 'index.html';
            return false;
        }
        return true;
    };

    /**
     * UI Initialization: Sidebar, User Profile, etc.
     */
    const initUI = () => {
        // Sidebar Toggle
        $('#sidebarCollapse').on('click', function() {
            $('#sidebar').toggleClass('active');
        });

        // Set User Name
        const username = localStorage.getItem('loggedInUsername');
        if (username) {
            $('#currentUserName').text(username);
        }

        // Logout logic
        $('#logoutButton, #logoutButtonAdmin').on('click', function(e) {
            e.preventDefault();
            if (confirm('¿Estás seguro de que deseas cerrar sesión?')) {
                localStorage.clear();
                window.location.href = 'index.html';
            }
        });
    };

    /**
     * Notifications Logic
     */
    const loadNotifications = () => {
        const token = localStorage.getItem('token');
        const $notificationCount = $('#notificationCount');
        const $notificationList = $('#notificationList');

        if (!token || !$notificationList.length) return;

        $.ajax({
            url: `${getApiBaseUrl()}/notificaciones`,
            method: 'GET',
            headers: { 'Authorization': 'Bearer ' + token },
            success: function(notificaciones) {
                $notificationList.empty();

                if (notificaciones && Array.isArray(notificaciones) && notificaciones.length > 0) {
                    $notificationCount.text(notificaciones.length).show();

                    notificaciones.forEach(function(notif) {
                        let iconClass = 'fa-info-circle';
                        if (notif.tipo === 'stock_bajo') {
                            iconClass = 'fa-warning text-warning';
                        } else if (notif.tipo === 'orden_vencimiento') {
                            iconClass = 'fa-calendar text-danger';
                        }

                        $notificationList.append(`
                            <li>
                                <a class="dropdown-item" href="#">
                                    <i class="fa ${iconClass}"></i> ${notif.mensaje}
                                </a>
                            </li>
                        `);
                    });
                } else {
                    $notificationCount.hide();
                    $notificationList.append('<li><span class="dropdown-item-text">No hay notificaciones nuevas.</span></li>');
                }
            },
            error: function(xhr) {
                console.error("Dashboard Core: Error loading notifications.", xhr.status);
                if (xhr.status === 401) {
                    localStorage.clear();
                    window.location.href = 'index.html';
                }
            }
        });
    };

    // Initialize everything on document ready
    $(document).ready(function() {
        if (checkAuth()) {
            initUI();
            loadNotifications();
            
            // Poll for notifications every 2 minutes
            setInterval(loadNotifications, 120000);
        }
    });

})();
