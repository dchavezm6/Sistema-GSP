/**
 * JavaScript Principal del Sistema Municipal
 * Archivo: static/js/main.js
 */

// ========================================
// UTILIDADES GENERALES
// ========================================
/**
 * Animar contadores
 */
function animarContador(elementoId, valorFinal, duracion = 1000) {
    const elemento = document.getElementById(elementoId);
    if (!elemento) {
        console.warn('Elemento no encontrado:', elementoId);
        return;
    }

    const valorInicial = 0;
    const pasos = 60; // 60 frames
    const incremento = valorFinal / pasos;
    let valorActual = valorInicial;
    let paso = 0;

    const timer = setInterval(() => {
        paso++;
        valorActual += incremento;

        if (paso >= pasos) {
            elemento.textContent = Math.floor(valorFinal);
            clearInterval(timer);
        } else {
            elemento.textContent = Math.floor(valorActual);
        }
    }, duracion / pasos);
}

function confirmarAccion(mensaje, callback) {
    if (confirm(mensaje)) {
        if (typeof callback === 'function') {
            callback();
        }
        return true;
    }
    return false;
}

function mostrarToast(mensaje, tipo = 'info') {
    const toastHTML = `
        <div class="toast align-items-center text-white bg-${tipo} border-0 position-fixed bottom-0 end-0 m-3" role="alert" style="z-index: 9999;">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-info-circle me-2"></i>
                    ${mensaje}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', toastHTML);

    const toastElement = document.querySelector('.toast:last-child');
    const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// ========================================
// CONFIRMACIONES DE FORMULARIOS
// ========================================

document.addEventListener('DOMContentLoaded', function() {

    // Confirmación para cancelar solicitud
    const btnsCancelar = document.querySelectorAll('[data-confirm-cancel]');
    btnsCancelar.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('¿Está seguro que desea cancelar esta solicitud? Esta acción no se puede deshacer.')) {
                e.preventDefault();
            }
        });
    });

    // Confirmación para eliminar
    const btnsEliminar = document.querySelectorAll('[data-confirm-delete]');
    btnsEliminar.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('¿Está seguro que desea eliminar este elemento? Esta acción no se puede deshacer.')) {
                e.preventDefault();
            }
        });
    });

    // Confirmación genérica
    const btnsConfirm = document.querySelectorAll('[data-confirm]');
    btnsConfirm.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const mensaje = this.getAttribute('data-confirm');
            if (!confirm(mensaje)) {
                e.preventDefault();
            }
        });
    });
});

// ========================================
// INICIALIZACIÓN
// ========================================

console.log('✅ Sistema Municipal - JavaScript cargado correctamente');

// Exponer funciones globales
window.municipalApp = {
    confirmarAccion,
    mostrarToast,
    animarContador
};