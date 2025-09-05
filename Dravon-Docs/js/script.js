// Enhanced Mobile Navigation Toggle
const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('nav-menu');

hamburger?.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
    document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
});

// Close mobile menu when clicking on a link or outside
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        hamburger?.classList.remove('active');
        navMenu?.classList.remove('active');
        document.body.style.overflow = '';
    });
});

document.addEventListener('click', (e) => {
    if (!navMenu?.contains(e.target) && !hamburger?.contains(e.target)) {
        hamburger?.classList.remove('active');
        navMenu?.classList.remove('active');
        document.body.style.overflow = '';
    }
});

// Enhanced Smooth Scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const headerOffset = 80;
            const elementPosition = target.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Enhanced Navbar Scroll Effect
let lastScrollY = window.scrollY;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScrollY = window.scrollY;
    
    if (navbar) {
        if (currentScrollY > 100) {
            navbar.style.background = 'rgba(13, 17, 23, 0.98)';
            navbar.style.backdropFilter = 'blur(16px)';
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
        } else {
            navbar.style.background = 'rgba(13, 17, 23, 0.95)';
            navbar.style.backdropFilter = 'blur(12px)';
            navbar.style.boxShadow = 'none';
        }
        
        // Hide/show navbar on scroll
        if (currentScrollY > lastScrollY && currentScrollY > 200) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
    }
    
    lastScrollY = currentScrollY;
});

// Enhanced Intersection Observer for Animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const fadeInObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            fadeInObserver.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe elements for fade-in animation
document.addEventListener('DOMContentLoaded', () => {
    const animateElements = document.querySelectorAll('.step-card, .command-category, .showcase-item');
    
    animateElements.forEach((el, index) => {
        el.classList.add('fade-in');
        el.style.transitionDelay = `${index * 0.1}s`;
        fadeInObserver.observe(el);
    });
});

// Enhanced Command Category Interactions
document.querySelectorAll('.command-category').forEach(category => {
    category.addEventListener('click', (e) => {
        // Don't trigger if clicking on dropdown menu
        if (e.target.closest('.category-menu')) return;
        
        const categoryType = category.dataset.category;
        if (categoryType) {
            // Add click animation
            category.style.transform = 'scale(0.98)';
            setTimeout(() => {
                category.style.transform = '';
                window.open(`pages/${categoryType}.html`, '_blank');
            }, 150);
        }
    });
    
    // Add hover sound effect (optional)
    category.addEventListener('mouseenter', () => {
        category.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    });
});

// Enhanced Copy Code Functionality
function copyCode(button) {
    const codeBlock = button.nextElementSibling;
    const code = codeBlock?.textContent || '';
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(code).then(() => {
            showCopyFeedback(button, 'Copied!', '#238636');
        }).catch(() => {
            fallbackCopyTextToClipboard(code, button);
        });
    } else {
        fallbackCopyTextToClipboard(code, button);
    }
}

function fallbackCopyTextToClipboard(text, button) {
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
        showCopyFeedback(button, 'Copied!', '#238636');
    } catch (err) {
        showCopyFeedback(button, 'Failed', '#f85149');
    }
    
    document.body.removeChild(textArea);
}

function showCopyFeedback(button, text, color) {
    const originalText = button.textContent;
    const originalBg = button.style.background;
    
    button.textContent = text;
    button.style.background = color;
    button.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
        button.textContent = originalText;
        button.style.background = originalBg;
        button.style.transform = '';
    }, 2000);
}

// Enhanced Search Functionality
function initSearch() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            performSearch(e.target.value.toLowerCase());
        }, 300);
    });
}

function performSearch(query) {
    const categories = document.querySelectorAll('.command-category');
    let visibleCount = 0;
    
    categories.forEach(category => {
        const title = category.querySelector('h3')?.textContent.toLowerCase() || '';
        const description = category.querySelector('p')?.textContent.toLowerCase() || '';
        const features = Array.from(category.querySelectorAll('.feature-tag'))
            .map(tag => tag.textContent.toLowerCase()).join(' ');
        
        const matches = !query || title.includes(query) || 
                       description.includes(query) || 
                       features.includes(query);
        
        category.style.display = matches ? 'block' : 'none';
        if (matches) visibleCount++;
    });
    
    // Show no results message
    const noResults = document.getElementById('no-results');
    if (noResults) {
        noResults.style.display = visibleCount === 0 && query ? 'block' : 'none';
    }
}

// Theme Toggle Functionality
const themeToggle = document.getElementById('theme-toggle');
const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

function getCurrentTheme() {
    return localStorage.getItem('theme') || (prefersDarkScheme.matches ? 'dark' : 'light');
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    const icon = themeToggle?.querySelector('i');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

themeToggle?.addEventListener('click', () => {
    const currentTheme = getCurrentTheme();
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
});

// Initialize theme
document.addEventListener('DOMContentLoaded', () => {
    setTheme(getCurrentTheme());
});

// Enhanced Scroll to Top
const scrollTopBtn = document.getElementById('scroll-top');

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

function toggleScrollTopButton() {
    if (scrollTopBtn) {
        if (window.scrollY > 300) {
            scrollTopBtn.style.display = 'flex';
            scrollTopBtn.style.opacity = '1';
        } else {
            scrollTopBtn.style.opacity = '0';
            setTimeout(() => {
                if (window.scrollY <= 300) {
                    scrollTopBtn.style.display = 'none';
                }
            }, 300);
        }
    }
}

window.addEventListener('scroll', toggleScrollTopButton);

// Enhanced Loading Animation
window.addEventListener('load', () => {
    const loader = document.querySelector('.loader');
    if (loader) {
        loader.style.opacity = '0';
        setTimeout(() => {
            loader.style.display = 'none';
            document.body.style.overflow = '';
        }, 300);
    }
});

// Enhanced Form Validation
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        const value = input.value.trim();
        const isEmail = input.type === 'email';
        const isValidEmail = isEmail ? /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) : true;
        
        if (!value || (isEmail && !isValidEmail)) {
            showFieldError(input, isEmail && value ? 'Invalid email format' : 'This field is required');
            isValid = false;
        } else {
            clearFieldError(input);
        }
    });
    
    return isValid;
}

function showFieldError(input, message) {
    input.classList.add('error');
    
    let errorMsg = input.parentNode.querySelector('.error-message');
    if (!errorMsg) {
        errorMsg = document.createElement('div');
        errorMsg.className = 'error-message';
        input.parentNode.appendChild(errorMsg);
    }
    errorMsg.textContent = message;
}

function clearFieldError(input) {
    input.classList.remove('error');
    const errorMsg = input.parentNode.querySelector('.error-message');
    if (errorMsg) {
        errorMsg.remove();
    }
}

// Enhanced Tooltip Functionality
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(element => {
        let tooltip;
        
        element.addEventListener('mouseenter', (e) => {
            tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = e.target.dataset.tooltip;
            document.body.appendChild(tooltip);
            
            positionTooltip(e.target, tooltip);
        });
        
        element.addEventListener('mouseleave', () => {
            if (tooltip) {
                tooltip.remove();
                tooltip = null;
            }
        });
        
        element.addEventListener('mousemove', (e) => {
            if (tooltip) {
                positionTooltip(e.target, tooltip);
            }
        });
    });
}

function positionTooltip(target, tooltip) {
    const rect = target.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
    let top = rect.top - tooltipRect.height - 10;
    
    // Adjust if tooltip goes off screen
    if (left < 10) left = 10;
    if (left + tooltipRect.width > window.innerWidth - 10) {
        left = window.innerWidth - tooltipRect.width - 10;
    }
    if (top < 10) {
        top = rect.bottom + 10;
    }
    
    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
}

// Lazy Loading for Images
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                img.classList.add('loaded');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => {
        img.classList.add('lazy');
        imageObserver.observe(img);
    });
}

// Performance Monitoring
function initPerformanceMonitoring() {
    if ('performance' in window) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    console.log(`Page load time: ${perfData.loadEventEnd - perfData.loadEventStart}ms`);
                }
            }, 0);
        });
    }
}

// Keyboard Navigation Enhancement
function initKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
        // ESC key closes mobile menu
        if (e.key === 'Escape') {
            hamburger?.classList.remove('active');
            navMenu?.classList.remove('active');
            document.body.style.overflow = '';
        }
        
        // Enter key on command categories
        if (e.key === 'Enter' && e.target.classList.contains('command-category')) {
            e.target.click();
        }
    });
}

// Initialize all functionality
document.addEventListener('DOMContentLoaded', () => {
    initSearch();
    initTooltips();
    initLazyLoading();
    initPerformanceMonitoring();
    initKeyboardNavigation();
    
    // Add loading class to body
    document.body.classList.add('loaded');
});

// Service Worker Registration (for PWA capabilities)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Error Handling
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
});

// Analytics (placeholder for future implementation)
function trackEvent(eventName, properties = {}) {
    // Implement analytics tracking here
    console.log('Event tracked:', eventName, properties);
}

// Export functions for external use
window.DravonDocs = {
    copyCode,
    scrollToTop,
    validateForm,
    trackEvent
};