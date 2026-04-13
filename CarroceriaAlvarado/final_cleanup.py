
import os

SETTINGS_MODAL_HTML = """
<!-- Modal de Configuración/Perfil (Reutilizado) -->
<div class="modal fade" id="settingsModal" tabindex="-1" role="dialog" aria-labelledby="settingsModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content border-0 shadow-lg" style="border-radius: 15px; overflow: hidden;">
            <div class="modal-header bg-secondary text-white border-0">
                <h5 class="modal-title" id="settingsModalLabel">
                    <i class="fa fa-cog mr-2"></i> Configuraciones Generales
                </h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body p-4">
                <div id="settingsMessage"></div>
                <form id="settingsForm">
                    <div class="form-group mb-3">
                        <label for="settingResetTokenExpiry" class="font-weight-bold">Duración del Token (minutos)</label>
                        <input type="number" class="form-control" id="settingResetTokenExpiry" min="1" required style="border-radius: 8px;">
                        <small class="form-text text-muted">Tiempo de validez para el enlace de reseteo.</small>
                    </div>
                    <div class="form-group mb-3">
                        <label for="settingMaxLoginAttempts" class="font-weight-bold">Máximos Intentos de Login</label>
                        <input type="number" class="form-control" id="settingMaxLoginAttempts" min="1" required style="border-radius: 8px;">
                        <small class="form-text text-muted">Número de intentos antes de bloquear la cuenta.</small>
                    </div>
                    <div class="form-group mb-3">
                        <label for="settingGlobalLowStockThreshold" class="font-weight-bold">Limite Global de Stock Bajo</label>
                        <input type="number" class="form-control" id="settingGlobalLowStockThreshold" min="0" required style="border-radius: 8px;">
                        <small class="form-text text-muted">Materiales a resaltar bajo este stock.</small>
                    </div>
                    <div class="modal-footer border-0 justify-content-center pt-3">
                        <button type="button" class="btn btn-light px-4" data-bs-dismiss="modal" style="border-radius: 10px;">Cancelar</button>
                        <button type="submit" class="btn btn-secondary px-4" style="border-radius: 10px; font-weight: 600;">Guardar Configuraciones</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
"""

SCRIPTS_BLOCK = """
<!-- Dependencias de Scripts (Orden Correcto) -->
<script src="vendor/jquery/jquery-3.2.1.min.js"></script>
<script src="vendor/bootstrap/js/bootstrap.bundle.min.js"></script>
<script src="js/config.js"></script>
<script src="js/dashboard-core.js"></script>
"""

DASHBOARD_PAGES = [
    "ver_inventario.html",
    "ver_proveedores.html",
    "vision_general.html",
    "listar_ordenes_trabajo.html",
    "ver_empleados.html",
    "gestion_categorias.html"
]

def clean_and_inject(filename):
    path = os.path.join("frontend", filename)
    if not os.path.exists(path):
        return
    
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 1. Inject settingsModal if missing
    if 'id="settingsModal"' not in content:
        # Find the last closing div of admin-wrapper context or similar
        # Usually it's before the first script tag
        script_idx = content.find('<script')
        if script_idx != -1:
            content = content[:script_idx] + SETTINGS_MODAL_HTML + content[script_idx:]
            print(f"Injected settingsModal to {filename}")

    # 2. Fix scripts (This is trickier without regex, but we can look for common mess)
    # Actually, we already fixed most. Let's just ensure dashboard-core is there.
    if 'dashboard-core.js' not in content:
        # Add it after config.js
        content = content.replace('src="js/config.js"></script>', 'src="js/config.js"></script>\n<script src="js/dashboard-core.js"></script>')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    for page in DASHBOARD_PAGES:
        clean_and_inject(page)

if __name__ == "__main__":
    main()
