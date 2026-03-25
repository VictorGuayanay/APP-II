// JavaScript para el Modal de Configuraciones
// Este script debe incluirse en todas las páginas que tengan el enlace de Configuración

// Cuando el modal de configuraciones se va a mostrar, cargar los valores actuales
$('#settingsModal').on('show.bs.modal', function () {
    console.log("Abriendo modal de configuraciones. Cargando valores actuales...");
    const token = localStorage.getItem('token');

    if (!token) {
        alert("Error de autenticación. Por favor, inicie sesión de nuevo.");
        var settingsModalEl = document.getElementById('settingsModal');
        if (settingsModalEl) {
            var settingsModalInstance = bootstrap.Modal.getInstance(settingsModalEl);
            if (settingsModalInstance) {
                settingsModalInstance.hide();
            }
        }
        window.location.href = 'index.html';
        return;
    }

    // Limpiar mensajes previos en el modal
    const mensajeDivModal = $('#settingsMessage');
    if (mensajeDivModal.length) {
        mensajeDivModal.text('').removeClass('alert alert-success alert-danger alert-info');
    }

    $.ajax({
        url: `${API_BASE_URL}/configuraciones`,
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + token },
        success: function (config) {
            console.log("Configuraciones actuales recibidas del backend:", config);
            if (config) {
                $('#settingResetTokenExpiry').val(config.reset_token_expiry_minutes);
                $('#settingMaxLoginAttempts').val(config.max_failed_login_attempts);
                $('#settingGlobalLowStockThreshold').val(config.global_low_stock_threshold);
            } else {
                console.error("Error: No se recibieron datos de configuración válidos del backend.");
                if (mensajeDivModal.length) {
                    mensajeDivModal.text('Error al cargar configuraciones: datos no válidos desde el servidor.').addClass('alert alert-danger');
                }
            }
        },
        error: function (xhr) {
            console.error("Error al cargar configuraciones:", xhr.status, xhr.responseText);
            if (mensajeDivModal.length) {
                mensajeDivModal.text(xhr.responseJSON?.error || 'Error al cargar configuraciones. Intente de nuevo más tarde.').addClass('alert alert-danger');
            }
            if (xhr.status === 401 || xhr.status === 403) {
                alert("Su sesión ha expirado o no tiene permisos. Será redirigido al login.");
                localStorage.removeItem('token');
                localStorage.removeItem('userRol');
                localStorage.removeItem('loggedInUsername');
                window.location.href = 'index.html';
            }
        }
    });
});

// Manejador para guardar las configuraciones
$('#settingsForm').on('submit', function (event) {
    event.preventDefault();
    const token = localStorage.getItem('token');

    if (!token) {
        alert("Error de autenticación. Por favor, inicie sesión de nuevo antes de guardar.");
        window.location.href = 'index.html';
        return;
    }

    const newSettings = {
        reset_token_expiry_minutes: parseInt($('#settingResetTokenExpiry').val(), 10),
        max_failed_login_attempts: parseInt($('#settingMaxLoginAttempts').val(), 10),
        global_low_stock_threshold: parseInt($('#settingGlobalLowStockThreshold').val(), 10)
    };

    console.log("Guardando nuevas configuraciones:", newSettings);
    const mensajeDivModal = $('#settingsMessage');
    if (mensajeDivModal.length) {
        mensajeDivModal.text('Guardando configuraciones...').removeClass('alert-success alert-danger alert-info').addClass('alert alert-info show');
    }

    // Validación simple en el frontend
    if (isNaN(newSettings.reset_token_expiry_minutes) || newSettings.reset_token_expiry_minutes <= 0 ||
        isNaN(newSettings.max_failed_login_attempts) || newSettings.max_failed_login_attempts <= 0 ||
        isNaN(newSettings.global_low_stock_threshold) || newSettings.global_low_stock_threshold < 0) {

        let validationErrorMsg = "Por favor, ingrese valores numéricos válidos. ";
        if (isNaN(newSettings.reset_token_expiry_minutes) || newSettings.reset_token_expiry_minutes <= 0) {
            validationErrorMsg += "La duración del token debe ser un número positivo. ";
        }
        if (isNaN(newSettings.max_failed_login_attempts) || newSettings.max_failed_login_attempts <= 0) {
            validationErrorMsg += "Los intentos de login deben ser un número positivo. ";
        }
        if (isNaN(newSettings.global_low_stock_threshold) || newSettings.global_low_stock_threshold < 0) {
            validationErrorMsg += "El umbral de stock bajo debe ser un número no negativo (0 o mayor).";
        }

        if (mensajeDivModal.length) {
            mensajeDivModal.text(validationErrorMsg).removeClass('alert-info').addClass('alert alert-danger');
        } else {
            alert(validationErrorMsg);
        }
        return;
    }

    $.ajax({
        url: `${API_BASE_URL}/configuraciones`,
        method: 'PUT',
        headers: {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        },
        data: JSON.stringify(newSettings),
        success: function (response) {
            console.log("Respuesta de guardar configuraciones:", response);
            if (mensajeDivModal.length) {
                mensajeDivModal.text(response.message || "Configuraciones guardadas exitosamente.").removeClass('alert-info alert-danger').addClass('alert alert-success');
            } else {
                alert(response.message || "Configuraciones guardadas exitosamente.");
            }
        },
        error: function (xhr) {
            console.error("Error al guardar configuraciones:", xhr.status, xhr.responseText);
            const errorText = xhr.responseJSON?.error || 'Error al guardar configuraciones. Intente de nuevo más tarde.';
            if (mensajeDivModal.length) {
                mensajeDivModal.text(errorText).removeClass('alert-info alert-success').addClass('alert alert-danger');
            } else {
                alert(errorText);
            }
            if (xhr.status === 401 || xhr.status === 403) {
                alert("Su sesión ha expirado o no tiene permisos. Será redirigido al login.");
                localStorage.removeItem('token');
                localStorage.removeItem('userRol');
                localStorage.removeItem('loggedInUsername');
                window.location.href = 'index.html';
            }
        }
    });
});
