/* ========================================
   LOADING STATES - Carrocería Alvarado
   Sistema de estados de carga para botones
   ======================================== */

/**
 * Muestra estado de carga en un botón
 * @param {string|jQuery} button - Selector o elemento jQuery del botón
 * @param {string} loadingText - Texto a mostrar durante la carga (opcional)
 */
function setButtonLoading(button, loadingText = 'Cargando...') {
    const $btn = $(button);

    // Guardar estado original
    $btn.data('original-html', $btn.html());
    $btn.data('original-disabled', $btn.prop('disabled'));

    // Aplicar estado de carga
    $btn.prop('disabled', true);
    $btn.addClass('btn-loading');

    // HTML con spinner
    const spinnerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        ${loadingText}
    `;

    $btn.html(spinnerHTML);
}

/**
 * Restaura el estado original del botón
 * @param {string|jQuery} button - Selector o elemento jQuery del botón
 */
function resetButtonLoading(button) {
    const $btn = $(button);

    // Restaurar estado original
    const originalHTML = $btn.data('original-html');
    const originalDisabled = $btn.data('original-disabled');

    if (originalHTML) {
        $btn.html(originalHTML);
    }

    $btn.prop('disabled', originalDisabled || false);
    $btn.removeClass('btn-loading');

    // Limpiar datos
    $btn.removeData('original-html');
    $btn.removeData('original-disabled');
}

/**
 * Ejecuta una función con loading state en un botón
 * @param {string|jQuery} button - Selector o elemento jQuery del botón
 * @param {function} asyncFunction - Función asíncrona a ejecutar
 * @param {string} loadingText - Texto durante la carga
 * @returns {Promise}
 */
async function withButtonLoading(button, asyncFunction, loadingText = 'Cargando...') {
    setButtonLoading(button, loadingText);

    try {
        const result = await asyncFunction();
        return result;
    } finally {
        resetButtonLoading(button);
    }
}

/**
 * Muestra overlay de carga en toda la página
 */
function showPageLoading(message = 'Cargando...') {
    // Crear overlay si no existe
    if ($('#page-loading-overlay').length === 0) {
        const overlayHTML = `
            <div id="page-loading-overlay" class="page-loading-overlay">
                <div class="page-loading-content">
                    <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <p class="page-loading-text">${message}</p>
                </div>
            </div>
        `;
        $('body').append(overlayHTML);
    } else {
        $('#page-loading-overlay .page-loading-text').text(message);
        $('#page-loading-overlay').fadeIn(200);
    }
}

/**
 * Oculta overlay de carga de la página
 */
function hidePageLoading() {
    $('#page-loading-overlay').fadeOut(200);
}

/**
 * Muestra skeleton loader en un contenedor
 * @param {string|jQuery} container - Selector o elemento jQuery del contenedor
 * @param {number} rows - Número de filas skeleton (default: 5)
 */
function showSkeletonLoader(container, rows = 5) {
    const $container = $(container);

    let skeletonHTML = '<div class="skeleton-loader">';
    for (let i = 0; i < rows; i++) {
        skeletonHTML += `
            <div class="skeleton-row">
                <div class="skeleton-item skeleton-avatar"></div>
                <div class="skeleton-item skeleton-text" style="width: 80%"></div>
                <div class="skeleton-item skeleton-text" style="width: 60%"></div>
            </div>
        `;
    }
    skeletonHTML += '</div>';

    $container.html(skeletonHTML);
}

/**
 * Muestra loading en tabla
 * @param {string|jQuery} tableBody - Selector del tbody
 * @param {number} colspan - Número de columnas
 */
function showTableLoading(tableBody, colspan = 5) {
    const $tbody = $(tableBody);
    const loadingHTML = `
        <tr>
            <td colspan="${colspan}" class="text-center py-5">
                <div class="spinner-border text-primary mb-2" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="text-muted mb-0">Cargando datos...</p>
            </td>
        </tr>
    `;
    $tbody.html(loadingHTML);
}
