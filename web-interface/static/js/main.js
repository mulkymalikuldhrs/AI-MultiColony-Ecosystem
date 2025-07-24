// Mobile navbar toggle
document.getElementById('navbar-toggle').addEventListener('click', function() {
    this.classList.toggle('active');
    document.getElementById('navbar-nav').classList.toggle('show');
});

// Active navigation highlighting
const currentPath = window.location.pathname;
document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
        link.classList.add('active');
    }
});

// Loading overlay control
window.showLoading = () => {
    document.getElementById('loading-overlay').style.display = 'flex';
};

window.hideLoading = () => {
    document.getElementById('loading-overlay').style.display = 'none';
};

// Global error handler
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    hideLoading();
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    hideLoading();
});
