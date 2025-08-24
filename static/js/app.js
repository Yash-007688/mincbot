/**
 * Bot Vision Commander - Main JavaScript File
 * Provides common functionality across all pages
 */

// Global variables
let appState = {
    isConnected: false,
    lastUpdate: null,
    notifications: [],
    settings: {},
    theme: 'light'
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('🚀 Initializing Bot Vision Commander...');
    
    // Load settings
    loadAppSettings();
    
    // Setup global event listeners
    setupGlobalEventListeners();
    
    // Initialize theme
    initializeTheme();
    
    // Setup notification system
    setupNotificationSystem();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    console.log('✅ Bot Vision Commander initialized successfully');
}

/**
 * Load application settings from localStorage
 */
function loadAppSettings() {
    try {
        const savedSettings = localStorage.getItem('botVisionSettings');
        if (savedSettings) {
            appState.settings = JSON.parse(savedSettings);
        }
    } catch (error) {
        console.error('Error loading app settings:', error);
    }
}

/**
 * Setup global event listeners
 */
function setupGlobalEventListeners() {
    // Handle window resize
    window.addEventListener('resize', debounce(handleWindowResize, 250));
    
    // Handle page visibility changes
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Handle beforeunload
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    // Handle clicks outside modals
    document.addEventListener('click', handleOutsideClick);
}

/**
 * Initialize theme system
 */
function initializeTheme() {
    const savedTheme = appState.settings?.display?.theme || 'light';
    applyTheme(savedTheme);
    
    // Listen for system theme changes
    if (window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addListener(handleSystemThemeChange);
    }
}

/**
 * Apply theme to the application
 */
function applyTheme(theme) {
    const body = document.body;
    
    // Remove existing theme classes
    body.classList.remove('theme-light', 'theme-dark');
    
    // Determine actual theme
    let actualTheme = theme;
    if (theme === 'auto') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        actualTheme = prefersDark ? 'dark' : 'light';
    }
    
    // Apply theme class
    body.classList.add(`theme-${actualTheme}`);
    appState.theme = actualTheme;
    
    // Update theme toggle if it exists
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.checked = actualTheme === 'dark';
    }
    
    // Emit theme change event
    document.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: actualTheme } }));
}

/**
 * Handle system theme change
 */
function handleSystemThemeChange(e) {
    if (appState.settings?.display?.theme === 'auto') {
        applyTheme('auto');
    }
}

/**
 * Setup notification system
 */
function setupNotificationSystem() {
    // Request notification permission
    if ('Notification' in window) {
        Notification.requestPermission();
    }
    
    // Setup notification container
    createNotificationContainer();
}

/**
 * Create notification container
 */
function createNotificationContainer() {
    if (!document.getElementById('notification-container')) {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info', duration = 5000) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to container
    const container = document.getElementById('notification-container');
    if (container) {
        container.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
        
        // Add to app state
        appState.notifications.push({
            id: Date.now(),
            message,
            type,
            timestamp: new Date()
        });
        
        // Show desktop notification if enabled
        if (appState.settings?.system?.enableNotifications && type === 'error') {
            showDesktopNotification(message, type);
        }
    }
}

/**
 * Show desktop notification
 */
function showDesktopNotification(message, type) {
    if ('Notification' in window && Notification.permission === 'granted') {
        const notification = new Notification('Bot Vision Commander', {
            body: message,
            icon: '/static/images/robot-icon.png',
            tag: 'bot-vision-notification'
        });
        
        // Auto-close after 5 seconds
        setTimeout(() => notification.close(), 5000);
    }
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Only trigger shortcuts when not typing in input fields
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }
        
        // Ctrl/Cmd + K: Focus command input
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            focusCommandInput();
        }
        
        // Ctrl/Cmd + R: Refresh current page
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            refreshCurrentPage();
        }
        
        // Ctrl/Cmd + S: Save settings (if on settings page)
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            saveCurrentPage();
        }
        
        // Escape: Close modals
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });
}

/**
 * Focus command input if available
 */
function focusCommandInput() {
    const commandInputs = [
        'quick-command-input',
        'dashboard-command-input',
        'main-command-input'
    ];
    
    for (const id of commandInputs) {
        const input = document.getElementById(id);
        if (input) {
            input.focus();
            break;
        }
    }
}

/**
 * Refresh current page
 */
function refreshCurrentPage() {
    const currentPage = getCurrentPage();
    
    switch (currentPage) {
        case 'dashboard':
            if (typeof refreshDashboard === 'function') {
                refreshDashboard();
            }
            break;
        case 'bots':
            if (typeof refreshBotData === 'function') {
                refreshBotData();
            }
            break;
        case 'world':
            if (typeof refreshWorldData === 'function') {
                refreshWorldData();
            }
            break;
        case 'commands':
            if (typeof refreshCommands === 'function') {
                refreshCommands();
            }
            break;
        case 'analytics':
            if (typeof refreshAnalytics === 'function') {
                refreshAnalytics();
            }
            break;
        default:
            window.location.reload();
    }
}

/**
 * Save current page
 */
function saveCurrentPage() {
    const currentPage = getCurrentPage();
    
    switch (currentPage) {
        case 'settings':
            if (typeof saveAllSettings === 'function') {
                saveAllSettings();
            }
            break;
        default:
            showNotification('No save action available for this page', 'info');
    }
}

/**
 * Get current page name
 */
function getCurrentPage() {
    const path = window.location.pathname;
    if (path === '/' || path === '/index') return 'home';
    if (path === '/dashboard') return 'dashboard';
    if (path === '/bots') return 'bots';
    if (path === '/world') return 'world';
    if (path === '/commands') return 'commands';
    if (path === '/analytics') return 'analytics';
    if (path === '/settings') return 'settings';
    return 'unknown';
}

/**
 * Close all open modals
 */
function closeAllModals() {
    const modals = document.querySelectorAll('.modal.show');
    modals.forEach(modal => {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
            modalInstance.hide();
        }
    });
}

/**
 * Handle window resize
 */
function handleWindowResize() {
    // Emit resize event for components that need it
    document.dispatchEvent(new CustomEvent('windowResized', {
        detail: {
            width: window.innerWidth,
            height: window.innerHeight
        }
    }));
}

/**
 * Handle page visibility change
 */
function handleVisibilityChange() {
    if (document.hidden) {
        // Page is hidden, pause updates
        document.dispatchEvent(new CustomEvent('pageHidden'));
    } else {
        // Page is visible, resume updates
        document.dispatchEvent(new CustomEvent('pageVisible'));
    }
}

/**
 * Handle before unload
 */
function handleBeforeUnload() {
    // Save any unsaved data
    if (typeof saveCurrentPage === 'function') {
        saveCurrentPage();
    }
    
    // Clean up any timers or connections
    cleanupApp();
}

/**
 * Handle clicks outside elements
 */
function handleOutsideClick(e) {
    // Close dropdowns when clicking outside
    const dropdowns = document.querySelectorAll('.dropdown.show');
    dropdowns.forEach(dropdown => {
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });
}

/**
 * Cleanup application resources
 */
function cleanupApp() {
    // Clear any intervals
    if (window.appIntervals) {
        window.appIntervals.forEach(interval => clearInterval(interval));
    }
    
    // Clear any timeouts
    if (window.appTimeouts) {
        window.appTimeouts.forEach(timeout => clearTimeout(timeout));
    }
    
    // Close any open connections
    if (window.socket && window.socket.connected) {
        window.socket.disconnect();
    }
}

/**
 * Utility function to debounce function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility function to throttle function calls
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Format timestamp
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) { // Less than 1 minute
        return 'Just now';
    } else if (diff < 3600000) { // Less than 1 hour
        const minutes = Math.floor(diff / 60000);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else if (diff < 86400000) { // Less than 1 day
        const hours = Math.floor(diff / 3600000);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
        return date.toLocaleDateString();
    }
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard!', 'success', 2000);
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

/**
 * Fallback copy to clipboard for older browsers
 */
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Copied to clipboard!', 'success', 2000);
    } catch (err) {
        showNotification('Failed to copy to clipboard', 'error');
    }
    
    document.body.removeChild(textArea);
}

/**
 * Download data as file
 */
function downloadAsFile(data, filename, type = 'application/json') {
    const blob = new Blob([data], { type });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
}

/**
 * Validate email address
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Generate random ID
 */
function generateId(length = 8) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

/**
 * Deep clone object
 */
function deepClone(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime());
    if (obj instanceof Array) return obj.map(item => deepClone(item));
    if (typeof obj === 'object') {
        const cloned = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                cloned[key] = deepClone(obj[key]);
            }
        }
        return cloned;
    }
}

/**
 * Local storage wrapper with error handling
 */
const storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Error saving to localStorage:', error);
            return false;
        }
    },
    
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return defaultValue;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Error removing from localStorage:', error);
            return false;
        }
    },
    
    clear: function() {
        try {
            localStorage.clear();
            return true;
        } catch (error) {
            console.error('Error clearing localStorage:', error);
            return false;
        }
    }
};

/**
 * API wrapper with error handling
 */
const api = {
    get: async function(url, options = {}) {
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API GET error:', error);
            throw error;
        }
    },
    
    post: async function(url, data, options = {}) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                body: JSON.stringify(data),
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API POST error:', error);
            throw error;
        }
    }
};

/**
 * Export utility functions to global scope
 */
window.BotVisionUtils = {
    showNotification,
    copyToClipboard,
    downloadAsFile,
    formatTimestamp,
    formatFileSize,
    generateId,
    deepClone,
    storage,
    api,
    debounce,
    throttle
};

/**
 * Export app state to global scope for debugging
 */
window.appState = appState;

console.log('📦 Bot Vision Commander utilities loaded');