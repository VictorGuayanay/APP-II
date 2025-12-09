/* ========================================
   TOAST NOTIFICATIONS SYSTEM
   Sistema de notificaciones JavaScript
   ======================================== */

/**
 * Muestra un toast notification
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo: 'success', 'error', 'warning', 'info'
 * @param {number} duration - Duración en ms (default: 3000)
 */
function showToast(message, type = 'info', duration = 3000) {
    // Crear contenedor si no existe
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    // Generar ID único para el toast
    const toastId = 'toast-' + Date.now();

    // Iconos según el tipo
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };

    // Títulos según el tipo
    const titles = {
        success: 'Éxito',
        error: 'Error',
        warning: 'Advertencia',
        info: 'Información'
    };

    // Crear el toast HTML
    const toastHTML = `
        <div id="${toastId}" class="toast toast-${type}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="fa ${icons[type]} toast-icon"></i>
                <strong class="me-auto">${titles[type]}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
            ${duration > 0 ? '<div class="toast-progress"></div>' : ''}
        </div>
    `;

    // Agregar al contenedor
    container.insertAdjacentHTML('beforeend', toastHTML);

    // Obtener el elemento del toast
    const toastElement = document.getElementById(toastId);
    const bsToast = new bootstrap.Toast(toastElement, {
        autohide: duration > 0,
        delay: duration
    });

    // Mostrar el toast
    bsToast.show();

    // Eliminar del DOM después de ocultarse
    toastElement.addEventListener('hidden.bs.toast', function () {
        toastElement.remove();
    });

    return bsToast;
}

/**
 * Atajos para tipos específicos de toast
 */
function showSuccessToast(message, duration = 3000) {
    return showToast(message, 'success', duration);
}

function showErrorToast(message, duration = 4000) {
    return showToast(message, 'error', duration);
}

function showWarningToast(message, duration = 3500) {
    return showToast(message, 'warning', duration);
}

function showInfoToast(message, duration = 3000) {
    return showToast(message, 'info', duration);
}

/**
 * Toast de confirmación con botones
 * @param {string} message - Mensaje
 * @param {function} onConfirm - Callback al confirmar
 * @param {function} onCancel - Callback al cancelar
 */
function showConfirmToast(message, onConfirm, onCancel) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toastId = 'toast-' + Date.now();
    const toastHTML = `
        <div id="${toastId}" class="toast toast-warning" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="fa fa-question-circle toast-icon"></i>
                <strong class="me-auto">Confirmación</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
                <div class="mt-2 pt-2 border-top">
                    <button type="button" class="btn btn-sm btn-primary me-2" id="${toastId}-confirm">Confirmar</button>
                    <button type="button" class="btn btn-sm btn-secondary" id="${toastId}-cancel">Cancelar</button>
                </div>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = document.getElementById(toastId);
    const bsToast = new bootstrap.Toast(toastElement, { autohide: false });
    bsToast.show();

    // Event listeners para botones
    document.getElementById(`${toastId}-confirm`).addEventListener('click', function() {
        if (onConfirm) onConfirm();
        bsToast.hide();
    });

    document.getElementById(`${toastId}-cancel`).addEventListener('click', function() {
        if (onCancel) onCancel();
        bsToast.hide();
    });

    toastElement.addEventListener('hidden.bs.toast', function () {
        toastElement.remove();
    });

    return bsToast;
}
