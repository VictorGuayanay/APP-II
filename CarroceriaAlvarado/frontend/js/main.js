$(document).ready(function() {
    // Manejo del formulario de login
    $(document).ready(function() {
    // ... (otro código que puedas tener al inicio de main.js) ...

    $('#loginForm').on('submit', function(event) {
        event.preventDefault();

        const username = $('#username').val().trim();
        const password = $('#password').val().trim();
        const messageDiv = $('#message'); // Asegúrate que este div exista en tu index.html

        // Limpiar mensajes anteriores
        messageDiv.text('').removeClass('error success');

        console.log('Datos enviados:', { username, password });

        if (!username || !password) {
            console.log('Faltan campos requeridos');
            messageDiv.text('Por favor, complete todos los campos.').addClass('error');
            return;
        }

        $.ajax({
            url: 'http://127.0.0.1:5000/login', // Asegúrate que el puerto de tu backend (app.py) sea correcto
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ username, password }),
            success: function(response) {
                console.log('Respuesta exitosa:', response); // LÍNEA IMPORTANTE PARA DEBUG
                
                if (response.token && response.rol) { // CONDICIÓN CRÍTICA
                    // Guardar el token y el rol en localStorage
                    localStorage.setItem('token', response.token);
                    localStorage.setItem('userRol', response.rol);

                    messageDiv.text('Login exitoso. Redirigiendo...').removeClass('error').addClass('success');

                    // Redirigir según el rol
                    if (response.rol === 'Administrador') { 
                        window.location.href = 'admin.html';
                    } else {
                        window.location.href = 'users.html';
                    }
                } else {
                    // Si la respuesta de éxito no contiene token o rol, es un estado inesperado.
                    console.error('Respuesta de login exitoso pero faltan datos (token/rol):', response); // LÍNEA IMPORTANTE PARA DEBUG
                    messageDiv.text('Error inesperado al procesar el login. Intente de nuevo.').removeClass('success').addClass('error');
                }
            },
            error: function(xhr, status, errorThrown) { // Cambié 'error' por 'errorThrown' para claridad
                console.log('Error en login AJAX detectado:');
                console.log('xhr:', xhr);
                console.log('status:', status); // ej: "error", "timeout", "parsererror"
                console.log('errorThrown:', errorThrown); // ej: "Unauthorized", "Not Found"

                let errorMsg = 'Error al iniciar sesión. Verifique sus credenciales o intente más tarde.'; // Mensaje por defecto mejorado

                if (xhr.responseJSON && xhr.responseJSON.error) {
                    // Si el backend envía un JSON con una propiedad "error" (ideal)
                    errorMsg = xhr.responseJSON.error; // Debería ser "Credenciales inválidas"
                } else if (xhr.responseText) {
                    // Si no hay responseJSON, intentar parsear responseText manualmente
                    // Esto puede ayudar si el Content-Type no fue application/json pero el cuerpo es JSON válido
                    try {
                        const parsedResponse = JSON.parse(xhr.responseText);
                        if (parsedResponse && parsedResponse.error) {
                            errorMsg = parsedResponse.error;
                        }
                    } catch (e) {
                        // Si no se puede parsear, o no tiene la propiedad error,
                        // el errorMsg por defecto se usará.
                        console.log("No se pudo parsear xhr.responseText como JSON o no contiene 'error':", xhr.responseText);
                    }
                }
                
                messageDiv.text(errorMsg).removeClass('success').addClass('error');
                console.log('Mensaje de error a mostrar:', errorMsg);
            }
        });
    });

    // Manejo del formulario de reset password
    $('#resetPassForm').on('submit', function(event) {
        event.preventDefault();

        const email = $('#email').val().trim();
        const messageDiv = $('#message');

        console.log('Datos enviados:', { email });

        if (!email) {
            console.log('Falta el correo');
            messageDiv.text('Por favor, ingrese un correo electrónico.').addClass('error');
            return;
        }

        $.ajax({
            url: 'http://127.0.0.1:5000/reset_password',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ email }),
            success: function(response) {
                console.log('Respuesta exitosa:', response);
                messageDiv.text('Instrucciones enviadas a su correo electrónico. Serás redirigido en 3 segundos...').removeClass('error').addClass('success');
                setTimeout(function() {
                    window.location.href = 'index.html';
                }, 3000);
            },
            error: function(xhr, status, error) {
                console.log('Error en reset_password:', xhr, status, error);
                const errorMsg = xhr.responseJSON?.error || 'Error al procesar la solicitud.';
                messageDiv.text(errorMsg).addClass('error');
            }
        });
    });

    // Manejo del formulario de nueva contraseña
    $('#newPassForm').on('submit', function(event) {
        event.preventDefault();

        const password = $('#password').val().trim();
        const confirmPassword = $('#confirm_password').val().trim();
        const messageDiv = $('#message');

        console.log('Datos enviados:', { password, confirmPassword });

        if (password !== confirmPassword) {
            console.log('Las contraseñas no coinciden');
            messageDiv.text('Las contraseñas no coinciden.').addClass('error');
            return;
        }

        // Obtener el token de la URL
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');

        if (!token) {
            console.log('Falta el token');
            messageDiv.text('Enlace inválido o expirado.').addClass('error');
            return;
        }

        $.ajax({
            url: 'http://127.0.0.1:8000/new_password',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ token, password }),
            success: function(response) {
                console.log('Respuesta exitosa:', response);
                messageDiv.text('Contraseña actualizada exitosamente. Serás redirigido en 3 segundos...').removeClass('error').addClass('success');
                setTimeout(function() {
                    window.location.href = 'index.html';
                }, 3000);
            },
            error: function(xhr, status, error) {
                console.log('Error en new_password:', xhr, status, error);
                const errorMsg = xhr.responseJSON?.error || 'Error al actualizar la contraseña.';
                messageDiv.text(errorMsg).addClass('error');
            }
        });
    });

    // Indicadores de robustez y coincidencia de contraseñas (para new_pass.html)
    $('#password').on('input', function() {
        const password = $(this).val();
        const strengthIndicator = $('#strengthIndicator');
        let strength = 'low';

        if (password.length > 11 && password.length <= 15) {
            strength = 'good';
            strengthIndicator.text('Fortaleza: Buena');
        } else if (password.length >= 6 && password.length <= 10) {
            strength = 'medium';
            strengthIndicator.text('Fortaleza: Media');
        } else if (password.length >= 0 && password.length <= 5) {
            strength = 'low';
            strengthIndicator.text('Fortaleza: Baja');
        }

        strengthIndicator.removeClass('strength-low strength-medium strength-good')
            .addClass('strength-' + strength);
        });
    });

    $('#confirm_password').on('input', function() {
        const password = $('#password').val();
        const confirmPassword = $(this).val();
        const confirmInput = $(this);

        if (password === confirmPassword && confirmPassword !== '') {
            confirmInput.removeClass('invalid').addClass('valid');
        } else {
            confirmInput.removeClass('valid').addClass('invalid');
        }
    });

    $('#logoutButton').on('click', function() { // Asume que tienes un botón con id="logoutButton"
        localStorage.removeItem('token');
        localStorage.removeItem('userRol');
        window.location.href = 'index.html';
    });
});
