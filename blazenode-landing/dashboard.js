// Dashboard functionality
class Dashboard {
    constructor() {
        this.apiKey = null; // Will be set when provided
        this.baseUrl = null; // Pterodactyl panel URL
        this.username = 'dev_shadowz'; // Default, will be updated from login
        this.init();
    }

    init() {
        this.loadUserData();
        this.setupEventListeners();
        // Initialize with 0% resources as requested
        this.updateResourceDisplay();
    }

    // Load user data from API
    async loadUserData() {
        try {
            const response = await fetch('/api/user', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const user = await response.json();
                this.username = user.username;
                this.userCoins = user.coins;
                document.getElementById('username').textContent = this.username;
                
                // Update avatar if available
                if (user.avatar) {
                    const avatarElement = document.querySelector('.profile-avatar i');
                    if (avatarElement) {
                        avatarElement.outerHTML = `<img src="https://cdn.discordapp.com/avatars/${user.discordId}/${user.avatar}.png" alt="Avatar" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">`;
                    }
                }
                
                // Update coins display
                this.updateCoinsDisplay();
            } else {
                // Not authenticated, redirect to login
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Error loading user data:', error);
            window.location.href = '/';
        }
    }

    // Setup event listeners
    setupEventListeners() {
        // Claim reward button
        const claimBtn = document.querySelector('.claim-btn');
        if (claimBtn) {
            claimBtn.addEventListener('click', this.claimDailyReward.bind(this));
        }

        // Sidebar navigation
        const menuItems = document.querySelectorAll('.menu-item');
        menuItems.forEach(item => {
            item.addEventListener('click', (e) => {
                // Remove active class from all items
                menuItems.forEach(mi => mi.classList.remove('active'));
                // Add active class to clicked item
                e.currentTarget.classList.add('active');
            });
        });
    }

    // Update resource display (starts at 0% as requested)
    updateResourceDisplay() {
        const resources = {
            memory: { used: 0, total: 6, unit: 'GB' },
            cpu: { used: 0, total: 200, unit: '%' },
            storage: { used: 0, total: 15, unit: 'GB' },
            servers: { used: 0, total: 4, unit: '' }
        };

        Object.keys(resources).forEach(key => {
            const resource = resources[key];
            const percentage = (resource.used / resource.total) * 100;
            
            // Update progress bar
            const progressBar = document.querySelector(`.resource-card:nth-child(${Object.keys(resources).indexOf(key) + 1}) .progress-fill`);
            if (progressBar) {
                progressBar.style.width = `${percentage}%`;
            }

            // Update text values
            const valueElement = document.querySelector(`.resource-card:nth-child(${Object.keys(resources).indexOf(key) + 1}) .resource-value`);
            const percentageElement = document.querySelector(`.resource-card:nth-child(${Object.keys(resources).indexOf(key) + 1}) .resource-percentage`);
            
            if (valueElement) {
                if (key === 'cpu') {
                    valueElement.textContent = `${resource.used}% / ${resource.total}%`;
                } else {
                    valueElement.textContent = `${resource.used}${resource.unit} / ${resource.total}${resource.unit}`;
                }
            }
            
            if (percentageElement) {
                percentageElement.textContent = `${Math.round(percentage)}% utilized`;
            }
        });

        // Update server stats
        const serverCountElement = document.querySelector('.stat-number');
        if (serverCountElement) {
            serverCountElement.textContent = resources.servers.used;
        }
    }

    // Update coins display
    updateCoinsDisplay() {
        if (this.userCoins !== undefined) {
            // Add coins display to header if not exists
            const welcomeSection = document.querySelector('.welcome-section');
            let coinsDisplay = document.querySelector('.coins-display');
            
            if (!coinsDisplay && welcomeSection) {
                coinsDisplay = document.createElement('div');
                coinsDisplay.className = 'coins-display';
                coinsDisplay.style.cssText = 'margin-top: 10px; color: #fbbf24; font-weight: 600;';
                welcomeSection.appendChild(coinsDisplay);
            }
            
            if (coinsDisplay) {
                coinsDisplay.innerHTML = `💰 ${this.userCoins} BlazeCoins`;
            }
        }
    }

    // Claim daily reward
    async claimDailyReward() {
        const claimBtn = document.querySelector('.claim-btn');
        
        try {
            const response = await fetch('/api/claim-reward', {
                method: 'POST',
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                claimBtn.textContent = 'Claimed! ✓';
                claimBtn.style.background = '#10b981';
                claimBtn.disabled = true;
                
                // Update coins
                this.userCoins = data.coins;
                this.updateCoinsDisplay();
                
                // Show success message
                alert(`Daily reward claimed! You now have ${data.coins} coins. Streak: ${data.streak} days`);
            } else {
                alert(data.error || 'Failed to claim reward');
            }
        } catch (error) {
            console.error('Error claiming reward:', error);
            alert('Failed to claim reward');
        }
    }

    // Set Pterodactyl API configuration
    setPterodactylConfig(apiKey, baseUrl) {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        console.log('Pterodactyl API configured');
        this.fetchServerData();
    }

    // Fetch server data from Pterodactyl API
    async fetchServerData() {
        if (!this.apiKey || !this.baseUrl) {
            console.log('API key or base URL not configured');
            return;
        }

        try {
            const response = await fetch(`${this.baseUrl}/api/client`, {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json',
                    'Accept': 'Application/vnd.pterodactyl.v1+json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateServersDisplay(data.data);
                this.updateResourcesFromAPI(data.data);
            } else {
                console.error('Failed to fetch server data:', response.status);
            }
        } catch (error) {
            console.error('Error fetching server data:', error);
        }
    }

    // Update servers display with real data
    updateServersDisplay(servers) {
        const serversList = document.getElementById('serversList');
        
        if (!servers || servers.length === 0) {
            serversList.innerHTML = `
                <div class="no-servers">
                    <p>No servers found. Create your first server to get started!</p>
                </div>
            `;
            return;
        }

        serversList.innerHTML = servers.map(server => `
            <div class="server-item">
                <div class="server-info">
                    <div class="server-status-dot ${server.attributes.is_suspended ? 'offline' : 'online'}"></div>
                    <div>
                        <div class="server-name">${server.attributes.name}</div>
                        <div class="server-id">${server.attributes.identifier}</div>
                    </div>
                </div>
            </div>
        `).join('');

        // Update server count
        const serverCountElement = document.querySelector('.stat-number');
        if (serverCountElement) {
            serverCountElement.textContent = servers.length;
        }

        // Update online/offline count
        const onlineCount = servers.filter(s => !s.attributes.is_suspended).length;
        const offlineCount = servers.length - onlineCount;
        
        const statusElement = document.querySelector('.server-status');
        if (statusElement) {
            statusElement.innerHTML = `
                <span class="status-dot online"></span>
                <span>${onlineCount} online</span>
                <span class="separator">•</span>
                <span class="status-dot offline"></span>
                <span>${offlineCount} offline</span>
            `;
        }
    }

    // Update resources from API data
    updateResourcesFromAPI(servers) {
        // This would calculate actual resource usage from server data
        // For now, keeping at 0% as requested until API is connected
        console.log('Resource data will be updated when API is fully integrated');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});

// Function to be called when API key is provided
function connectPterodactylAPI(apiKey, baseUrl) {
    if (window.dashboard) {
        window.dashboard.setPterodactylConfig(apiKey, baseUrl);
    }
}

// Example usage (uncomment when you have the API key):
// connectPterodactylAPI('your-api-key-here', 'https://your-panel-url.com');