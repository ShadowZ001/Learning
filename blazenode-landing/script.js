// Initialize animations when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS-like animations
    initAnimations();
    
    // Add smooth scrolling
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add loading states to form
    const form = document.getElementById('authForm');
    const authBtn = form.querySelector('.auth-btn');
    
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

// Global auth mode state
let isLoginMode = true;

// Toggle between login and register modes
function toggleAuthMode() {
    isLoginMode = !isLoginMode;
    const authBtn = document.querySelector('.auth-btn');
    const authTitle = document.getElementById('authTitle');
    const authSubtitle = document.getElementById('authSubtitle');
    const switchBtn = document.querySelector('.switch-btn');
    const btnText = authBtn.querySelector('.btn-text');
    const switchText = switchBtn.parentElement;
    
    if (isLoginMode) {
        authTitle.textContent = 'Welcome Back';
        authSubtitle.textContent = 'Sign in to access your game servers and manage your resources';
        btnText.innerHTML = '<i class="fas fa-sign-in-alt"></i> Sign In';
        switchText.innerHTML = 'Don\'t have an account? <button type="button" onclick="toggleAuthMode()" class="switch-btn">Create Account</button>';
        authBtn.className = 'auth-btn login-mode';
    } else {
        authTitle.textContent = 'Create Account';
        authSubtitle.textContent = 'Join BlazeNode and get your free game servers today';
        btnText.innerHTML = '<i class="fas fa-user-plus"></i> Create Account';
        switchText.innerHTML = 'Already have an account? <button type="button" onclick="toggleAuthMode()" class="switch-btn">Sign In</button>';
        authBtn.className = 'auth-btn register-mode';
    }
}

// Handle authentication (login/register)
async function handleAuth(event) {
    event.preventDefault();
    
    const form = event.target;
    const authBtn = form.querySelector('.auth-btn');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const username = form.username.value.trim();
    const password = form.password.value.trim();
    
    // Enhanced validation
    if (!username || !password) {
        showNotification('Please fill in all fields', 'error');
        return;
    }
    
    if (username.length < 3) {
        showNotification('Username must be at least 3 characters', 'error');
        return;
    }
    
    if (password.length < 3) {
        showNotification('Password must be at least 3 characters', 'error');
        return;
    }
    
    // Show loading state
    authBtn.classList.add('loading');
    authBtn.disabled = true;
    
    try {
        const endpoint = isLoginMode ? '/api/login' : '/api/register';
        const action = isLoginMode ? 'login' : 'registration';
        
        console.log(`🔐 Attempting ${action} for:`, username);
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        console.log(`${action} response:`, response.status, data);
        
        if (response.ok && data.success) {
            if (isLoginMode) {
                // Login success
                showNotification('Login successful! Redirecting...', 'success');
                loadingOverlay.classList.add('active');
                
                setTimeout(() => {
                    window.location.href = '/dashboard.html';
                }, 1500);
            } else {
                // Registration success
                showNotification('Account created! You can now sign in.', 'success');
                
                // Switch to login mode
                setTimeout(() => {
                    toggleAuthMode();
                    form.username.value = username;
                    form.password.value = '';
                    form.password.focus();
                }, 1500);
            }
        } else {
            // Handle specific errors
            let errorMessage = data.error || `${action} failed`;
            
            if (response.status === 409) {
                errorMessage = 'Username already exists. Try a different one.';
            } else if (response.status === 401) {
                errorMessage = 'Invalid username or password.';
            } else if (response.status === 503) {
                errorMessage = 'Service temporarily unavailable. Please try again.';
            }
            
            showNotification(errorMessage, 'error');
            
            // Add shake animation
            form.classList.add('shake');
            setTimeout(() => form.classList.remove('shake'), 500);
        }
    } catch (error) {
        console.error(`${isLoginMode ? 'Login' : 'Registration'} error:`, error);
        showNotification('Connection error. Please check your internet and try again.', 'error');
        
        // Add shake animation
        form.classList.add('shake');
        setTimeout(() => form.classList.remove('shake'), 500);
    } finally {
        // Remove loading state
        authBtn.classList.remove('loading');
        authBtn.disabled = false;
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
    
    .switch-btn {
        background: none;
        border: none;
        color: #ff6b35;
        cursor: pointer;
        text-decoration: underline;
        font-weight: 500;
    }
    
    .switch-btn:hover {
        color: #f7931e;
    }
    
    .auth-switch {
        text-align: center;
        margin-top: 20px;
        color: rgba(255, 255, 255, 0.7);
    }
    
    .auth-switch p {
        margin: 0;
        font-size: 14px;
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
    if (e.target.matches('.auth-btn, .feature-card')) {
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

// Add ripple animation
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    @keyframes ripple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
`;
document.head.appendChild(rippleStyle);