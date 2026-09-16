// API Base Configuration
const API_BASE = '/api';

// Auth State Helper
const Auth = {
    getToken() {
        return localStorage.getItem('copilot_token');
    },
    setToken(token, isAdmin = false) {
        localStorage.setItem('copilot_token', token);
        localStorage.setItem('copilot_is_admin', isAdmin ? 'true' : 'false');
    },
    clearToken() {
        localStorage.removeItem('copilot_token');
        localStorage.removeItem('copilot_is_admin');
    },
    isLoggedIn() {
        return !!this.getToken();
    },
    isAdmin() {
        return localStorage.getItem('copilot_is_admin') === 'true';
    },
    getHeaders() {
        const headers = { 'Content-Type': 'application/json' };
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    }
};

// Global Navigation Hydration
document.addEventListener('DOMContentLoaded', () => {
    updateNavUI();
});

function updateNavUI() {
    const navAuthContainer = document.getElementById('nav-auth');
    if (!navAuthContainer) return;

    if (Auth.isLoggedIn()) {
        const isAdmin = Auth.isAdmin();
        navAuthContainer.innerHTML = `
            ${isAdmin ? '<a href="/admin/index.html" class="text-amber-600 hover:text-amber-700 font-semibold px-3 py-2 text-xs uppercase tracking-wider">Admin Panel</a>' : ''}
            <a href="/dashboard.html" class="text-slate-600 hover:text-slate-900 px-3 py-2 text-xs font-semibold">Dashboard</a>
            <a href="/onboarding.html" class="text-blue-600 hover:text-blue-700 px-3 py-2 text-xs font-bold">Find Schemes</a>
            <button onclick="handleLogout()" class="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-colors">Logout</button>
        `;
    } else {
        navAuthContainer.innerHTML = `
            <a href="/login.html" class="text-slate-600 hover:text-slate-900 px-3 py-2 text-xs font-semibold">Login</a>
            <a href="/register.html" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-sm">Get Started</a>
        `;
    }
}

function handleLogout() {
    Auth.clearToken();
    window.location.href = '/login.html';
}

// Toast Alert Notification
function showToast(message, type = 'info') {
    let toast = document.getElementById('toast-notification');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast-notification';
        toast.className = 'fixed bottom-5 right-5 z-50 px-5 py-3 rounded-2xl shadow-2xl text-white text-xs font-bold transition-all transform translate-y-10 opacity-0 duration-300 border border-white/20';
        document.body.appendChild(toast);
    }
    
    if (type === 'error') {
        toast.className = toast.className.replace(/bg-\w+-\d+/, '') + ' bg-red-600';
    } else if (type === 'success') {
        toast.className = toast.className.replace(/bg-\w+-\d+/, '') + ' bg-emerald-600';
    } else {
        toast.className = toast.className.replace(/bg-\w+-\d+/, '') + ' bg-blue-600';
    }

    toast.innerText = message;
    setTimeout(() => {
        toast.classList.remove('translate-y-10', 'opacity-0');
    }, 10);

    setTimeout(() => {
        toast.classList.add('translate-y-10', 'opacity-0');
    }, 4000);
}
