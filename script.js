// Initialize animations when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS-like animations
    initAnimations();
    
    // Add smooth scrolling
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add loading states to form
    const form = document.getElementById('loginForm');
    const loginBtn = form.querySelector('.login-btn');
    
    // Add focus effects to inputs
    const inputs = form.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
    });
});

// Initialize animations
function initAnimations() {
    const animatedElements = document.querySelectorAll('[data-aos]');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('aos-animate');
                }, parseInt(entry.target.dataset.aosDelay) || 0);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    animatedElements.forEach(el => {
        observer.observe(el);
    });
}

// Enhanced Discord OAuth feedback
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.get('login') === 'discord_success') {
        const discordJoin = urlParams.get('discord_join');
        let message = '🎉 Discord login successful!';
        
        if (discordJoin === 'joined') {
            message += ' You\'ve been added to our Discord server!';
        } else if (discordJoin === 'not_joined') {
            message += ' Note: Could not auto-join Discord server.';
        }
        
        showNotification(message, 'success');
        
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    } else if (urlParams.get('login') === 'success') {
        showNotification('Login successful!', 'success');
        window.history.replaceState({}, document.title, window.location.pathname);
    } else if (urlParams.get('error')) {
        const error = urlParams.get('error');
        const reason = urlParams.get('reason');
        
        let errorMessage = 'Authentication failed';
        
        if (error === 'discord_auth_failed') {
            errorMessage = 'Discord authentication failed';
            if (reason === 'server_error') {
                errorMessage += ' - Server error occurred';
            } else if (reason === 'no_user') {
                errorMessage += ' - User verification failed';
            }
        } else if (error === 'login_failed') {
            errorMessage = 'Login failed';
            if (reason === 'session_error') {
                errorMessage += ' - Session creation failed';
            } else if (reason === 'session_setup') {
                errorMessage += ' - Session setup failed';
            }
        }
        
        showNotification(errorMessage, 'error');
        
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});

// Simple login function
async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const loginBtn = form.querySelector('.login-btn');
    const username = form.username.value;
    const password = form.password.value;
    
    if (!username || !password) {
        showNotification('Please enter username and password', 'error');
        return;
    }
    
    loginBtn.disabled = true;
    loginBtn.textContent = 'Logging in...';
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Login successful!', 'success');
            window.location.href = '/dashboard.html';
        } else {
            showNotification(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showNotification('Connection error', 'error');
    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = 'Login';
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // Set styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        border-radius: 12px;
        color: white;
        font-weight: 500;
        font-size: 14px;
        z-index: 10000;
        max-width: 400px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        animation: slideInRight 0.3s ease, fadeOut 0.3s ease 2.7s forwards;
        transform: translateX(100%);
    `;
    
    // Set background based on type
    if (type === 'success') {
        notification.style.background = 'linear-gradient(135deg, #10b981, #059669)';
        notification.innerHTML = `<i class="fas fa-check-circle" style="margin-right: 8px;"></i>${message}`;
    } else if (type === 'error') {
        notification.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
        notification.innerHTML = `<i class="fas fa-exclamation-circle" style="margin-right: 8px;"></i>${message}`;
    } else {
        notification.style.background = 'linear-gradient(135deg, #3b82f6, #2563eb)';
        notification.innerHTML = `<i class="fas fa-info-circle" style="margin-right: 8px;"></i>${message}`;
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Trigger animation
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Remove after delay
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
    
    .shake {
        animation: shake 0.5s ease-in-out;
    }
    
    .form-group.focused label {
        color: #ff6b35;
    }
    
    .form-group.focused input {
        border-color: #ff6b35;
        box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
    }
    
    .login-help {
        text-align: center;
        margin-top: 20px;
        padding: 15px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .help-text {
        color: rgba(255, 255, 255, 0.7);
        font-size: 12px;
        margin: 0;
        line-height: 1.4;
    }
    

    
    /* Smooth transitions for all interactive elements */
    * {
        transition: all 0.3s ease;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #ff6b35, #f7931e);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #f7931e, #ff6b35);
    }
`;
document.head.appendChild(style);



// Add some interactive effects
document.addEventListener('mousemove', function(e) {
    // Subtle parallax effect for particles
    const particles = document.querySelectorAll('.particle');
    const mouseX = e.clientX / window.innerWidth;
    const mouseY = e.clientY / window.innerHeight;
    
    particles.forEach((particle, index) => {
        const speed = (index + 1) * 0.5;
        const x = (mouseX - 0.5) * speed;
        const y = (mouseY - 0.5) * speed;
        
        particle.style.transform = `translate(${x}px, ${y}px)`;
    });
});

// Add click ripple effect to buttons
document.addEventListener('click', function(e) {
    if (e.target.matches('.login-btn, .feature-card')) {
        const ripple = document.createElement('span');
        const rect = e.target.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
        `;
        
        e.target.style.position = 'relative';
        e.target.style.overflow = 'hidden';
        e.target.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }
});

// Password toggle function
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.getElementById('passwordToggleIcon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.className = 'fas fa-eye-slash';
    } else {
        passwordInput.type = 'password';
        toggleIcon.className = 'fas fa-eye';
    }
}

// Add ripple animation
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    @keyframes ripple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    .password-input-container {
        position: relative;
        display: flex;
        align-items: center;
    }
    
    .password-input-container input {
        flex: 1;
        padding-right: 45px;
    }
    
    .password-toggle {
        position: absolute;
        right: 12px;
        background: none;
        border: none;
        color: rgba(255, 255, 255, 0.6);
        cursor: pointer;
        padding: 8px;
        border-radius: 4px;
        transition: color 0.3s ease;
    }
    
    .password-toggle:hover {
        color: #ff6b35;
    }
    
    .password-toggle i {
        font-size: 16px;
    }
`;
document.head.appendChild(rippleStyle);