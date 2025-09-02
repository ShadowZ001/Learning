// MongoDB Database Connection and User Data Management
class SonicDatabase {
    constructor() {
        this.dbName = 'sonicbot';
        this.collections = {
            users: 'users',
            servers: 'servers',
            analytics: 'analytics'
        };
    }

    // Store user visit data
    async trackUserVisit() {
        const visitData = {
            timestamp: new Date(),
            userAgent: navigator.userAgent,
            url: window.location.href,
            referrer: document.referrer,
            sessionId: this.generateSessionId()
        };

        try {
            await this.storeData('analytics', visitData);
        } catch (error) {
            console.log('Analytics tracking failed:', error);
        }
    }

    // Store user interaction data
    async trackUserAction(action, data = {}) {
        const actionData = {
            action,
            data,
            timestamp: new Date(),
            sessionId: this.getSessionId(),
            url: window.location.href
        };

        try {
            await this.storeData('analytics', actionData);
        } catch (error) {
            console.log('Action tracking failed:', error);
        }
    }

    // Generate unique session ID
    generateSessionId() {
        const sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('sonic_session_id', sessionId);
        return sessionId;
    }

    // Get current session ID
    getSessionId() {
        return localStorage.getItem('sonic_session_id') || this.generateSessionId();
    }

    // Store data (placeholder for actual MongoDB integration)
    async storeData(collection, data) {
        // In a real implementation, this would connect to MongoDB
        // For now, store in localStorage as fallback
        const key = `sonic_${collection}_${Date.now()}`;
        localStorage.setItem(key, JSON.stringify(data));
        return true;
    }
}

// Initialize database tracking
const sonicDB = new SonicDatabase();

// Track page visits
document.addEventListener('DOMContentLoaded', () => {
    sonicDB.trackUserVisit();
});

// Track button clicks
document.addEventListener('click', (e) => {
    if (e.target.matches('.btn, .add-btn')) {
        const buttonText = e.target.textContent.trim();
        sonicDB.trackUserAction('button_click', { button: buttonText });
    }
});

// Track form submissions
document.addEventListener('submit', (e) => {
    sonicDB.trackUserAction('form_submit', { form: e.target.id || 'unknown' });
});

// Export for global use
window.SonicDB = sonicDB;