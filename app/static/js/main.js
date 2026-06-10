/**
 * MedIntel Angola - JavaScript Principal
 */

// Inicializar tema ao carregar página
function initTheme() {
    const savedTheme = localStorage.getItem('medintel_theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);
    } else if (prefersDark) {
        document.documentElement.setAttribute('data-theme', 'dark');
        updateThemeIcon('dark');
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        updateThemeIcon('light');
    }
}

// Atualizar ícone do botão conforme tema
function updateThemeIcon(theme) {
    const sunIcon = document.getElementById('theme-sun');
    const moonIcon = document.getElementById('theme-moon');
    const themeText = document.querySelector('.theme-toggle span');
    
    if (sunIcon && moonIcon) {
        if (theme === 'dark') {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'inline';
            if (themeText) themeText.textContent = 'Escuro';
        } else {
            sunIcon.style.display = 'inline';
            moonIcon.style.display = 'none';
            if (themeText) themeText.textContent = 'Claro';
        }
    }
}

// Alternar entre temas
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('medintel_theme', newTheme);
    updateThemeIcon(newTheme);
    
    showNotification(newTheme === 'dark' ? 'Modo Escuro Ativado' : 'Modo Claro Ativado', 'info');
}

// Notificações
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fade-in-up`;
    notification.style.position = 'fixed';
    notification.style.top = '80px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '250px';
    notification.style.maxWidth = '350px';
    notification.style.boxShadow = 'var(--shadow-md)';
    notification.style.background = 'var(--bg-card)';
    notification.style.borderLeft = `4px solid var(--${type === 'success' ? 'success-green' : type === 'danger' ? 'danger-red' : 'accent-cyan'})`;
    
    notification.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'danger' ? 'fa-exclamation-triangle' : 'fa-info-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-sm" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) notification.remove();
    }, 3000);
}

// Auto-dismiss para alertas
function initAutoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.opacity = '0';
                setTimeout(() => {
                    if (alert.parentNode) alert.remove();
                }, 300);
            }
        }, 5000);
    });
}

// Confirmar eliminação
function initDeleteConfirmation() {
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Tem certeza que deseja eliminar? Esta ação não pode ser desfeita.')) {
                e.preventDefault();
            }
        });
    });
}

// Executar ao carregar
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    initAutoDismissAlerts();
    initDeleteConfirmation();
    
    // Adicionar evento ao botão de toggle
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }
});

// Exportar funções globais
window.MedIntel = {
    showNotification,
    initTheme,
    toggleTheme
};