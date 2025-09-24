// Clerk configuration
const CLERK_PUBLISHABLE_KEY = 'pk_test_dmlhYmxlLWNvdy0zNy5jbGVyay5hY2NvdW50cy5kZXYk';

// Wait for Clerk to load
function waitForClerk() {
    return new Promise((resolve) => {
        if (window.Clerk) {
            resolve(window.Clerk);
        } else {
            const checkClerk = setInterval(() => {
                if (window.Clerk) {
                    clearInterval(checkClerk);
                    resolve(window.Clerk);
                }
            }, 100);
        }
    });
}

// Initialize Clerk authentication
async function initializeAuth() {
    try {
        const clerk = await waitForClerk();
        
        // Load Clerk with publishable key
        await clerk.load({
            publishableKey: CLERK_PUBLISHABLE_KEY
        });

        // Check if user is already signed in
        if (clerk.user) {
            window.location.href = '/dashboard';
            return;
        }

        // Mount sign-in component
        const signInElement = document.getElementById('sign-in');
        
        clerk.mountSignIn(signInElement, {
            afterSignInUrl: '/dashboard',
            afterSignUpUrl: '/dashboard',
            appearance: {
                elements: {
                    card: {
                        backgroundColor: 'transparent',
                        boxShadow: 'none',
                        border: 'none'
                    },
                    headerTitle: {
                        color: '#ffffff',
                        fontSize: '1.5rem'
                    },
                    formFieldInput: {
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        borderRadius: '10px',
                        color: '#ffffff',
                        padding: '12px 16px'
                    },
                    formFieldLabel: {
                        color: 'rgba(255, 255, 255, 0.8)'
                    },
                    button: {
                        background: 'linear-gradient(45deg, #ff6b6b, #4ecdc4)',
                        border: 'none',
                        borderRadius: '10px',
                        padding: '12px 24px',
                        fontWeight: '600'
                    },
                    socialButtonsBlockButton: {
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        borderRadius: '10px',
                        color: '#ffffff'
                    },
                    footerActionLink: {
                        color: '#4ecdc4'
                    }
                }
            }
        });

        // Listen for sign-in events
        clerk.addListener('user', (user) => {
            if (user) {
                window.location.href = '/dashboard';
            }
        });

    } catch (error) {
        console.error('Clerk initialization error:', error);
        showError('Failed to load authentication. Please refresh the page.');
    }
}

// Show error message
function showError(message) {
    const signInDiv = document.getElementById('sign-in');
    signInDiv.innerHTML = `
        <div style="
            background: rgba(255, 107, 107, 0.1);
            border: 1px solid rgba(255, 107, 107, 0.3);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            color: #ff6b6b;
        ">
            <h3>Authentication Error</h3>
            <p>${message}</p>
            <button onclick="location.reload()" style="
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                color: white;
                margin-top: 10px;
                cursor: pointer;
                font-weight: 600;
            ">Retry</button>
        </div>
    `;
}

// Show loading state
function showLoading() {
    const signInDiv = document.getElementById('sign-in');
    signInDiv.innerHTML = `
        <div style="text-align: center; padding: 40px; color: rgba(255,255,255,0.7);">
            <div class="loading"></div>
            <p style="margin-top: 15px;">Loading authentication...</p>
        </div>
    `;
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    showLoading();
    initializeAuth();
});