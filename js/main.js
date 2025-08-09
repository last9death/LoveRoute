/* LoveRoute - Main JavaScript */

// Global variables
let isLoading = false;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize flash message auto-hide
    initFlashMessages();
    
    // Initialize mobile menu
    initMobileMenu();
    
    // Initialize form validations
    initFormValidations();
    
    // Initialize tooltips
    initTooltips();
});

// Flash Messages
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(function(message) {
        // Auto-hide after 5 seconds
        setTimeout(function() {
            hideFlashMessage(message);
        }, 5000);
        
        // Add click to dismiss
        message.addEventListener('click', function() {
            hideFlashMessage(message);
        });
    });
}

function hideFlashMessage(message) {
    message.style.transform = 'translateX(100%)';
    message.style.opacity = '0';
    setTimeout(function() {
        message.remove();
    }, 300);
}

// Mobile Menu
function initMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            const isOpen = mobileMenu.classList.contains('block');
            
            if (isOpen) {
                mobileMenu.classList.remove('block');
                mobileMenu.classList.add('hidden');
            } else {
                mobileMenu.classList.remove('hidden');
                mobileMenu.classList.add('block');
            }
        });
    }
}

// Form Validations
function initFormValidations() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                validateField(input);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(input);
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(function(input) {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    const required = field.hasAttribute('required');
    
    // Clear previous errors
    clearFieldError(field);
    
    // Required validation
    if (required && !value) {
        showFieldError(field, 'Это поле обязательно для заполнения');
        return false;
    }
    
    // Email validation
    if (type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Введите корректный email адрес');
            return false;
        }
    }
    
    // Password validation
    if (type === 'password' && value) {
        if (value.length < 6) {
            showFieldError(field, 'Пароль должен содержать минимум 6 символов');
            return false;
        }
    }
    
    // Select validation
    if (field.tagName === 'SELECT' && required && (!value || value === '')) {
        showFieldError(field, 'Выберите вариант из списка');
        return false;
    }
    
    return true;
}

function showFieldError(field, message) {
    field.classList.add('border-red-500');
    field.classList.remove('border-gray-300');
    
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error message
    const errorElement = document.createElement('div');
    errorElement.className = 'field-error text-red-500 text-sm mt-1';
    errorElement.textContent = message;
    field.parentNode.appendChild(errorElement);
}

function clearFieldError(field) {
    field.classList.remove('border-red-500');
    field.classList.add('border-gray-300');
    
    const errorElement = field.parentNode.querySelector('.field-error');
    if (errorElement) {
        errorElement.remove();
    }
}

// Tooltips
function initTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    
    tooltipTriggers.forEach(function(trigger) {
        trigger.addEventListener('mouseenter', function() {
            showTooltip(trigger);
        });
        
        trigger.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

function showTooltip(element) {
    const text = element.getAttribute('data-tooltip');
    const tooltip = document.createElement('div');
    
    tooltip.id = 'tooltip';
    tooltip.className = 'absolute z-50 bg-black text-white text-sm px-2 py-1 rounded shadow-lg';
    tooltip.textContent = text;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
}

function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Loading States
function showLoading() {
    isLoading = true;
    const loadingElements = document.querySelectorAll('.loading-state');
    loadingElements.forEach(function(element) {
        element.classList.remove('hidden');
    });
}

function hideLoading() {
    isLoading = false;
    const loadingElements = document.querySelectorAll('.loading-state');
    loadingElements.forEach(function(element) {
        element.classList.add('hidden');
    });
}

// API Utilities
function apiRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    };
    
    const config = Object.assign({}, defaultOptions, options);
    
    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }
    
    return fetch(url, config)
        .then(function(response) {
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.statusText);
            }
            return response.json();
        })
        .catch(function(error) {
            console.error('API request failed:', error);
            throw error;
        });
}

// Utility Functions
function debounce(func, wait, immediate) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(function() {
                inThrottle = false;
            }, limit);
        }
    };
}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const href = link.getAttribute('href');
            const target = document.querySelector(href);
            
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Initialize smooth scrolling
document.addEventListener('DOMContentLoaded', initSmoothScrolling);

// Image lazy loading
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(function(img) {
        imageObserver.observe(img);
    });
}

// Initialize lazy loading if IntersectionObserver is supported
if ('IntersectionObserver' in window) {
    document.addEventListener('DOMContentLoaded', initLazyLoading);
}

// Export functions for global use
window.LoveRoute = {
    showLoading,
    hideLoading,
    apiRequest,
    showTooltip,
    hideTooltip,
    validateForm,
    debounce,
    throttle
};