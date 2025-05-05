$(document).ready(function() {
    $('#loginForm').on('submit', function(event) {
        event.preventDefault();

        const username = $('#username').val();
        const password = $('#password').val();
        const messageDiv = $('#message');

        $.ajax({
            url: 'http://127.0.0.1:5000/login',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ username, password }),
            success: function(response, status, xhr) {
                if (response.message) {
                    messageDiv.text('' + response.message).removeClass('message').addClass('message success');
                    // Redirigir al dashboard después de 1 segundo
                    setTimeout(function() {
                        window.location.href = 'dashboard.html';
                    }, 1000);
                } else if (response.error) {
                    messageDiv.text('' + response.error).removeClass('message success').addClass('message');
                }
            },
            error: function(xhr, status, error) {
                if (xhr.status === 0) {
                    messageDiv.text('Error al conectar con el servidor. Asegúrate de que el servidor esté activo.').removeClass('message success').addClass('message');
                } else {
                    messageDiv.text('Error inesperado: ' + xhr.statusText).removeClass('message success').addClass('message');
                }
            }
        });
    });
});