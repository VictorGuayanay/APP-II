$(document).ready(function() {
    // Manejo del formulario de login
    $('#loginForm').on('submit', function(event) {
        event.preventDefault();

        const username = $('#username').val().trim();
        const password = $('#password').val().trim();
        const messageDiv = $('#message'); 

        messageDiv.text('').removeClass('error success'); // Limpiar mensajes anteriores

        if (!username || !password) {
            console.log('Faltan campos requeridos para login');
            messageDiv.text('Por favor, complete todos los campos.').addClass('error');
            return;
        }

        console.log('Datos enviados para login:', { username, password });

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
            url: 'http://127.0.0.1:5000/reset_password',
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
            url: 'http://127.0.0.1:5000/new_password', 
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
    
    function cargarNotificaciones() {
        console.log("cargarNotificaciones() - Iniciando carga de notificaciones...");
        const token = localStorage.getItem('token');
        const $notificationCount = $('#notificationCount'); 
        const $notificationList = $('#notificationList');   

      
        if (!token) {
            console.error("cargarNotificaciones() - No hay token. No se puede llamar a la API.");
            return;
        }

        $.ajax({
            url: 'http://127.0.0.1:5000/notificaciones',
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(notificaciones) {
                console.log("cargarNotificaciones() - Notificaciones recibidas:", notificaciones);
                $notificationList.empty(); 

                if (notificaciones && Array.isArray(notificaciones) && notificaciones.length > 0) {
                    // Hay notificaciones, actualizar contador y mostrarlo
                    $notificationCount.text(notificaciones.length).show();

                    // Poblar la lista desplegable
                    notificaciones.forEach(function(notif) {
                        let iconClass = 'fa-info-circle'; // Icono por defecto
                        if (notif.tipo === 'stock_bajo') {
                            iconClass = 'fa-warning text-warning'; // Icono de advertencia para stock bajo
                        } else if (notif.tipo === 'orden_vencimiento') {
                            iconClass = 'fa-calendar text-danger'; // Icono de calendario para órdenes por vencer
                        }

                        const notificacionHtml = `
                            <li>
                                <a class="dropdown-item" href="#">
                                    <i class="fa ${iconClass}"></i> ${notif.mensaje}
                                </a>
                            </li>
                        `;
                        $notificationList.append(notificacionHtml);
                    });

                } else {
                    // No hay notificaciones
                    console.log("cargarNotificaciones() - No hay notificaciones nuevas.");
                    $notificationCount.hide(); // Ocultar el contador
                    $notificationList.append('<li><span class="dropdown-item-text">No hay notificaciones nuevas.</span></li>');
                }
            },
            error: function(xhr, status, error) {
                console.error("cargarNotificaciones() - Error al cargar notificaciones. Status:", xhr.status, "Response:", xhr.responseText);
                $notificationCount.hide();
                $notificationList.empty().append('<li><span class="dropdown-item-text text-danger">Error al cargar notificaciones.</span></li>');
                // No redirigimos aquí para no interrumpir al usuario, a menos que sea un error de autenticación
                if (xhr.status === 401) { //no autorizado
                    window.location.reload();
                }
            }
        });
    }

    function cargarRecursosEstimados(idOrden) {
        const token = localStorage.getItem('token');
        if (!token) return;

        $.ajax({
            url: `http://127.0.0.1:5000/ordenes-trabajo/${idOrden}/recursos-estimados`,
            method: 'GET',
            headers: { 'Authorization': 'Bearer ' + token },
            success: function(response) {
                $('#recursosEstimados').removeClass('hidden');
                $('#personalEstimado').text(response.personal_estimado);
                $('#horasEstimadas').text(response.horas_estimadas);
                $('#descOrden').text(response.descripcion);
            },
            error: function(xhr, status, error) {
                console.error('Error al cargar recursos estimados:', error);
            }
        });
    }

    // Llamada después de crear una orden
    $('#ordenForm').on('submit', function(event) {
        event.preventDefault();

        const id_empleado = $('#empleado').val();
        const id_cliente = $('#cliente').val();
        const fecha_inicio = $('#fechaInicio').val();
        const fecha_fin = $('#fechaFin').val();
        const descripcion = $('#descripcion').val();

        if (!id_empleado || !id_cliente || !fecha_inicio || !descripcion) {
            alert('Por favor, complete todos los campos requeridos.');
            return;
        }

        const token = localStorage.getItem('token');
        if (!token) {
            alert('Debe iniciar sesión para crear una orden.');
            return;
        }

        $.ajax({
            url: 'http://127.0.0.1:5000/ordenes-trabajo',
            method: 'POST',
            contentType: 'application/json',
            headers: { 'Authorization': 'Bearer ' + token },
            data: JSON.stringify({
                id_empleado, id_cliente, fecha_inicio, fecha_fin, descripcion
            }),
            success: function(response) {
                alert('Orden creada exitosamente.');
                if (response.id_orden_creada) {
                    cargarRecursosEstimados(response.id_orden_creada);
                }
            },
            error: function(xhr, status, error) {
                alert('Error al crear la orden: ' + (xhr.responseJSON?.error || error));
            }
        });
    });

    const urlParams = new URLSearchParams(window.location.search);
    const idOrden = urlParams.get('id_orden');
    if (idOrden) {
        cargarRecursosEstimados(idOrden);
    }



});