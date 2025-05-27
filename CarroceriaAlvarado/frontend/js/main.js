$(document).ready(function() {
    // Manejo del formulario de login
    $('#loginForm').on('submit', function(event) {
        event.preventDefault();

        const username = $('#username').val().trim();
        const password = $('#password').val().trim();
        const messageDiv = $('#message'); 

        messageDiv.text('').removeClass('error success'); // Limpiar mensajes anteriores

        console.log('Datos enviados para login:', { username, password });

        if (!username || !password) {
            console.log('Faltan campos requeridos para login');
            messageDiv.text('Por favor, complete todos los campos.').addClass('error');
            return;
        }

        $.ajax({
            url: 'http://127.0.0.1:5000/login', // API Flask en puerto 5000
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ username, password }),
            success: function(response) {
                console.log('Respuesta exitosa del login:', response);
                
                // Asegurarse que la respuesta contiene token, rol Y username
                if (response.token && response.rol && response.username) { 
                    localStorage.setItem('token', response.token);
                    localStorage.setItem('userRol', response.rol);
                    localStorage.setItem('loggedInUsername', response.username); // Guardar username

                    messageDiv.text('Login exitoso. Redirigiendo...').removeClass('error').addClass('success');

                    if (response.rol === 'Administrador') { 
                        window.location.href = 'admin.html';
                    } else {
                        window.location.href = 'users.html';
                    }
                } else {
                    console.error('Respuesta de login exitoso pero faltan datos (token/rol/username):', response);
                    messageDiv.text('Error inesperado al procesar el login. Intente de nuevo.').removeClass('success').addClass('error');
                }
            },
            error: function(xhr, status, errorThrown) {
                console.log('Error en login AJAX detectado:');
                console.log('xhr:', xhr);
                console.log('status:', status);
                console.log('errorThrown:', errorThrown);

                let errorMsg = 'Error al iniciar sesión. Verifique sus credenciales o intente más tarde.';

                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                } else if (xhr.responseText) {
                    try {
                        const parsedResponse = JSON.parse(xhr.responseText);
                        if (parsedResponse && parsedResponse.error) {
                            errorMsg = parsedResponse.error;
                        }
                    } catch (e) {
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

        messageDiv.text('').removeClass('error success');
        console.log('Datos enviados para reset password:', { email });

        if (!email) {
            console.log('Falta el correo para reset password');
            messageDiv.text('Por favor, ingrese un correo electrónico.').addClass('error');
            return;
        }

        $.ajax({
            url: 'http://127.0.0.1:5000/reset_password', // API Flask en puerto 5000
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ email }),
            success: function(response) {
                console.log('Respuesta exitosa de reset_password:', response);
                messageDiv.text(response.message || 'Instrucciones enviadas a su correo electrónico. Serás redirigido en 3 segundos...').removeClass('error').addClass('success');
                setTimeout(function() {
                    window.location.href = 'index.html';
                }, 3000);
            },
            error: function(xhr, status, errorThrown) { 
                console.log('Error en reset_password:', xhr, status, errorThrown);
                const errorMsg = xhr.responseJSON?.error || 'Error al procesar la solicitud de restablecimiento.';
                messageDiv.text(errorMsg).removeClass('success').addClass('error');
            }
        });
    });

    // Manejo del formulario de nueva contraseña
    $('#newPassForm').on('submit', function(event) {
        event.preventDefault();

        const password = $('#password').val().trim(); 
        const confirmPassword = $('#confirm_password').val().trim(); 
        const messageDiv = $('#message'); 

        messageDiv.text('').removeClass('error success');
        // No mostrar contraseñas en log de producción, solo un indicador de que se envían datos.
        console.log('Datos (sin contraseña) enviados para new password.');


        if (!password || !confirmPassword) {
            messageDiv.text('Por favor, complete ambos campos de contraseña.').addClass('error');
            return;
        }

        if (password !== confirmPassword) {
            console.log('Las contraseñas no coinciden en new_password');
            messageDiv.text('Las contraseñas no coinciden.').addClass('error');
            return;
        }

        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');

        if (!token) {
            console.log('Falta el token en new_password');
            messageDiv.text('Enlace inválido o expirado. No se encontró token.').addClass('error');
            return;
        }

        $.ajax({
            url: 'http://127.0.0.1:5000/new_password', // API Flask en puerto 5000
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ token, password }),
            success: function(response) {
                console.log('Respuesta exitosa de new_password:', response);
                messageDiv.text(response.message || 'Contraseña actualizada exitosamente. Serás redirigido en 3 segundos...').removeClass('error').addClass('success');
                setTimeout(function() {
                    window.location.href = 'index.html';
                }, 3000);
            },
            error: function(xhr, status, errorThrown) { 
                console.log('Error en new_password. Status:', status, 'Error:', errorThrown);
                console.log('xhr.responseText para new_password:', xhr.responseText); 
                const errorMsg = xhr.responseJSON?.error || 'Error al actualizar la contraseña.';
                messageDiv.text(errorMsg).removeClass('success').addClass('error');
            }
        });
    });

    // Indicadores de robustez y coincidencia de contraseñas 
    // (aplicable a páginas que tengan estos elementos, como new_pass.html o registrer.html)
    // Solo se adjuntan los eventos si los elementos existen en la página actual.
    if ($('#password').length > 0) { 
        $('#password').on('input', function() {
            const passwordVal = $(this).val(); 
            const strengthIndicator = $('#strengthIndicator'); 
            if (strengthIndicator.length > 0) {
                let strengthText = 'Baja';
                let strengthClass = 'low';

                if (passwordVal.length > 11 && passwordVal.length <= 15) {
                    strengthText = 'Buena';
                    strengthClass = 'good';
                } else if (passwordVal.length >= 6 && passwordVal.length <= 10) {
                    strengthText = 'Media';
                    strengthClass = 'medium';
                }
                strengthIndicator.text('Fortaleza: ' + strengthText);
                strengthIndicator.removeClass('strength-low strength-medium strength-good').addClass('strength-' + strengthClass);
            }
        });
    }

    if ($('#confirm_password').length > 0 && $('#password').length > 0) { 
        $('#confirm_password').on('input', function() {
            const mainPassword = $('#password').val(); 
            const confirmPasswordVal = $(this).val(); 
            const confirmInput = $(this);

            if (mainPassword === confirmPasswordVal && confirmPasswordVal !== '') {
                confirmInput.removeClass('invalid').addClass('valid');
            } else {
                confirmInput.removeClass('valid').addClass('invalid');
            }
        });
    }
    
    // Botón de Logout genérico (opcional, si tienes un botón con este ID en varias páginas)
    // Si tienes botones de logout con IDs específicos en admin.html y users.html, este puede no ser necesario.
    // Asegúrate de que si usas este, también elimine 'loggedInUsername'.
    /*
    $('#logoutButton').on('click', function() { 
        console.log("Botón de logout genérico clickeado");
        localStorage.removeItem('token');
        localStorage.removeItem('userRol');
        localStorage.removeItem('loggedInUsername'); // Importante limpiar el username también
        window.location.href = 'index.html';
    });
    */
});