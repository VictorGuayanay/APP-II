/**
 * Módulo de Logout Global
 * Maneja la funcionalidad de cerrar sesión de manera consistente
 */

function setupLogout() {
    // Buscar todos los botones de logout (pueden tener diferentes IDs)
    const logoutSelectors = [
        '#logoutButton',
        '#logoutButtonAdmin', 
        'a[href="#logout"]',
        '[data-logout]'
    ];

    logoutSelectors.forEach(selector => {
        $(document).on('click', selector, function(e) {
            e.preventDefault();
            performLogout();
        });
    });
}

function performLogout() {
    console.log('Iniciando logout...');
    
    // Limpiar localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('userRol');
    localStorage.removeItem('loggedInUsername');
    localStorage.clear();
    
    console.log('Session data cleared');
    
    // Redirigir al login
    window.location.href = 'index.html';
}

/**
 * Verificar si el usuario está autenticado
 * Si no, redirigir al login
 */
function checkAuthentication() {
    const token = localStorage.getItem('token');
    const userRol = localStorage.getItem('userRol');
    const username = localStorage.getItem('loggedInUsername');

    if (!token || !userRol || !username) {
        console.warn('No authentication found, redirecting to login');
        window.location.href = 'index.html';
        return false;
    }
    
    return true;
}

/**
 * Mostrar nombre de usuario en la página
 */
function displayUserInfo() {
    const username = localStorage.getItem('loggedInUsername');
    if (username) {
        $('#currentUserName').text(username);
        $('#loggedInUser').text(username);
    }
}

/**
 * Inicializar módulo al cargar la página
 */
$(document).ready(function() {
    // Verificar autenticación
    if (!window.location.pathname.includes('index.html') && 
        !window.location.pathname.includes('templates/login.html') &&
        !window.location.pathname.includes('registrer.html') &&
        !window.location.pathname.includes('reset_pass.html') &&
        !window.location.pathname.includes('new_pass.html')) {
        checkAuthentication();
    }
    
    // Mostrar info del usuario
    displayUserInfo();
    
    // Configurar logout
    setupLogout();
});
