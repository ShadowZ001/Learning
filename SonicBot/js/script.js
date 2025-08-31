// Enhanced mobile-first JavaScript with performance optimizations
class SonicWebsite {
    constructor() {
        this.init();
    }

    init() {
        this.createParticles();
        this.setupNavigation();
        this.setupAnimations();
        this.setupInteractions();
        this.setupAccessibility();
    }

    // Optimized particle system
    createParticles() {
        const particlesContainer = document.createElement('div');
        particlesContainer.className = 'particles';
        document.body.appendChild(particlesContainer);
        
        const particleCount = window.innerWidth < 768 ? 20 : 50;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            const size = Math.random() * 3 + 1;
            particle.style.cssText = `
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                width: ${size}px;
                height: ${size}px;
                animation-delay: ${Math.random() * 8}s;
                animation-duration: ${Math.random() * 4 + 4}s;
            `;
            
            particlesContainer.appendChild(particle);
        }
    }

    // Enhanced navigation with mobile support
    setupNavigation() {
        const mobileMenu = document.querySelector('.mobile-menu');
        const navLinks = document.querySelector('.nav-links');
        const nav = document.querySelector('nav');
        
        // Mobile menu toggle
        if (mobileMenu && navLinks) {
            mobileMenu.addEventListener('click', () => {
                mobileMenu.classList.toggle('active');
                navLinks.classList.toggle('active');
                document.body.style.overflow = navLinks.classList.contains('active') ? 'hidden' : '';
            });

            // Close menu when clicking on links
            navLinks.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    mobileMenu.classList.remove('active');
                    navLinks.classList.remove('active');
                    document.body.style.overflow = '';
                });
            });
        }

        // Enhanced scroll effect with throttling
        let ticking = false;
        const updateNav = () => {
            const scrolled = window.scrollY;
            
            if (scrolled > 50) {
                nav.style.background = 'rgba(10, 10, 10, 0.95)';
                nav.style.backdropFilter = 'blur(25px)';
                nav.style.boxShadow = '0 8px 32px rgba(0,0,0,0.3)';
            } else {
                nav.style.background = 'rgba(10, 10, 10, 0.8)';
                nav.style.backdropFilter = 'blur(20px)';
                nav.style.boxShadow = 'none';
            }
            
            ticking = false;
        };

        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateNav);
                ticking = true;
            }
        });
    }

    // Intersection Observer for animations
    setupAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0) scale(1)';
                        entry.target.classList.add('animate-in');
                    }, index * 100);
                }
            });
        }, observerOptions);

        // Observe elements with staggered animation
        document.querySelectorAll('.feature-card, .stat-item, .support-card, .faq-item').forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px) scale(0.95)';
            el.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
            observer.observe(el);
        });

        // Counter animation for stats
        this.setupCounters();
    }

    setupCounters() {
        const animateCounter = (element, target) => {
            let current = 0;
            const increment = target / 60;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                
                const suffix = target >= 1000 ? 'K+' : target >= 50 ? '+' : '';
                const displayValue = target >= 1000 ? Math.floor(current / 1000) : Math.floor(current);
                element.textContent = displayValue + suffix;
            }, 16);
        };

        const statsObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const statItems = entry.target.querySelectorAll('.stat-item h3');
                    statItems.forEach(item => {
                        const text = item.textContent;
                        let number = parseInt(text.replace(/[^0-9]/g, ''));
                        
                        // Handle K+ format
                        if (text.includes('K+')) {
                            number = number * 1000;
                        }
                        
                        animateCounter(item, number);
                    });
                    statsObserver.unobserve(entry.target);
                }
            });
        });

        const statsSection = document.querySelector('.stats');
        if (statsSection) {
            statsObserver.observe(statsSection);
        }
    }

    // Enhanced interactions
    setupInteractions() {
        // FAQ Accordion with smooth animations
        document.querySelectorAll('.faq-question').forEach(question => {
            question.addEventListener('click', () => {
                const answer = question.nextElementSibling;
                const isActive = answer.classList.contains('active');
                const icon = question.querySelector('span');
                
                // Close all other answers
                document.querySelectorAll('.faq-answer').forEach(ans => {
                    ans.classList.remove('active');
                    ans.style.maxHeight = '0';
                });
                
                document.querySelectorAll('.faq-question span').forEach(span => {
                    span.style.transform = 'rotate(0deg)';
                    span.textContent = '+';
                });
                
                // Toggle current answer
                if (!isActive) {
                    answer.classList.add('active');
                    answer.style.maxHeight = answer.scrollHeight + 'px';
                    icon.style.transform = 'rotate(45deg)';
                    icon.textContent = '×';
                }
            });
        });

        // Enhanced button interactions
        this.setupButtonEffects();
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    setupButtonEffects() {
        // Ripple effect for buttons
        document.querySelectorAll('.btn, .add-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
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
                
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
            });
        });

        // Hover effects with performance optimization
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-3px) scale(1.02)';
            });
            
            btn.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    // Accessibility enhancements
    setupAccessibility() {
        // Keyboard navigation for mobile menu
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const mobileMenu = document.querySelector('.mobile-menu');
                const navLinks = document.querySelector('.nav-links');
                
                if (navLinks && navLinks.classList.contains('active')) {
                    mobileMenu.classList.remove('active');
                    navLinks.classList.remove('active');
                    document.body.style.overflow = '';
                }
            }
        });

        // Focus management
        document.querySelectorAll('.btn, .add-btn, .faq-question').forEach(element => {
            element.addEventListener('focus', function() {
                this.style.outline = '2px solid #00d4ff';
                this.style.outlineOffset = '2px';
            });
            
            element.addEventListener('blur', function() {
                this.style.outline = 'none';
            });
        });

        // Reduced motion support
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.documentElement.style.setProperty('--animation-duration', '0.01s');
        }
    }
}

// Performance optimizations
const addRippleCSS = () => {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(2);
                opacity: 0;
            }
        }
        
        .animate-in {
            animation: pulse 0.6s ease-out;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
    `;
    document.head.appendChild(style);
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    addRippleCSS();
    new SonicWebsite();
});

// Handle page visibility for performance
document.addEventListener('visibilitychange', () => {
    const particles = document.querySelector('.particles');
    if (particles) {
        particles.style.animationPlayState = document.hidden ? 'paused' : 'running';
    }
});

// Resize handler with debouncing
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        // Recreate particles on significant resize
        if (Math.abs(window.innerWidth - (window.lastWidth || 0)) > 200) {
            const existingParticles = document.querySelector('.particles');
            if (existingParticles) {
                existingParticles.remove();
            }
            new SonicWebsite().createParticles();
            window.lastWidth = window.innerWidth;
        }
    }, 250);
});