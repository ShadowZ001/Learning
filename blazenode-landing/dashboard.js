// Dashboard Application
class Dashboard {
    constructor() {
        console.log('🏠 Dashboard constructor called');
        this.currentUser = null;
        this.servers = [];
        this.eggs = [];
        this.nodes = [];
        this.nests = [];
        this.userLimits = null;
        this.currentStep = 1;
        this.serverData = {};
        this.pterodactylCredentials = null;
        
        // Initialize after a short delay to ensure DOM is ready
        setTimeout(() => {
            this.init();
        }, 100);
    }

    async init() {
        console.log('🚀 Dashboard initializing...');
        
        try {
            // Setup event listeners first
            this.setupEventListeners();
            
            // Load user data
            const userLoaded = await this.loadUserData();
            
            if (!userLoaded) {
                console.log('❌ User not authenticated, redirecting to login');
                window.location.href = '/';
                return;
            }
            
            // Show home page
            this.showPage('home');
            
            // Load dashboard data
            await this.loadDashboardData();
            
            console.log('✅ Dashboard ready for:', this.currentUser.username);
            
        } catch (error) {
            console.error('❌ Dashboard init error:', error);
            window.location.href = '/';
        }
    }

    // Load user data with retry mechanism
    async loadUserData() {
        try {
            console.log('👤 Fetching user data...');
            
            const response = await fetch('/api/user', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });
            
            console.log('User API response status:', response.status);
            
            if (response.ok) {
                this.currentUser = await response.json();
                console.log('✅ User data loaded:', this.currentUser.username);
                
                // Update username immediately
                const usernameEl = document.getElementById('username');
                if (usernameEl) {
                    usernameEl.textContent = this.currentUser.username;
                }
                
                // Show admin menu if user is admin
                if (this.currentUser.isAdmin) {
                    const adminMenu = document.querySelector('.admin-only');
                    if (adminMenu) {
                        adminMenu.style.display = 'block';
                        console.log('✅ Admin menu shown');
                    }
                }
                
                // Update coins display
                this.updateCoinsDisplay();
                
                return true;
            } else if (response.status === 401) {
                console.log('❌ User not authenticated, redirecting to login');
                // Add small delay to prevent redirect loops
                setTimeout(() => {
                    window.location.href = '/';
                }, 100);
                return false;
            } else {
                console.log('❌ Server error:', response.status);
                // Retry once after a short delay
                await new Promise(resolve => setTimeout(resolve, 1000));
                return this.loadUserData();
            }
        } catch (error) {
            console.error('❌ Error loading user data:', error);
            // Add small delay to prevent redirect loops
            setTimeout(() => {
                window.location.href = '/';
            }, 100);
            return false;
        }
    }

    // Update coins display
    updateCoinsDisplay() {
        const welcomeSection = document.querySelector('.welcome-section');
        let coinsDisplay = document.querySelector('.coins-display');
        
        if (!coinsDisplay && welcomeSection) {
            coinsDisplay = document.createElement('div');
            coinsDisplay.className = 'coins-display';
            coinsDisplay.style.cssText = 'margin-top: 8px; color: #fbbf24; font-weight: 600; font-size: 14px;';
            welcomeSection.appendChild(coinsDisplay);
        }
        
        if (coinsDisplay && this.currentUser) {
            coinsDisplay.innerHTML = `💰 ${this.formatCoins(this.currentUser.coins)} BlazeCoins`;
        }
    }
    
    // Format coins display
    formatCoins(coins) {
        const num = parseFloat(coins);
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'k';
        } else if (num % 1 === 0) {
            return num.toString();
        } else {
            return num.toFixed(1);
        }
    }
    
    // Initialize AFK page
    initAFKPage() {
        console.log('Initializing AFK page...');
        
        // Initialize AFK system
        if (!window.afkSystem) {
            window.afkSystem = new AFKSystem(this);
        }
        
        // Initialize Pong game
        if (!window.pongGame) {
            window.pongGame = new PongGame();
        }
        
        // Setup event listeners
        this.setupAFKListeners();
    }
    
    // Setup AFK event listeners
    setupAFKListeners() {
        const startBtn = document.getElementById('startAfkBtn');
        const stopBtn = document.getElementById('stopAfkBtn');
        const startGameBtn = document.getElementById('startGameBtn');
        const pauseGameBtn = document.getElementById('pauseGameBtn');
        
        if (startBtn) {
            startBtn.addEventListener('click', () => {
                window.afkSystem.startAFK();
            });
        }
        
        if (stopBtn) {
            stopBtn.addEventListener('click', () => {
                window.afkSystem.stopAFK();
            });
        }
        
        if (startGameBtn) {
            startGameBtn.addEventListener('click', () => {
                window.pongGame.startGame();
            });
        }
        
        if (pauseGameBtn) {
            pauseGameBtn.addEventListener('click', () => {
                window.pongGame.pauseGame();
            });
        }
        
        const resetGameBtn = document.getElementById('resetGameBtn');
        const moveUpBtn = document.getElementById('moveUpBtn');
        const moveDownBtn = document.getElementById('moveDownBtn');
        
        if (resetGameBtn) {
            resetGameBtn.addEventListener('click', () => {
                window.pongGame.resetGame();
            });
        }
        
        if (moveUpBtn) {
            moveUpBtn.addEventListener('mousedown', () => {
                window.pongGame.setMobileControl('up', true);
            });
            moveUpBtn.addEventListener('mouseup', () => {
                window.pongGame.setMobileControl('up', false);
            });
            moveUpBtn.addEventListener('touchstart', (e) => {
                e.preventDefault();
                window.pongGame.setMobileControl('up', true);
            });
            moveUpBtn.addEventListener('touchend', (e) => {
                e.preventDefault();
                window.pongGame.setMobileControl('up', false);
            });
        }
        
        if (moveDownBtn) {
            moveDownBtn.addEventListener('mousedown', () => {
                window.pongGame.setMobileControl('down', true);
            });
            moveDownBtn.addEventListener('mouseup', () => {
                window.pongGame.setMobileControl('down', false);
            });
            moveDownBtn.addEventListener('touchstart', (e) => {
                e.preventDefault();
                window.pongGame.setMobileControl('down', true);
            });
            moveDownBtn.addEventListener('touchend', (e) => {
                e.preventDefault();
                window.pongGame.setMobileControl('down', false);
            });
        }
    }
    
    // Load promotions
    async loadPromotions() {
        try {
            const response = await fetch('/api/promotions', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updatePromotionsDisplay(data.promotions || []);
            } else {
                console.error('Failed to load promotions');
            }
        } catch (error) {
            console.error('Error loading promotions:', error);
        }
    }
    
    // Update promotions display
    updatePromotionsDisplay(promotions) {
        const promotionsGrid = document.getElementById('promotionsGrid');
        
        if (!promotions || promotions.length === 0) {
            promotionsGrid.innerHTML = `
                <div class="no-promotions">
                    <p>No server promotions yet. Be the first to promote your server!</p>
                </div>
            `;
            return;
        }
        
        promotionsGrid.innerHTML = promotions.map(promo => `
            <div class="promotion-item ${promo.boosted ? 'boosted' : ''}">
                <div class="promotion-header">
                    <div>
                        <div class="promotion-title">${promo.serverName}</div>
                        <div class="promotion-ip">${promo.serverIP}</div>
                    </div>
                </div>
                <div class="promotion-description">${promo.description}</div>
                <div class="promotion-footer">
                    <div class="promotion-author">by ${promo.author}</div>
                    <div class="promotion-actions">
                        <button class="copy-btn" onclick="copyServerIP('${promo.serverIP}')">
                            <i class="fas fa-copy"></i> Copy IP
                        </button>
                        ${promo.author === this.currentUser?.username ? 
                            `<button class="boost-btn" onclick="boostPromotion('${promo._id}')">
                                <i class="fas fa-rocket"></i> Boost (100 coins)
                            </button>` : ''
                        }
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Load dashboard data
    async loadDashboardData() {
        await Promise.all([
            this.loadServers(),
            this.loadResourceUsage()
        ]);
        this.updateDashboardStats();
    }

    // Load servers from API
    async loadServers() {
        try {
            console.log('📊 Loading servers...');
            const response = await fetch('/api/servers', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.servers = data.servers || [];
                console.log('✅ Servers loaded:', this.servers.length);
                
                this.updateServersDisplay();
                this.updateServersTable();
                this.updateServersGrid();
            } else {
                console.error('❌ Failed to load servers:', response.status);
                this.servers = [];
                this.updateServersDisplay();
                this.updateServersTable();
                this.updateServersGrid();
            }
        } catch (error) {
            console.error('❌ Error loading servers:', error);
            this.servers = [];
            this.updateServersDisplay();
            this.updateServersTable();
            this.updateServersGrid();
        }
    }

    // Load resource usage
    async loadResourceUsage() {
        try {
            const response = await fetch('/api/resource-usage', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateResourceCards(data);
            }
        } catch (error) {
            console.error('Error loading resource usage:', error);
            // Set default values if API fails
            this.updateResourceCards({
                memory: { used: 0, total: 0 },
                cpu: { used: 0, total: 0 },
                disk: { used: 0, total: 0 }
            });
        }
    }

    // Update resource cards
    updateResourceCards(data) {
        // Memory - show allocated vs total available (including purchased)
        const memoryUsed = Math.round(data.memory.used || 0); // MB allocated to servers
        const memoryTotal = Math.round(data.memory.total || 2048); // MB total available (base + purchased)
        const memoryPercent = memoryTotal > 0 ? Math.round((memoryUsed / memoryTotal) * 100) : 0;
        
        const memoryUsedGB = (memoryUsed / 1024).toFixed(1);
        const memoryTotalGB = (memoryTotal / 1024).toFixed(1);
        
        const memoryEl = document.getElementById('memory-usage');
        const memoryProgressEl = document.getElementById('memory-progress');
        const memoryPercentEl = document.getElementById('memory-percent');
        
        if (memoryEl) memoryEl.textContent = `${memoryUsedGB}GB / ${memoryTotalGB}GB`;
        if (memoryProgressEl) memoryProgressEl.style.width = `${memoryPercent}%`;
        if (memoryPercentEl) memoryPercentEl.textContent = `${memoryPercent}% allocated`;

        // CPU - show allocated vs total available (including purchased)
        const cpuUsed = Math.round(data.cpu.used || 0); // % allocated to servers
        const cpuTotal = Math.round(data.cpu.total || 100); // % total available (base + purchased)
        const cpuPercent = cpuTotal > 0 ? Math.round((cpuUsed / cpuTotal) * 100) : 0;
        
        const cpuEl = document.getElementById('cpu-usage');
        const cpuProgressEl = document.getElementById('cpu-progress');
        const cpuPercentEl = document.getElementById('cpu-percent');
        
        if (cpuEl) cpuEl.textContent = `${cpuUsed}% / ${cpuTotal}%`;
        if (cpuProgressEl) cpuProgressEl.style.width = `${cpuPercent}%`;
        if (cpuPercentEl) cpuPercentEl.textContent = `${cpuPercent}% allocated`;

        // Storage - show allocated vs total available (including purchased)
        const storageUsed = Math.round(data.disk.used || 0); // MB allocated to servers
        const storageTotal = Math.round(data.disk.total || 5120); // MB total available (base + purchased)
        const storagePercent = storageTotal > 0 ? Math.round((storageUsed / storageTotal) * 100) : 0;
        
        const storageUsedGB = (storageUsed / 1024).toFixed(1);
        const storageTotalGB = (storageTotal / 1024).toFixed(1);
        
        const storageEl = document.getElementById('storage-usage');
        const storageProgressEl = document.getElementById('storage-progress');
        const storagePercentEl = document.getElementById('storage-percent');
        
        if (storageEl) storageEl.textContent = `${storageUsedGB}GB / ${storageTotalGB}GB`;
        if (storageProgressEl) storageProgressEl.style.width = `${storagePercent}%`;
        if (storagePercentEl) storagePercentEl.textContent = `${storagePercent}% allocated`;

        // Servers - show used vs available slots (including purchased)
        const serverCount = data.slots?.used || this.servers.length;
        const serverLimit = data.slots?.total || 2;
        const serverPercent = serverLimit > 0 ? Math.round((serverCount / serverLimit) * 100) : 0;
        
        const serversEl = document.getElementById('servers-count');
        const serversProgressEl = document.getElementById('servers-progress');
        const serversPercentEl = document.getElementById('servers-percent');
        
        if (serversEl) serversEl.textContent = `${serverCount} / ${serverLimit}`;
        if (serversProgressEl) serversProgressEl.style.width = `${serverPercent}%`;
        if (serversPercentEl) serversPercentEl.textContent = `${serverPercent}% used`;
        
        console.log('✅ Resource cards updated:', {
            memory: `${memoryUsedGB}GB / ${memoryTotalGB}GB (${memoryPercent}%)`,
            cpu: `${cpuUsed}% / ${cpuTotal}% (${cpuPercent}%)`,
            storage: `${storageUsedGB}GB / ${storageTotalGB}GB (${storagePercent}%)`,
            servers: `${serverCount} / ${serverLimit} (${serverPercent}%)`
        });
    }

    // Update dashboard stats
    updateDashboardStats() {
        const totalServers = this.servers.length;
        const onlineServers = this.servers.filter(s => !s.attributes.suspended).length;
        const offlineServers = totalServers - onlineServers;

        document.getElementById('total-servers').textContent = totalServers;
        document.getElementById('online-count').textContent = `${onlineServers} online`;
        document.getElementById('offline-count').textContent = `${offlineServers} offline`;
    }

    // Update servers display on home page
    updateServersDisplay() {
        const serversList = document.getElementById('serversList');
        
        if (!this.servers || this.servers.length === 0) {
            serversList.innerHTML = `
                <div class="no-servers">
                    <p>No servers found. Create your first server to get started!</p>
                </div>
            `;
            return;
        }

        serversList.innerHTML = this.servers.map(server => `
            <div class="server-item">
                <div class="server-info" onclick="openServerPanel('${server.attributes.identifier}')" style="cursor: pointer; flex: 1;">
                    <div class="status-dot ${server.attributes.suspended ? 'offline' : 'online'}"></div>
                    <div>
                        <div class="server-name">${server.attributes.name}</div>
                        <div class="server-id">${server.attributes.identifier}</div>
                    </div>
                </div>
                <div class="server-specs" onclick="openServerPanel('${server.attributes.identifier}')" style="cursor: pointer; flex: 1;">
                    <div>RAM: ${(server.attributes.limits.memory / 1024).toFixed(1)}GB | CPU: ${server.attributes.limits.cpu}% | Disk: ${(server.attributes.limits.disk / 1024).toFixed(1)}GB</div>
                    <div class="server-link">Click to manage →</div>
                </div>
                <div class="server-actions" style="display: flex; gap: 8px; align-items: center;">
                    <button class="btn-edit" onclick="event.stopPropagation(); editServer('${server.attributes.identifier}')" style="padding: 4px 8px; font-size: 12px;">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-danger" onclick="event.stopPropagation(); deleteServer('${server.attributes.identifier}', '${server.attributes.name}')" style="padding: 4px 8px; font-size: 12px;">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    // Update servers table
    updateServersTable() {
        const tableBody = document.getElementById('serversTableBody');
        
        if (!this.servers || this.servers.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="loading-row">No servers found</td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = this.servers.map(server => {
            const status = server.attributes.suspended ? 'offline' : 'online';
            const memoryUsed = 0; // Would come from real-time stats
            const cpuUsed = 0; // Would come from real-time stats
            const diskUsed = 0; // Would come from real-time stats
            
            return `
                <tr>
                    <td>
                        <div class="server-name">${server.attributes.name}</div>
                        <div class="server-id">${server.attributes.identifier}</div>
                    </td>
                    <td>
                        <span class="status-badge ${status}">${status.charAt(0).toUpperCase() + status.slice(1)}</span>
                    </td>
                    <td>${memoryUsed}MB / ${server.attributes.limits.memory}MB</td>
                    <td>${cpuUsed}% / ${server.attributes.limits.cpu}%</td>
                    <td>${diskUsed}MB / ${server.attributes.limits.disk}MB</td>
                    <td>
                        <button class="btn-secondary" onclick="openServerPanel('${server.attributes.identifier}')" style="padding: 6px 12px; font-size: 12px; margin-right: 5px;">Manage</button>
                        <button class="btn-edit" onclick="editServer('${server.attributes.identifier}')" style="padding: 6px 12px; font-size: 12px; margin-right: 5px;">Edit</button>
                        <button class="btn-danger" onclick="deleteServer('${server.attributes.identifier}', '${server.attributes.name}')" style="padding: 6px 12px; font-size: 12px;">Delete</button>
                    </td>
                </tr>
            `;
        }).join('');
    }
    
    // Update servers grid (mobile)
    updateServersGrid() {
        const serversGrid = document.getElementById('serversGrid');
        
        if (!this.servers || this.servers.length === 0) {
            serversGrid.innerHTML = `
                <div class="no-servers">
                    <p>No servers found. Create your first server to get started!</p>
                </div>
            `;
            return;
        }

        serversGrid.innerHTML = this.servers.map(server => {
            const status = server.attributes.suspended ? 'offline' : 'online';
            
            return `
                <div class="server-card">
                    <div class="server-card-header">
                        <div class="server-card-info">
                            <h4>${server.attributes.name}</h4>
                            <p>${server.attributes.identifier}</p>
                        </div>
                        <div class="server-card-status">
                            <span class="status-badge ${status}">${status.charAt(0).toUpperCase() + status.slice(1)}</span>
                        </div>
                    </div>
                    
                    <div class="server-resources">
                        <div class="resource-item">
                            <div class="resource-item-label">Memory</div>
                            <div class="resource-item-value">${(server.attributes.limits.memory / 1024).toFixed(1)}GB</div>
                        </div>
                        <div class="resource-item">
                            <div class="resource-item-label">CPU</div>
                            <div class="resource-item-value">${server.attributes.limits.cpu}%</div>
                        </div>
                        <div class="resource-item">
                            <div class="resource-item-label">Disk</div>
                            <div class="resource-item-value">${(server.attributes.limits.disk / 1024).toFixed(1)}GB</div>
                        </div>
                    </div>
                    
                    <div class="server-card-actions">
                        <button class="server-action-btn btn-manage" onclick="openServerPanel('${server.attributes.identifier}')">
                            <i class="fas fa-external-link-alt"></i>
                            Manage
                        </button>
                        <button class="server-action-btn btn-edit" onclick="editServer('${server.attributes.identifier}')">
                            <i class="fas fa-edit"></i>
                            Edit
                        </button>
                        <button class="server-action-btn btn-danger" onclick="deleteServer('${server.attributes.identifier}', '${server.attributes.name}')">
                            <i class="fas fa-trash"></i>
                            Delete
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    // Load nests for server creation
    async loadNests() {
        try {
            console.log('Loading nests...');
            const response = await fetch('/api/nests', {
                credentials: 'include',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.nests = data.nests || [];
                console.log('Nests loaded:', this.nests.length);
                
                if (this.nests.length === 0) {
                    this.showNotification('No server nests available', 'error');
                } else {
                    this.updateNestsDropdown();
                }
            } else {
                const errorData = await response.json();
                console.error('Failed to load nests:', response.status, errorData);
                this.showNotification(errorData.error || 'Failed to load server nests', 'error');
            }
        } catch (error) {
            console.error('Error loading nests:', error);
            this.showNotification('Connection error while loading nests', 'error');
        }
    }

    // Load eggs for specific nest
    async loadEggsForNest(nestId) {
        try {
            console.log('Loading eggs for nest:', nestId);
            const response = await fetch(`/api/nests/${nestId}/eggs`, {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.eggs = data.eggs || [];
                console.log('Eggs loaded:', this.eggs.length);
                this.updateEggsDropdown();
            } else {
                console.error('Failed to load eggs:', response.status);
                this.showNotification('Failed to load server types', 'error');
            }
        } catch (error) {
            console.error('Error loading eggs:', error);
            this.showNotification('Error loading server types', 'error');
        }
    }



    // Update nests dropdown
    updateNestsDropdown() {
        const select = document.getElementById('serverNest');
        if (!select) return;
        
        select.innerHTML = '<option value="">Select nest</option>';
        
        this.nests.forEach(nest => {
            const option = document.createElement('option');
            option.value = nest.attributes.id;
            option.textContent = nest.attributes.name;
            select.appendChild(option);
        });
        
        console.log('Nests dropdown updated with', this.nests.length, 'options');
    }

    // Update eggs dropdown
    updateEggsDropdown() {
        const select = document.getElementById('serverEgg');
        if (!select) return;
        
        select.innerHTML = '<option value="">Select server type</option>';
        
        this.eggs.forEach(egg => {
            const option = document.createElement('option');
            option.value = egg.attributes.id;
            option.textContent = egg.attributes.name;
            select.appendChild(option);
        });
        
        console.log('Eggs dropdown updated with', this.eggs.length, 'options');
    }



    // Setup event listeners
    setupEventListeners() {
        // Sidebar navigation
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const page = e.currentTarget.dataset.page;
                this.showPage(page);
            });
        });

        // Claim reward button
        const claimBtn = document.getElementById('claimBtn');
        if (claimBtn) {
            claimBtn.addEventListener('click', () => {
                this.claimDailyReward();
            });
        }

        // Use event delegation for all button clicks
        document.addEventListener('click', (e) => {
            // Handle create server button
            if (e.target.id === 'createServerBtn' || e.target.closest('#createServerBtn')) {
                console.log('🎮 Create server button clicked');
                e.preventDefault();
                this.showCreateServer();
            }
            
            // Handle new server button in servers page
            if (e.target.classList.contains('new-server-btn') || e.target.closest('.new-server-btn')) {
                console.log('🎮 New server button clicked');
                e.preventDefault();
                this.showCreateServer();
            }

            // Handle back to servers button
            if (e.target.id === 'backToServersBtn') {
                console.log('Back to servers clicked');
                e.preventDefault();
                this.showPage('servers');
            }

            // Handle next step button
            if (e.target.id === 'nextStepBtn') {
                console.log('Next step clicked');
                e.preventDefault();
                this.nextStep();
            }

            // Handle previous step button
            if (e.target.id === 'prevStepBtn') {
                console.log('Previous step clicked');
                e.preventDefault();
                this.showPage('create-server-step1');
            }

            // Handle create server final button
            if (e.target.id === 'createServerFinalBtn') {
                console.log('Create server final clicked');
                e.preventDefault();
                this.createServerFinal();
            }
        });

        // Nest selection change - use event delegation
        document.addEventListener('change', (e) => {
            if (e.target.id === 'serverNest') {
                const nestId = e.target.value;
                console.log('Nest changed to:', nestId);
                if (nestId) {
                    this.loadEggsForNest(nestId);
                } else {
                    const eggSelect = document.getElementById('serverEgg');
                    if (eggSelect) {
                        eggSelect.innerHTML = '<option value="">Select nest first...</option>';
                    }
                }
            }
        });

        // Form validation for step 2 - use event delegation
        document.addEventListener('input', (e) => {
            if (['serverRam', 'serverCpu', 'serverDisk'].includes(e.target.id)) {
                this.validateResources();
            }
        });
    }

    // Show page
    showPage(pageName) {
        console.log('📝 Showing page:', pageName);
        
        // Update sidebar only for main pages
        if (!pageName.startsWith('create-server')) {
            document.querySelectorAll('.menu-item').forEach(item => {
                item.classList.remove('active');
            });
            
            const menuItem = document.querySelector(`[data-page="${pageName}"]`);
            if (menuItem) {
                menuItem.classList.add('active');
            }
        }

        // Update content
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        
        // Handle create server pages
        let targetPage;
        if (pageName.startsWith('create-server')) {
            targetPage = document.getElementById(pageName);
        } else {
            targetPage = document.getElementById(`${pageName}-page`);
        }
        
        if (targetPage) {
            targetPage.classList.add('active');
            console.log('✅ Page activated:', pageName);
        } else {
            console.error('❌ Page not found:', pageName);
        }

        // Close mobile menu when navigating
        if (window.innerWidth <= 768) {
            closeMobileMenu();
        }
        
        // Stop AFK when navigating away from AFK page
        if (pageName !== 'afk' && window.afkSystem && window.afkSystem.isActive) {
            window.afkSystem.stopAFK();
        }
        
        // Load page-specific data
        if (pageName === 'servers') {
            console.log('📊 Loading servers data...');
            this.loadServers();
        } else if (pageName === 'profile') {
            console.log('👤 Loading profile data...');
            this.loadProfileData();
        } else if (pageName === 'leaderboard') {
            console.log('🏆 Loading leaderboard data...');
            this.loadLeaderboard();
        } else if (pageName === 'admin') {
            console.log('🔧 Loading admin data...');
            this.loadAdminData();
            // Load Discord link from storage
            const savedDiscordLink = localStorage.getItem('discordLink');
            if (savedDiscordLink) {
                const discordLinkInput = document.getElementById('discordLink');
                if (discordLinkInput) {
                    discordLinkInput.value = savedDiscordLink;
                }
            }
        } else if (pageName === 'store') {
            console.log('🛍️ Loading store data...');
            this.loadStoreData();
        } else if (pageName === 'afk') {
            console.log('🕰️ Loading AFK page...');
            this.initAFKPage();
        } else if (pageName === 'promotion') {
            console.log('📢 Loading promotion page...');
            this.loadPromotions();
        } else if (pageName === 'earn') {
            console.log('💰 Loading earn coins page...');
            this.loadEarnData();
        } else if (pageName === 'home') {
            // Stop AFK when leaving AFK page
            if (window.afkSystem && window.afkSystem.isActive) {
                window.afkSystem.stopAFK();
            }
            // Refresh home page data
            this.loadDashboardData();
        }
    }

    // Claim daily reward
    async claimDailyReward() {
        const claimBtn = document.getElementById('claimBtn');
        
        try {
            const response = await fetch('/api/claim-reward', {
                method: 'POST',
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                claimBtn.textContent = 'Claimed! ✓';
                claimBtn.disabled = true;
                
                this.currentUser.coins = data.coins;
                this.updateCoinsDisplay();
                
                document.getElementById('streak').textContent = data.streak;
                
                // Show success message
                this.showNotification('Daily reward claimed! +25 coins', 'success');
            } else {
                this.showNotification(data.error || 'Failed to claim reward', 'error');
            }
        } catch (error) {
            console.error('Error claiming reward:', error);
            this.showNotification('Failed to claim reward', 'error');
        }
    }

    // Show notification
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        if (type === 'success') {
            notification.style.background = '#10b981';
        } else if (type === 'error') {
            notification.style.background = '#ef4444';
        } else {
            notification.style.background = '#3b82f6';
        }
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Validate resources for step 2
    validateResources() {
        const ram = parseInt(document.getElementById('serverRam').value);
        const cpu = parseInt(document.getElementById('serverCpu').value);
        const disk = parseInt(document.getElementById('serverDisk').value);
        
        const validationMessage = document.getElementById('validation-message');
        let errors = [];
        
        if (!this.userLimits) {
            errors.push('User limits not loaded');
        } else {
            if (ram < this.userLimits.minMemory) {
                errors.push(`RAM must be at least ${this.userLimits.minMemory}MB`);
            }
            if (ram > this.userLimits.maxMemory) {
                errors.push(`RAM cannot exceed ${this.userLimits.maxMemory}MB`);
            }
            if (cpu < this.userLimits.minCpu) {
                errors.push(`CPU must be at least ${this.userLimits.minCpu}%`);
            }
            if (cpu > this.userLimits.maxCpu) {
                errors.push(`CPU cannot exceed ${this.userLimits.maxCpu}%`);
            }
            if (disk < this.userLimits.minDisk) {
                errors.push(`Disk must be at least ${this.userLimits.minDisk}MB`);
            }
            if (disk > this.userLimits.maxDisk) {
                errors.push(`Disk cannot exceed ${this.userLimits.maxDisk}MB`);
            }
        }
        
        if (errors.length > 0) {
            validationMessage.className = 'validation-message error';
            validationMessage.style.display = 'block';
            validationMessage.textContent = errors.join(', ');
            return false;
        } else {
            validationMessage.style.display = 'none';
            return true;
        }
    }

    // Create server final step
    async createServerFinal() {
        console.log('🚀 Starting server creation...');
        
        // Validate resources first
        if (!this.validateResources()) {
            console.log('❌ Resource validation failed');
            return;
        }

        // Get form values
        const serverName = document.getElementById('serverName')?.value?.trim();
        const serverEgg = document.getElementById('serverEgg')?.value;
        const serverRam = document.getElementById('serverRam')?.value;
        const serverCpu = document.getElementById('serverCpu')?.value;
        const serverDisk = document.getElementById('serverDisk')?.value;

        console.log('Form values:', { serverName, serverEgg, serverRam, serverCpu, serverDisk });

        // Validate all required fields
        if (!serverName) {
            this.showNotification('Server name is required', 'error');
            return;
        }
        
        if (!serverEgg) {
            this.showNotification('Server type is required', 'error');
            return;
        }
        
        if (!serverRam || !serverCpu || !serverDisk) {
            this.showNotification('All resource fields are required', 'error');
            return;
        }

        const serverData = {
            name: serverName,
            egg: parseInt(serverEgg),
            memory: parseInt(serverRam),
            cpu: parseInt(serverCpu),
            disk: parseInt(serverDisk)
        };
        
        console.log('Server data to send:', serverData);

        console.log('Creating server with data:', serverData);
        
        // Show loading state
        const createBtn = document.getElementById('createServerFinalBtn');
        const originalText = createBtn.textContent;
        createBtn.textContent = 'Creating Server...';
        createBtn.disabled = true;

        try {
            const response = await fetch('/api/create-server', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(serverData)
            });

            console.log('Server creation response status:', response.status);
            const data = await response.json();
            console.log('Server creation response:', data);

            if (response.ok && data.success) {
                this.showNotification('Server created successfully!', 'success');
                
                // Store Pterodactyl credentials
                if (data.pterodactylUser) {
                    this.pterodactylCredentials = data.pterodactylUser;
                    
                    // Show success message with server details
                    const successMsg = `🎉 Server "${data.server.name}" created successfully!\n\n📊 Resources:\n${data.resources.memory}\n${data.resources.cpu}\n${data.resources.disk}\n\n🌐 Access your server at: ${data.pterodactylUser.panelUrl}`;
                    alert(successMsg);
                }
                
                // Reset form
                document.getElementById('serverName').value = '';
                document.getElementById('serverNest').selectedIndex = 0;
                document.getElementById('serverEgg').innerHTML = '<option value="">Select nest first...</option>';
                document.getElementById('serverRam').value = '1024';
                document.getElementById('serverCpu').value = '50';
                document.getElementById('serverDisk').value = '2048';
                
                this.showPage('servers');
                await this.loadServers();
                await this.loadDashboardData(); // Refresh resource usage
            } else {
                const errorMsg = data.error || data.details || 'Failed to create server';
                this.showNotification(errorMsg, 'error');
                console.error('Server creation failed:', data);
            }
        } catch (error) {
            console.error('❌ Server creation error:', error);
            
            let errorMessage = 'Failed to create server';
            if (error.message) {
                errorMessage = error.message;
            }
            
            this.showNotification(errorMessage, 'error');
        } finally {
            createBtn.textContent = originalText;
            createBtn.disabled = false;
        }
    }

    // Load user limits
    async loadUserLimits() {
        try {
            const response = await fetch('/api/user-limits', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.userLimits = data.limits;
                console.log('User limits loaded:', this.userLimits);
            }
        } catch (error) {
            console.error('Error loading user limits:', error);
        }
    }

    // Show create server page
    showCreateServer() {
        console.log('🎮 Showing create server page');
        
        // Reset form data
        this.resetCreateServerForm();
        
        // Show step 1
        this.showPage('create-server-step1');
        
        // Load nests after a short delay
        setTimeout(() => {
            this.loadNests();
        }, 100);
    }

    // Reset create server form
    resetCreateServerForm() {
        const serverNameInput = document.getElementById('serverName');
        const serverNestSelect = document.getElementById('serverNest');
        const serverEggSelect = document.getElementById('serverEgg');
        const serverRamInput = document.getElementById('serverRam');
        const serverCpuInput = document.getElementById('serverCpu');
        const serverDiskInput = document.getElementById('serverDisk');
        
        if (serverNameInput) serverNameInput.value = '';
        if (serverNestSelect) serverNestSelect.selectedIndex = 0;
        if (serverEggSelect) serverEggSelect.innerHTML = '<option value="">Select nest first...</option>';
        if (serverRamInput) serverRamInput.value = '1024';
        if (serverCpuInput) serverCpuInput.value = '50';
        if (serverDiskInput) serverDiskInput.value = '2048';
        
        // Clear validation message
        const validationMessage = document.getElementById('validation-message');
        if (validationMessage) {
            validationMessage.style.display = 'none';
        }
    }

    // Next step validation
    nextStep() {
        const serverName = document.getElementById('serverName')?.value?.trim();
        const serverNest = document.getElementById('serverNest')?.value;
        const serverEgg = document.getElementById('serverEgg')?.value;
        
        console.log('Next step validation:', { serverName, serverNest, serverEgg });
        
        if (!serverName) {
            this.showNotification('Please enter a server name', 'error');
            return;
        }
        
        if (serverName.length < 3) {
            this.showNotification('Server name must be at least 3 characters', 'error');
            return;
        }
        
        if (!serverNest) {
            this.showNotification('Please select a server nest', 'error');
            return;
        }
        
        if (!serverEgg) {
            this.showNotification('Please select a server type', 'error');
            return;
        }
        
        console.log('✅ Step 1 validation passed, moving to step 2');
        this.showPage('create-server-step2');
    }

    // Load profile data
    async loadProfileData() {
        try {
            if (this.currentUser) {
                // Update profile information
                document.getElementById('profile-username').textContent = this.currentUser.username;
                document.getElementById('profile-email').textContent = `${this.currentUser.username}@gmail.com`;
                document.getElementById('profile-coins').textContent = this.formatCoins(this.currentUser.coins);
                document.getElementById('profile-servers').textContent = `${this.currentUser.serverCount || 0}/2`;
                
                // Set joined date
                document.getElementById('profile-joined').textContent = 'Recently';
                
                // Update Pterodactyl credentials
                document.getElementById('pterodactyl-username').textContent = this.currentUser.username;
                document.getElementById('pterodactyl-email').textContent = `${this.currentUser.username}@gmail.com`;
                
                // Store password for copy function
                window.pterodactylPassword = this.currentUser.username;
                
                console.log('✅ Profile data loaded');
            }
        } catch (error) {
            console.error('Error loading profile data:', error);
        }
    }

    // Load leaderboard data
    async loadLeaderboard() {
        try {
            const response = await fetch('/api/leaderboard', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateLeaderboard(data.users);
                

            }
        } catch (error) {
            console.error('Error loading leaderboard:', error);
        }
    }

    // Update leaderboard display
    updateLeaderboard(users) {
        const leaderboardList = document.getElementById('leaderboardList');
        
        if (!users || users.length === 0) {
            leaderboardList.innerHTML = '<div class="loading">No users found</div>';
            return;
        }
        
        leaderboardList.innerHTML = users.map((user, index) => {
            const rank = index + 1;
            const trophy = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : `#${rank}`;
            
            return `
                <div class="leaderboard-item">
                    <div class="leaderboard-rank">${trophy}</div>
                    <div class="leaderboard-user">
                        <div class="leaderboard-username">${user.username}</div>
                    </div>
                    <div class="leaderboard-coins">💰 ${this.formatCoins(user.coins)} coins</div>
                </div>
            `;
        }).join('');
    }

    // Load earn data
    async loadEarnData() {
        try {
            // Update earning stats
            this.updateEarnStats();
            
            // Load Linkvertise URL from localStorage or use default
            const savedLinkvertiseUrl = localStorage.getItem('linkvertiseUrl') || 'https://dash.blazenode.site';
            window.currentLinkvertiseUrl = savedLinkvertiseUrl;
            
            console.log('✅ Earn data loaded');
        } catch (error) {
            console.error('Error loading earn data:', error);
        }
    }
    
    // Update earning stats
    updateEarnStats() {
        if (this.currentUser) {
            // Get stats from localStorage or set defaults
            const earnStats = JSON.parse(localStorage.getItem('earnStats') || '{}');
            
            document.getElementById('totalEarned').textContent = this.formatCoins(earnStats.totalEarned || 0);
            document.getElementById('todayEarned').textContent = this.formatCoins(earnStats.todayEarned || 0);
            document.getElementById('linkvertiseCompleted').textContent = earnStats.linkvertiseCompleted || 0;
            document.getElementById('currentBalance').textContent = this.formatCoins(this.currentUser.coins);
        }
    }

    // Load admin data
    async loadAdminData() {
        try {
            const response = await fetch('/api/admin/users', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateUsersGrid(data.users);
            } else {
                this.showNotification('Access denied', 'error');
            }
            
            // Load Linkvertise URL for admin
            const savedLinkvertiseUrl = localStorage.getItem('linkvertiseUrl') || 'https://dash.blazenode.site';
            const linkvertiseUrlInput = document.getElementById('linkvertiseUrl');
            const currentLinkvertiseUrl = document.getElementById('currentLinkvertiseUrl');
            
            if (linkvertiseUrlInput) {
                linkvertiseUrlInput.value = savedLinkvertiseUrl;
            }
            if (currentLinkvertiseUrl) {
                currentLinkvertiseUrl.textContent = savedLinkvertiseUrl;
            }
        } catch (error) {
            console.error('Error loading admin data:', error);
        }
    }

    // Update users grid
    updateUsersGrid(users) {
        const usersGrid = document.getElementById('usersGrid');
        
        if (!users || users.length === 0) {
            usersGrid.innerHTML = '<div class="loading">No users found</div>';
            return;
        }
        
        usersGrid.innerHTML = users.map(user => `
            <div class="user-box">
                <div class="user-info">
                    <div class="user-username">${user.username}</div>
                    <div class="user-details">Coins: ${user.coins}</div>
                    <div class="user-details">Servers: ${user.serverCount || 0}</div>
                    <div class="user-details">ID: ${user._id}</div>
                </div>
                <div class="user-actions">
                    <button class="btn-small btn-edit" onclick="editUser('${user._id}', '${user.username}')">Edit</button>
                    <button class="btn-small btn-delete" onclick="deleteUser('${user._id}', '${user.username}')">Delete</button>
                </div>
            </div>
        `).join('');
    }
}

// Global logout function
function logout() {
    fetch('/api/logout', {
        method: 'POST',
        credentials: 'include'
    }).then(() => {
        window.location.href = '/';
    }).catch(() => {
        window.location.href = '/';
    });
}

// Initialize dashboard
let dashboard;

// Ensure DOM is ready before initializing
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}

function initDashboard() {
    console.log('🚀 Starting dashboard initialization...');
    
    // Debug: Check if create server elements exist
    setTimeout(() => {
        const step1 = document.getElementById('create-server-step1');
        const step2 = document.getElementById('create-server-step2');
        console.log('Create server step 1 exists:', !!step1);
        console.log('Create server step 2 exists:', !!step2);
        
        const createBtn = document.getElementById('createServerBtn');
        console.log('Create server button exists:', !!createBtn);
    }, 1000);
    
    try {
        dashboard = new Dashboard();
    } catch (error) {
        console.error('❌ Failed to initialize dashboard:', error);
        // Fallback: try to load user data directly
        loadUserDataFallback();
    }
}

// Fallback function to load user data if dashboard fails
async function loadUserDataFallback() {
    try {
        console.log('🔄 Trying fallback user data load...');
        const response = await fetch('/api/user', { credentials: 'include' });
        
        if (response.ok) {
            const user = await response.json();
            console.log('✅ Fallback user data loaded:', user.username);
            
            // Update username directly
            const usernameEl = document.getElementById('username');
            if (usernameEl) {
                usernameEl.textContent = user.username;
            }
            
            // Update coins display
            const coinsDisplay = document.querySelector('.coins-display') || document.createElement('div');
            coinsDisplay.className = 'coins-display';
            coinsDisplay.style.cssText = 'margin-top: 8px; color: #fbbf24; font-weight: 600; font-size: 14px;';
            coinsDisplay.innerHTML = `💰 ${user.coins} BlazeCoins`;
            
            const welcomeSection = document.querySelector('.welcome-section');
            if (welcomeSection && !document.querySelector('.coins-display')) {
                welcomeSection.appendChild(coinsDisplay);
            }
            
        } else {
            console.log('❌ Fallback failed, redirecting to login');
            window.location.href = '/';
        }
    } catch (error) {
        console.error('❌ Fallback error:', error);
        window.location.href = '/';
    }
}

// Profile page utility functions
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        dashboard.showNotification('Copied to clipboard!', 'success');
    }).catch(() => {
        dashboard.showNotification('Failed to copy', 'error');
    });
}

function copyPterodactylUsername() {
    const username = document.getElementById('pterodactyl-username').textContent;
    copyToClipboard(username);
}

function copyPterodactylEmail() {
    const email = document.getElementById('pterodactyl-email').textContent;
    copyToClipboard(email);
}

function copyPterodactylPassword() {
    const password = window.pterodactylPassword || dashboard.currentUser?.username;
    if (password) {
        copyToClipboard(password);
    } else {
        dashboard.showNotification('Password not available', 'error');
    }
}

function togglePassword() {
    const passwordSpan = document.getElementById('pterodactyl-password');
    const toggleBtn = event.target;
    
    if (passwordSpan.classList.contains('password-hidden')) {
        passwordSpan.textContent = window.pterodactylPassword || dashboard.currentUser?.username || 'N/A';
        passwordSpan.classList.remove('password-hidden');
        toggleBtn.textContent = '🙈';
    } else {
        passwordSpan.textContent = '••••••••';
        passwordSpan.classList.add('password-hidden');
        toggleBtn.textContent = '👁️';
    }
}

// Function to open server in Pterodactyl panel
function openServerPanel(serverIdentifier) {
    const panelUrl = `https://panel.blazenode.site/server/${serverIdentifier}`;
    window.open(panelUrl, '_blank');
    dashboard.showNotification('Opening server in Pterodactyl panel...', 'info');
}

// Function to join Discord server
function joinDiscord() {
    // Get Discord link from admin settings or use default
    const discordLink = localStorage.getItem('discordLink') || 'https://discord.gg/GwXUfVjnTm';
    window.open(discordLink, '_blank');
    dashboard.showNotification('Opening Discord server...', 'info');
}

// Admin function to give coins
async function giveCoins() {
    const username = document.getElementById('adminUsername').value.trim();
    const coins = parseInt(document.getElementById('adminCoins').value);
    
    if (!username || !coins || coins <= 0) {
        dashboard.showNotification('Please enter valid username and coins amount', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/admin/give-coins', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ username, coins })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            dashboard.showNotification(`Successfully gave ${coins} coins to ${username}`, 'success');
            document.getElementById('adminUsername').value = '';
            document.getElementById('adminCoins').value = '';
            dashboard.loadLeaderboard(); // Refresh leaderboard
        } else {
            dashboard.showNotification(data.error || 'Failed to give coins', 'error');
        }
    } catch (error) {
        console.error('Error giving coins:', error);
        dashboard.showNotification('Error giving coins', 'error');
    }
}

// Admin function to edit user
function editUser(userId, currentUsername) {
    const newUsername = prompt(`Edit username for ${currentUsername}:`, currentUsername);
    const newPassword = prompt('Enter new password (leave empty to keep current):');
    
    if (!newUsername || newUsername.trim() === '') {
        dashboard.showNotification('Username cannot be empty', 'error');
        return;
    }
    
    const updateData = { username: newUsername.trim() };
    if (newPassword && newPassword.trim() !== '') {
        updateData.password = newPassword.trim();
    }
    
    fetch('/api/admin/edit-user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ userId, ...updateData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            dashboard.showNotification('User updated successfully', 'success');
            dashboard.loadAdminData();
        } else {
            dashboard.showNotification(data.error || 'Failed to update user', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating user:', error);
        dashboard.showNotification('Error updating user', 'error');
    });
}

// Admin function to delete user
function deleteUser(userId, username) {
    if (!confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) {
        return;
    }
    
    fetch('/api/admin/delete-user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ userId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            dashboard.showNotification('User deleted successfully', 'success');
            dashboard.loadAdminData();
        } else {
            dashboard.showNotification(data.error || 'Failed to delete user', 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting user:', error);
        dashboard.showNotification('Error deleting user', 'error');
    });
}

// Function to redeem coupon
async function redeemCoupon() {
    const couponCode = document.getElementById('couponCode').value.trim().toUpperCase();
    
    if (!couponCode) {
        dashboard.showNotification('Please enter a coupon code', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/redeem-coupon', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ couponCode })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            dashboard.showNotification(`Successfully redeemed! +${data.coins} coins`, 'success');
            document.getElementById('couponCode').value = '';
            
            // Update user coins display
            if (dashboard.currentUser) {
                dashboard.currentUser.coins = data.newBalance;
                dashboard.updateCoinsDisplay();
                
                // Update profile page if visible
                const profileCoins = document.getElementById('profile-coins');
                if (profileCoins) {
                    profileCoins.textContent = dashboard.formatCoins(data.newBalance);
                }
            }
        } else {
            dashboard.showNotification(data.error || 'Failed to redeem coupon', 'error');
        }
    } catch (error) {
        console.error('Error redeeming coupon:', error);
        dashboard.showNotification('Error redeeming coupon', 'error');
    }
}

// Admin function to create coupon
async function createCoupon() {
    const couponCode = document.getElementById('couponCodeInput').value.trim().toUpperCase();
    const amount = parseInt(document.getElementById('couponAmount').value);
    const limit = parseInt(document.getElementById('couponLimit').value);
    
    if (!couponCode || !amount || !limit || amount <= 0 || limit <= 0) {
        dashboard.showNotification('Please fill all fields with valid values', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/admin/create-coupon', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ couponCode, amount, limit })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            dashboard.showNotification(`Coupon "${couponCode}" created successfully!`, 'success');
            document.getElementById('couponCodeInput').value = '';
            document.getElementById('couponAmount').value = '';
            document.getElementById('couponLimit').value = '';
        } else {
            dashboard.showNotification(data.error || 'Failed to create coupon', 'error');
        }
    } catch (error) {
        console.error('Error creating coupon:', error);
        dashboard.showNotification('Error creating coupon', 'error');
    }
}

// Admin function to update Discord link
async function updateDiscordLink() {
    const discordLink = document.getElementById('discordLink').value.trim();
    
    if (!discordLink || !discordLink.startsWith('https://discord.gg/')) {
        dashboard.showNotification('Please enter a valid Discord invite link', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/admin/update-discord', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ discordLink })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('discordLink', discordLink);
            dashboard.showNotification('Discord link updated successfully!', 'success');
        } else {
            dashboard.showNotification(data.error || 'Failed to update Discord link', 'error');
        }
    } catch (error) {
        console.error('Error updating Discord link:', error);
        dashboard.showNotification('Error updating Discord link', 'error');
    }
}

// Admin function to remove coins
async function removeCoins() {
    const username = document.getElementById('removeUsername').value.trim();
    const coins = parseInt(document.getElementById('removeCoins').value);
    
    if (!username || !coins || coins <= 0) {
        dashboard.showNotification('Please enter valid username and coins amount', 'error');
        return;
    }
    
    if (!confirm(`Are you sure you want to remove ${coins} coins from ${username}?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/admin/remove-coins', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ username, coins })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            dashboard.showNotification(`Successfully removed ${coins} coins from ${username}`, 'success');
            document.getElementById('removeUsername').value = '';
            document.getElementById('removeCoins').value = '';
            dashboard.loadLeaderboard(); // Refresh leaderboard
        } else {
            dashboard.showNotification(data.error || 'Failed to remove coins', 'error');
        }
    } catch (error) {
        console.error('Error removing coins:', error);
        dashboard.showNotification('Error removing coins', 'error');
    }
}

// Node Management Functions
async function loadNodeManagement() {
    try {
        const response = await fetch('/api/admin/nodes', {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            updateNodeDisplay(data);
        } else {
            dashboard.showNotification('Failed to load node information', 'error');
        }
    } catch (error) {
        console.error('Error loading nodes:', error);
        dashboard.showNotification('Error loading node information', 'error');
    }
}

function updateNodeDisplay(data) {
    const currentNodeEl = document.getElementById('currentNode');
    const nodeServerCountEl = document.getElementById('nodeServerCount');
    const nodeSelectEl = document.getElementById('nodeSelect');
    
    if (currentNodeEl) {
        currentNodeEl.textContent = data.currentNode?.name || 'Unknown';
    }
    
    if (nodeServerCountEl) {
        nodeServerCountEl.textContent = `${data.currentNode?.serverCount || 0} / ${data.serverLimit || 600}`;
    }
    
    if (nodeSelectEl && data.nodes) {
        nodeSelectEl.innerHTML = '<option value="">Select node...</option>';
        data.nodes.forEach(node => {
            const option = document.createElement('option');
            option.value = node.id;
            option.textContent = `${node.name} (${node.serverCount} servers)`;
            if (node.id === data.currentNode?.id) {
                option.selected = true;
            }
            nodeSelectEl.appendChild(option);
        });
    }
}

async function switchToNode() {
    const nodeId = document.getElementById('nodeSelect').value;
    
    if (!nodeId) {
        dashboard.showNotification('Please select a node', 'error');
        return;
    }
    
    if (!confirm('Are you sure you want to switch the active node? This will affect new server creations.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/admin/switch-node', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ nodeId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            dashboard.showNotification('Node switched successfully!', 'success');
            loadNodeManagement(); // Refresh node info
        } else {
            dashboard.showNotification(data.error || 'Failed to switch node', 'error');
        }
    } catch (error) {
        console.error('Error switching node:', error);
        dashboard.showNotification('Error switching node', 'error');
    }
}

async function refreshNodes() {
    dashboard.showNotification('Refreshing node information...', 'info');
    await loadNodeManagement();
}

async function checkNodeStatus() {
    try {
        const response = await fetch('/api/admin/node-status', {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            let statusMessage = `Node Status:\n`;
            data.nodes.forEach(node => {
                statusMessage += `${node.name}: ${node.serverCount} servers (${node.status})\n`;
            });
            alert(statusMessage);
        } else {
            dashboard.showNotification('Failed to check node status', 'error');
        }
    } catch (error) {
        console.error('Error checking node status:', error);
        dashboard.showNotification('Error checking node status', 'error');
    }
}

async function updateServerLimit() {
    const serverLimit = parseInt(document.getElementById('serverLimit').value);
    
    if (!serverLimit || serverLimit < 1 || serverLimit > 1000) {
        dashboard.showNotification('Please enter a valid server limit (1-1000)', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/admin/update-server-limit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ serverLimit })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            dashboard.showNotification('Server limit updated successfully!', 'success');
        } else {
            dashboard.showNotification(data.error || 'Failed to update server limit', 'error');
        }
    } catch (error) {
        console.error('Error updating server limit:', error);
        dashboard.showNotification('Error updating server limit', 'error');
    }
}

// Store functions
async function buyResource(type, amount, price) {
    if (!dashboard.currentUser || dashboard.currentUser.coins < price) {
        dashboard.showNotification('Insufficient coins', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/buy-resource', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ type, amount, price })
        });
        
        const data = await response.json();
        if (response.ok) {
            const typeDisplay = type === 'ram' ? `${amount}MB RAM` : type === 'cpu' ? `${amount}% CPU` : `${amount}MB Disk`;
            dashboard.showNotification(`Successfully bought ${typeDisplay}!`, 'success');
            dashboard.currentUser.coins = data.newBalance;
            dashboard.updateCoinsDisplay();
            
            // Force refresh resource usage immediately
            console.log('🔄 Refreshing resources after purchase...');
            await dashboard.loadResourceUsage();
            
            // Also refresh dashboard data
            setTimeout(() => {
                dashboard.loadDashboardData();
            }, 500);
        } else {
            dashboard.showNotification(data.error, 'error');
        }
    } catch (error) {
        console.error('Error buying resource:', error);
        dashboard.showNotification('Error buying resource', 'error');
    }
}

async function buySlot(slots, price) {
    if (!dashboard.currentUser || dashboard.currentUser.coins < price) {
        dashboard.showNotification('Insufficient coins', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/buy-slot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ slots, price })
        });
        
        const data = await response.json();
        if (response.ok) {
            const slotText = slots === 1 ? 'server slot' : `${slots} server slots`;
            dashboard.showNotification(`Successfully bought ${slotText}!`, 'success');
            dashboard.currentUser.coins = data.newBalance;
            dashboard.updateCoinsDisplay();
            
            // Force refresh resource usage immediately
            console.log('🔄 Refreshing resources after slot purchase...');
            await dashboard.loadResourceUsage();
            
            // Also refresh dashboard data
            setTimeout(() => {
                dashboard.loadDashboardData();
            }, 500);
        } else {
            dashboard.showNotification(data.error, 'error');
        }
    } catch (error) {
        console.error('Error buying slot:', error);
        dashboard.showNotification('Error buying slot', 'error');
    }
}

async function updatePrice(type, inputId) {
    const price = parseInt(document.getElementById(inputId).value);
    if (!price || price <= 0) {
        dashboard.showNotification('Invalid price', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/admin/update-price', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ type, price })
        });
        
        const data = await response.json();
        if (response.ok) {
            dashboard.showNotification(`${type} price updated!`, 'success');
        } else {
            dashboard.showNotification(data.error, 'error');
        }
    } catch (error) {
        dashboard.showNotification('Error updating price', 'error');
    }
}

// Mobile menu functions
function toggleMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.querySelector('.mobile-overlay');
    
    sidebar.classList.toggle('mobile-visible');
    overlay.classList.toggle('active');
}

function closeMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.querySelector('.mobile-overlay');
    
    sidebar.classList.remove('mobile-visible');
    overlay.classList.remove('active');
}

// Tab switching function
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // Activate button
    event.target.classList.add('active');
}

// Admin tab switching function
function showAdminTab(tabName) {
    // Hide all admin tabs
    document.querySelectorAll('.admin-tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from all admin tab buttons
    document.querySelectorAll('.admin-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected admin tab
    document.getElementById(tabName + '-admin-tab').classList.add('active');
    
    // Activate button
    event.target.classList.add('active');
    
    // Load specific data for the tab
    if (tabName === 'system') {
        loadNodeManagement();
    }
}

// AFK System Class
class AFKSystem {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.isActive = false;
        this.timer = null;
        this.timeLeft = 60;
        this.sessionEarnings = 0;
        this.streak = 0;
        this.lastActivity = Date.now();
        this.activityCheckInterval = null;
        
        // Load saved data
        this.loadAFKData();
        
        // Setup activity detection
        this.setupActivityDetection();
    }
    
    loadAFKData() {
        const saved = localStorage.getItem('afkData');
        if (saved) {
            const data = JSON.parse(saved);
            this.sessionEarnings = data.sessionEarnings || 0;
            this.streak = data.streak || 0;
        }
        this.updateDisplay();
    }
    
    saveAFKData() {
        localStorage.setItem('afkData', JSON.stringify({
            sessionEarnings: this.sessionEarnings,
            streak: this.streak
        }));
    }
    
    setupActivityDetection() {
        // Track user activity
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
            document.addEventListener(event, () => {
                this.lastActivity = Date.now();
            }, true);
        });
        
        // Check for inactivity every 5 seconds
        this.activityCheckInterval = setInterval(() => {
            if (this.isActive && Date.now() - this.lastActivity > 300000) { // 5 minutes
                console.log('User inactive for 5 minutes, stopping AFK');
                this.stopAFK();
            }
        }, 5000);
    }
    
    startAFK() {
        if (this.isActive) return;
        
        console.log('Starting AFK earning...');
        this.isActive = true;
        this.timeLeft = 60;
        this.lastActivity = Date.now();
        
        // Update UI
        document.getElementById('startAfkBtn').style.display = 'none';
        document.getElementById('stopAfkBtn').style.display = 'block';
        document.getElementById('afkStatus').textContent = 'Active';
        document.getElementById('afkStatus').className = 'status-indicator active';
        
        // Start timer
        this.timer = setInterval(() => {
            this.timeLeft--;
            this.updateTimer();
            
            if (this.timeLeft <= 0) {
                this.earnCoins();
                this.timeLeft = 60;
            }
        }, 1000);
        
        this.updateDisplay();
    }
    
    stopAFK() {
        if (!this.isActive) return;
        
        console.log('Stopping AFK earning...');
        this.isActive = false;
        
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
        
        // Update UI
        document.getElementById('startAfkBtn').style.display = 'block';
        document.getElementById('stopAfkBtn').style.display = 'none';
        document.getElementById('afkStatus').textContent = 'Inactive';
        document.getElementById('afkStatus').className = 'status-indicator inactive';
        
        this.timeLeft = 60;
        this.updateDisplay();
    }
    
    async earnCoins() {
        try {
            const response = await fetch('/api/afk-earn', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.sessionEarnings += 1.2;
                this.streak++;
                
                // Update user coins
                if (this.dashboard.currentUser) {
                    this.dashboard.currentUser.coins = data.newBalance;
                    this.dashboard.updateCoinsDisplay();
                }
                
                console.log('Earned 1.2 coins from AFK');
                this.saveAFKData();
                this.updateDisplay();
                
                // Show earning notification
                this.showEarningNotification();
            } else {
                console.error('Failed to earn AFK coins:', data.error);
                this.stopAFK();
            }
        } catch (error) {
            console.error('AFK earning error:', error);
            this.stopAFK();
        }
    }
    
    showEarningNotification() {
        const notification = document.createElement('div');
        notification.className = 'afk-earning-notification';
        notification.innerHTML = '+1.2 coins';
        notification.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #fbbf24, #f59e0b);
            color: #000000;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: 700;
            font-size: 16px;
            z-index: 10000;
            animation: afkEarnPop 2s ease-out forwards;
            pointer-events: none;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 2000);
    }
    
    updateTimer() {
        const timerEl = document.getElementById('afkTimer');
        const progressEl = document.getElementById('afkProgress');
        const progressTextEl = document.getElementById('progressText');
        
        if (timerEl) timerEl.textContent = this.timeLeft;
        
        if (progressEl) {
            const progress = ((60 - this.timeLeft) / 60) * 100;
            progressEl.style.width = `${progress}%`;
        }
        
        if (progressTextEl) {
            if (this.isActive) {
                progressTextEl.textContent = `Next reward in ${this.timeLeft} seconds`;
            } else {
                progressTextEl.textContent = 'Click Start to begin earning';
            }
        }
    }
    
    updateDisplay() {
        const sessionEl = document.getElementById('sessionEarnings');
        const streakEl = document.getElementById('afkStreak');
        const coinsEarnedEl = document.getElementById('coinsEarned');
        
        if (sessionEl) sessionEl.textContent = this.formatCoins(this.sessionEarnings);
        if (streakEl) streakEl.textContent = this.streak;
        if (coinsEarnedEl) coinsEarnedEl.textContent = `${this.formatCoins(this.sessionEarnings)} coins earned`;
    }
    
    formatCoins(coins) {
        const num = parseFloat(coins);
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'k';
        } else if (num % 1 === 0) {
            return num.toString();
        } else {
            return num.toFixed(1);
        }
        
        this.updateTimer();
    }
}

// Pong Game Class
class PongGame {
    constructor() {
        this.canvas = document.getElementById('pongCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.isRunning = false;
        this.isPaused = false;
        this.score = 0;
        this.highScore = parseInt(localStorage.getItem('pongHighScore')) || 0;
        this.mobileControls = { up: false, down: false };
        
        // Game objects
        this.ball = { x: 300, y: 150, dx: 4, dy: 3, radius: 8 };
        this.playerPaddle = { x: 20, y: 120, width: 10, height: 60, dy: 0 };
        this.aiPaddle = { x: 570, y: 120, width: 10, height: 60 };
        
        this.setupControls();
        this.updateScoreDisplay();
        this.draw();
    }
    
    setupControls() {
        document.addEventListener('keydown', (e) => {
            if (!this.isRunning || this.isPaused) return;
            
            switch(e.key) {
                case 'ArrowUp':
                case 'w':
                case 'W':
                    this.playerPaddle.dy = -6;
                    break;
                case 'ArrowDown':
                case 's':
                case 'S':
                    this.playerPaddle.dy = 6;
                    break;
            }
        });
        
        document.addEventListener('keyup', (e) => {
            if (!this.isRunning || this.isPaused) return;
            
            switch(e.key) {
                case 'ArrowUp':
                case 'ArrowDown':
                case 'w':
                case 'W':
                case 's':
                case 'S':
                    this.playerPaddle.dy = 0;
                    break;
            }
        });
    }
    
    startGame() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.isPaused = false;
        this.score = 0;
        this.resetBall();
        
        document.getElementById('startGameBtn').style.display = 'none';
        document.getElementById('pauseGameBtn').style.display = 'block';
        document.getElementById('resetGameBtn').style.display = 'block';
        
        this.gameLoop();
    }
    
    pauseGame() {
        this.isPaused = !this.isPaused;
        const pauseBtn = document.getElementById('pauseGameBtn');
        
        if (this.isPaused) {
            pauseBtn.innerHTML = '<i class="fas fa-play"></i> Resume';
        } else {
            pauseBtn.innerHTML = '<i class="fas fa-pause"></i> Pause';
            this.gameLoop();
        }
    }
    
    stopGame() {
        this.isRunning = false;
        this.isPaused = false;
        
        document.getElementById('startGameBtn').style.display = 'block';
        document.getElementById('pauseGameBtn').style.display = 'none';
        document.getElementById('resetGameBtn').style.display = 'none';
        document.getElementById('pauseGameBtn').innerHTML = '<i class="fas fa-pause"></i> Pause';
        
        if (this.score > this.highScore) {
            this.highScore = this.score;
            localStorage.setItem('pongHighScore', this.highScore);
        }
        
        this.updateScoreDisplay();
    }
    
    gameLoop() {
        if (!this.isRunning || this.isPaused) return;
        
        this.update();
        this.draw();
        
        requestAnimationFrame(() => this.gameLoop());
    }
    
    update() {
        // Handle mobile controls
        if (this.mobileControls.up) {
            this.playerPaddle.dy = -6;
        } else if (this.mobileControls.down) {
            this.playerPaddle.dy = 6;
        }
        
        // Move player paddle
        this.playerPaddle.y += this.playerPaddle.dy;
        this.playerPaddle.y = Math.max(0, Math.min(this.canvas.height - this.playerPaddle.height, this.playerPaddle.y));
        
        // Move AI paddle
        const aiCenter = this.aiPaddle.y + this.aiPaddle.height / 2;
        const ballCenter = this.ball.y;
        
        if (aiCenter < ballCenter - 35) {
            this.aiPaddle.y += 4;
        } else if (aiCenter > ballCenter + 35) {
            this.aiPaddle.y -= 4;
        }
        
        this.aiPaddle.y = Math.max(0, Math.min(this.canvas.height - this.aiPaddle.height, this.aiPaddle.y));
        
        // Move ball
        this.ball.x += this.ball.dx;
        this.ball.y += this.ball.dy;
        
        // Ball collision with top/bottom
        if (this.ball.y <= this.ball.radius || this.ball.y >= this.canvas.height - this.ball.radius) {
            this.ball.dy = -this.ball.dy;
        }
        
        // Ball collision with paddles
        if (this.ball.x <= this.playerPaddle.x + this.playerPaddle.width + this.ball.radius &&
            this.ball.y >= this.playerPaddle.y &&
            this.ball.y <= this.playerPaddle.y + this.playerPaddle.height) {
            this.ball.dx = -this.ball.dx;
            this.score++;
            this.updateScoreDisplay();
        }
        
        if (this.ball.x >= this.aiPaddle.x - this.ball.radius &&
            this.ball.y >= this.aiPaddle.y &&
            this.ball.y <= this.aiPaddle.y + this.aiPaddle.height) {
            this.ball.dx = -this.ball.dx;
        }
        
        // Ball out of bounds
        if (this.ball.x < 0 || this.ball.x > this.canvas.width) {
            this.stopGame();
        }
    }
    
    draw() {
        // Clear canvas
        this.ctx.fillStyle = '#000000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw center line
        this.ctx.setLineDash([5, 15]);
        this.ctx.beginPath();
        this.ctx.moveTo(this.canvas.width / 2, 0);
        this.ctx.lineTo(this.canvas.width / 2, this.canvas.height);
        this.ctx.strokeStyle = '#333333';
        this.ctx.stroke();
        this.ctx.setLineDash([]);
        
        // Draw paddles
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(this.playerPaddle.x, this.playerPaddle.y, this.playerPaddle.width, this.playerPaddle.height);
        this.ctx.fillRect(this.aiPaddle.x, this.aiPaddle.y, this.aiPaddle.width, this.aiPaddle.height);
        
        // Draw ball
        this.ctx.beginPath();
        this.ctx.arc(this.ball.x, this.ball.y, this.ball.radius, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Draw score
        this.ctx.font = '20px Inter';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(this.score, this.canvas.width / 4, 30);
        this.ctx.fillText('AI', 3 * this.canvas.width / 4, 30);
    }
    
    resetBall() {
        this.ball.x = this.canvas.width / 2;
        this.ball.y = this.canvas.height / 2;
        this.ball.dx = Math.random() > 0.5 ? 4 : -4;
        this.ball.dy = (Math.random() - 0.5) * 6;
    }
    
    updateScoreDisplay() {
        document.getElementById('gameScore').textContent = this.score;
        document.getElementById('highScore').textContent = this.highScore;
    }
    
    setMobileControl(direction, active) {
        this.mobileControls[direction] = active;
    }
    
    resetGame() {
        this.stopGame();
        this.score = 0;
        this.resetBall();
        this.updateScoreDisplay();
    }
}

// Promotion functions
async function submitPromotion(event) {
    event.preventDefault();
    
    const serverName = document.getElementById('promoServerName').value.trim();
    const serverIP = document.getElementById('promoServerIP').value.trim();
    const description = document.getElementById('promoServerDescription').value.trim();
    
    if (!serverName || !serverIP || !description) {
        dashboard.showNotification('Please fill in all fields', 'error');
        return;
    }
    
    if (dashboard.currentUser.coins < 500) {
        dashboard.showNotification('Insufficient coins. You need 500 coins to promote.', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/create-promotion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                serverName,
                serverIP,
                description
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            dashboard.showNotification('Promotion published successfully!', 'success');
            document.getElementById('promotionForm').reset();
            dashboard.currentUser.coins = data.newBalance;
            dashboard.updateCoinsDisplay();
            dashboard.loadPromotions();
        } else {
            dashboard.showNotification(data.error || 'Failed to create promotion', 'error');
        }
    } catch (error) {
        console.error('Error creating promotion:', error);
        dashboard.showNotification('Error creating promotion', 'error');
    }
}

async function boostPromotion(promotionId) {
    if (dashboard.currentUser.coins < 100) {
        dashboard.showNotification('Insufficient coins. You need 100 coins to boost.', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/boost-promotion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ promotionId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            dashboard.showNotification('Promotion boosted successfully!', 'success');
            dashboard.currentUser.coins = data.newBalance;
            dashboard.updateCoinsDisplay();
            dashboard.loadPromotions();
        } else {
            dashboard.showNotification(data.error || 'Failed to boost promotion', 'error');
        }
    } catch (error) {
        console.error('Error boosting promotion:', error);
        dashboard.showNotification('Error boosting promotion', 'error');
    }
}

function copyServerIP(ip) {
    navigator.clipboard.writeText(ip).then(() => {
        dashboard.showNotification('Server IP copied to clipboard!', 'success');
    }).catch(() => {
        dashboard.showNotification('Failed to copy IP', 'error');
    });
}

// Setup promotion form
document.addEventListener('DOMContentLoaded', function() {
    const promotionForm = document.getElementById('promotionForm');
    if (promotionForm) {
        promotionForm.addEventListener('submit', submitPromotion);
    }
});

// Add CSS animations for AFK and game
const afkStyle = document.createElement('style');
afkStyle.textContent = `
    @keyframes afkEarnPop {
        0% {
            transform: translate(-50%, -50%) scale(0);
            opacity: 0;
        }
        50% {
            transform: translate(-50%, -50%) scale(1.2);
            opacity: 1;
        }
        100% {
            transform: translate(-50%, -50%) scale(1) translateY(-50px);
            opacity: 0;
        }
    }
    
    .afk-earning-notification {
        animation: afkEarnPop 2s ease-out forwards;
    }
    
    .no-promotions {
        text-align: center;
        padding: 40px;
        color: #888888;
        background: #111111;
        border: 1px solid #1f1f1f;
        border-radius: 12px;
        grid-column: 1 / -1;
    }
`;
document.head.appendChild(afkStyle);

// Server editing variables
let currentEditingServer = null;
let currentResources = { ram: 1024, cpu: 50, disk: 2048 };

// Edit server function
function editServer(serverIdentifier) {
    const server = dashboard.servers.find(s => s.attributes.identifier === serverIdentifier);
    if (!server) {
        dashboard.showNotification('Server not found', 'error');
        return;
    }
    
    currentEditingServer = server;
    currentResources = {
        ram: server.attributes.limits.memory,
        cpu: server.attributes.limits.cpu,
        disk: server.attributes.limits.disk
    };
    
    // Update modal content
    document.getElementById('editServerName').textContent = server.attributes.name;
    document.getElementById('editServerID').textContent = server.attributes.identifier;
    
    // Update resource displays
    updateResourceDisplay('ram', currentResources.ram);
    updateResourceDisplay('cpu', currentResources.cpu);
    updateResourceDisplay('disk', currentResources.disk);
    
    // Show modal
    document.getElementById('serverEditModal').classList.add('active');
}

// Close server edit modal
function closeServerEditModal() {
    document.getElementById('serverEditModal').classList.remove('active');
    currentEditingServer = null;
}

// Adjust resource function
function adjustResource(type, change) {
    const limits = {
        ram: { min: 512, max: 2048, step: 256 },
        cpu: { min: 25, max: 100, step: 25 },
        disk: { min: 1024, max: 5120, step: 512 }
    };
    
    const limit = limits[type];
    const newValue = Math.max(limit.min, Math.min(limit.max, currentResources[type] + change));
    
    if (newValue !== currentResources[type]) {
        currentResources[type] = newValue;
        updateResourceDisplay(type, newValue);
    }
}

// Update resource display
function updateResourceDisplay(type, value) {
    const limits = {
        ram: { min: 512, max: 2048 },
        cpu: { min: 25, max: 100 },
        disk: { min: 1024, max: 5120 }
    };
    
    const limit = limits[type];
    const percentage = ((value - limit.min) / (limit.max - limit.min)) * 100;
    
    // Update value display
    const valueEl = document.getElementById(`${type}Value`);
    if (type === 'ram' || type === 'disk') {
        if (value >= 1024) {
            valueEl.textContent = `${(value / 1024).toFixed(value % 1024 === 0 ? 0 : 1)}GB`;
        } else {
            valueEl.textContent = `${value}MB`;
        }
    } else {
        valueEl.textContent = `${value}%`;
    }
    
    // Update progress bar
    const fillEl = document.getElementById(`${type}Fill`);
    fillEl.style.width = `${percentage}%`;
}

// Save server changes
async function saveServerChanges() {
    if (!currentEditingServer) {
        dashboard.showNotification('No server selected', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/update-server-resources', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                serverIdentifier: currentEditingServer.attributes.identifier,
                resources: currentResources
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            dashboard.showNotification('Server resources updated successfully!', 'success');
            closeServerEditModal();
            
            // Refresh servers
            await dashboard.loadServers();
        } else {
            dashboard.showNotification(data.error || 'Failed to update server resources', 'error');
        }
    } catch (error) {
        console.error('Error updating server resources:', error);
        dashboard.showNotification('Error updating server resources', 'error');
    }
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    const modal = document.getElementById('serverEditModal');
    if (e.target === modal) {
        closeServerEditModal();
    }
});

// Admin function to create user
async function createUser() {
    const username = document.getElementById('createUsername').value.trim();
    const password = document.getElementById('createPassword').value.trim();
    
    if (!username || !password) {
        dashboard.showNotification('Please enter both username and password', 'error');
        return;
    }
    
    if (username.length < 3) {
        dashboard.showNotification('Username must be at least 3 characters', 'error');
        return;
    }
    
    if (password.length < 3) {
        dashboard.showNotification('Password must be at least 3 characters', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/admin/create-user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            dashboard.showNotification(`User "${username}" created successfully!`, 'success');
            document.getElementById('createUsername').value = '';
            document.getElementById('createPassword').value = '';
            dashboard.loadAdminData(); // Refresh user list
        } else {
            dashboard.showNotification(data.error || 'Failed to create user', 'error');
        }
    } catch (error) {
        console.error('Error creating user:', error);
        dashboard.showNotification('Error creating user', 'error');
    }
}

// Advanced Linkvertise completion detection system
class LinkvertiseDetector {
    constructor() {
        this.isTracking = false;
        this.startTime = null;
        this.completionWindow = null;
        this.checkInterval = null;
        this.sessionId = null;
        this.minCompletionTime = 45000; // 45 seconds minimum
        this.maxCompletionTime = 300000; // 5 minutes maximum
        this.detectionMethods = {
            windowFocus: false,
            urlPattern: false,
            timeValidation: false,
            behaviorAnalysis: false
        };
    }
    
    generateSessionId() {
        return 'lv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    startTracking(linkvertiseUrl) {
        this.sessionId = this.generateSessionId();
        this.startTime = Date.now();
        this.isTracking = true;
        
        console.log(`🔍 Starting Linkvertise tracking session: ${this.sessionId}`);
        
        // Store session data
        const sessionData = {
            sessionId: this.sessionId,
            startTime: this.startTime,
            url: linkvertiseUrl,
            userAgent: navigator.userAgent,
            screenResolution: `${screen.width}x${screen.height}`,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        };
        
        localStorage.setItem('linkvertise_session', JSON.stringify(sessionData));
        
        // Open Linkvertise URL
        this.completionWindow = window.open(linkvertiseUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
        
        if (!this.completionWindow) {
            dashboard.showNotification('Please allow popups for this site to earn coins!', 'error');
            this.stopTracking();
            return false;
        }
        
        // Start monitoring
        this.startMonitoring();
        
        dashboard.showNotification('Linkvertise task opened! Complete it within 5 minutes to earn 8 coins.', 'info');
        return true;
    }
    
    startMonitoring() {
        // Monitor window focus and URL changes
        this.checkInterval = setInterval(() => {
            this.performChecks();
        }, 2000);
        
        // Listen for window focus events
        window.addEventListener('focus', () => {
            if (this.isTracking) {
                this.onWindowFocus();
            }
        });
        
        // Monitor for completion signals
        this.setupCompletionDetection();
    }
    
    performChecks() {
        if (!this.isTracking || !this.completionWindow) {
            return;
        }
        
        // Check if window is closed
        if (this.completionWindow.closed) {
            this.onWindowClosed();
            return;
        }
        
        // Check completion time limits
        const elapsed = Date.now() - this.startTime;
        if (elapsed > this.maxCompletionTime) {
            dashboard.showNotification('Linkvertise session expired. Please try again.', 'warning');
            this.stopTracking();
            return;
        }
        
        // Try to detect completion through URL analysis
        try {
            if (this.completionWindow.location && this.completionWindow.location.href) {
                this.analyzeURL(this.completionWindow.location.href);
            }
        } catch (e) {
            // Cross-origin restrictions - normal behavior
        }
    }
    
    analyzeURL(url) {
        // Advanced URL pattern analysis for completion detection
        const completionPatterns = [
            /completed?/i,
            /success/i,
            /finish/i,
            /done/i,
            /redirect/i,
            /continue/i,
            /proceed/i
        ];
        
        const isCompletionURL = completionPatterns.some(pattern => pattern.test(url));
        
        if (isCompletionURL && !this.detectionMethods.urlPattern) {
            this.detectionMethods.urlPattern = true;
            console.log('✅ URL pattern completion detected');
            this.checkForCompletion();
        }
    }
    
    onWindowFocus() {
        if (!this.detectionMethods.windowFocus) {
            this.detectionMethods.windowFocus = true;
            console.log('✅ Window focus completion signal detected');
            
            // Delay check to ensure user actually completed the task
            setTimeout(() => {
                this.checkForCompletion();
            }, 3000);
        }
    }
    
    onWindowClosed() {
        const elapsed = Date.now() - this.startTime;
        
        if (elapsed >= this.minCompletionTime) {
            console.log('✅ Window closed after minimum time - potential completion');
            this.detectionMethods.timeValidation = true;
            this.checkForCompletion();
        } else {
            dashboard.showNotification('Task closed too quickly. Please complete the full process.', 'warning');
            this.stopTracking();
        }
    }
    
    setupCompletionDetection() {
        // Advanced behavior analysis
        let interactionCount = 0;
        let lastInteraction = Date.now();
        
        const trackInteraction = () => {
            interactionCount++;
            lastInteraction = Date.now();
            
            if (interactionCount >= 3) {
                this.detectionMethods.behaviorAnalysis = true;
                console.log('✅ User behavior analysis passed');
            }
        };
        
        // Track user interactions
        ['click', 'keydown', 'scroll', 'mousemove'].forEach(event => {
            document.addEventListener(event, trackInteraction, { once: true });
        });
        
        // Periodic behavior check
        setTimeout(() => {
            const timeSinceLastInteraction = Date.now() - lastInteraction;
            if (timeSinceLastInteraction < 30000 && interactionCount >= 2) {
                this.detectionMethods.behaviorAnalysis = true;
            }
        }, 30000);
    }
    
    checkForCompletion() {
        const elapsed = Date.now() - this.startTime;
        const detectionScore = this.calculateDetectionScore();
        
        console.log(`🔍 Completion check - Score: ${detectionScore}, Time: ${elapsed}ms`);
        
        // Advanced completion validation
        if (this.validateCompletion(elapsed, detectionScore)) {
            this.processCompletion();
        }
    }
    
    calculateDetectionScore() {
        let score = 0;
        
        if (this.detectionMethods.windowFocus) score += 25;
        if (this.detectionMethods.urlPattern) score += 35;
        if (this.detectionMethods.timeValidation) score += 25;
        if (this.detectionMethods.behaviorAnalysis) score += 15;
        
        return score;
    }
    
    validateCompletion(elapsed, score) {
        // Multi-factor validation
        const timeValid = elapsed >= this.minCompletionTime && elapsed <= this.maxCompletionTime;
        const scoreValid = score >= 50; // Minimum 50% confidence
        const sessionValid = this.sessionId && localStorage.getItem('linkvertise_session');
        
        // Anti-fraud checks
        const recentCompletions = this.getRecentCompletions();
        const tooFrequent = recentCompletions.length >= 3; // Max 3 completions per hour
        
        if (tooFrequent) {
            dashboard.showNotification('Too many completions detected. Please wait before trying again.', 'warning');
            return false;
        }
        
        return timeValid && scoreValid && sessionValid;
    }
    
    getRecentCompletions() {
        const completions = JSON.parse(localStorage.getItem('linkvertise_completions') || '[]');
        const oneHourAgo = Date.now() - (60 * 60 * 1000);
        
        return completions.filter(completion => completion.timestamp > oneHourAgo);
    }
    
    async processCompletion() {
        console.log('🎉 Linkvertise completion validated!');
        
        try {
            // Record completion
            this.recordCompletion();
            
            // Award coins through API
            const response = await fetch('/api/linkvertise-complete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    sessionId: this.sessionId,
                    completionTime: Date.now() - this.startTime,
                    detectionMethods: this.detectionMethods,
                    userAgent: navigator.userAgent
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Update local stats
                this.updateLocalStats();
                
                // Update user coins in dashboard
                if (dashboard.currentUser) {
                    dashboard.currentUser.coins = data.newBalance;
                    dashboard.updateCoinsDisplay();
                }
                
                dashboard.showNotification(`🎉 Linkvertise completed! +8 coins earned!`, 'success');
                
                // Update earn page stats if visible
                if (dashboard.updateEarnStats) {
                    dashboard.updateEarnStats();
                }
            } else {
                dashboard.showNotification(data.error || 'Failed to process completion', 'error');
            }
        } catch (error) {
            console.error('Error processing completion:', error);
            dashboard.showNotification('Error processing completion. Please try again.', 'error');
        } finally {
            this.stopTracking();
        }
    }
    
    recordCompletion() {
        const completions = JSON.parse(localStorage.getItem('linkvertise_completions') || '[]');
        
        completions.push({
            sessionId: this.sessionId,
            timestamp: Date.now(),
            completionTime: Date.now() - this.startTime,
            detectionScore: this.calculateDetectionScore()
        });
        
        // Keep only last 10 completions
        if (completions.length > 10) {
            completions.splice(0, completions.length - 10);
        }
        
        localStorage.setItem('linkvertise_completions', JSON.stringify(completions));
    }
    
    updateLocalStats() {
        const earnStats = JSON.parse(localStorage.getItem('earnStats') || '{}');
        earnStats.linkvertiseCompleted = (earnStats.linkvertiseCompleted || 0) + 1;
        earnStats.totalEarned = (earnStats.totalEarned || 0) + 8;
        earnStats.todayEarned = (earnStats.todayEarned || 0) + 8;
        
        localStorage.setItem('earnStats', JSON.stringify(earnStats));
    }
    
    stopTracking() {
        this.isTracking = false;
        
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
        }
        
        if (this.completionWindow && !this.completionWindow.closed) {
            this.completionWindow.close();
        }
        
        // Clean up session data
        localStorage.removeItem('linkvertise_session');
        
        console.log(`🔍 Stopped tracking session: ${this.sessionId}`);
        this.sessionId = null;
    }
}

// Global Linkvertise detector instance
window.linkvertiseDetector = new LinkvertiseDetector();

// Function to open Linkvertise earning with advanced detection
function openLinkvertise() {
    const linkvertiseUrl = window.currentLinkvertiseUrl || localStorage.getItem('linkvertiseUrl') || 'https://dash.blazenode.site';
    
    // Check if already tracking
    if (window.linkvertiseDetector.isTracking) {
        dashboard.showNotification('A Linkvertise task is already in progress!', 'warning');
        return;
    }
    
    // Start advanced tracking
    const success = window.linkvertiseDetector.startTracking(linkvertiseUrl);
    
    if (!success) {
        dashboard.showNotification('Failed to start Linkvertise task. Please check popup settings.', 'error');
    }
}

// Admin function to update Linkvertise URL
async function updateLinkvertiseUrl() {
    const linkvertiseUrl = document.getElementById('linkvertiseUrl').value.trim();
    
    if (!linkvertiseUrl || !linkvertiseUrl.startsWith('http')) {
        dashboard.showNotification('Please enter a valid URL starting with http:// or https://', 'error');
        return;
    }
    
    try {
        // Save to localStorage (in a real app, this would be saved to database)
        localStorage.setItem('linkvertiseUrl', linkvertiseUrl);
        window.currentLinkvertiseUrl = linkvertiseUrl;
        
        // Update display
        const currentLinkvertiseUrl = document.getElementById('currentLinkvertiseUrl');
        if (currentLinkvertiseUrl) {
            currentLinkvertiseUrl.textContent = linkvertiseUrl;
        }
        
        dashboard.showNotification('Linkvertise URL updated successfully!', 'success');
        
        console.log(`Admin ${dashboard.currentUser?.username} updated Linkvertise URL to: ${linkvertiseUrl}`);
        
    } catch (error) {
        console.error('Error updating Linkvertise URL:', error);
        dashboard.showNotification('Error updating Linkvertise URL', 'error');
    }
}

// Delete server function
async function deleteServer(serverIdentifier, serverName) {
    if (!confirm(`Are you sure you want to delete server "${serverName}"?\n\nThis action cannot be undone and will permanently delete the server from both the dashboard and Pterodactyl panel.`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/delete-server', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ serverIdentifier })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            dashboard.showNotification(`Server "${serverName}" deleted successfully!`, 'success');
            
            // Update user server count in session
            if (dashboard.currentUser) {
                dashboard.currentUser.serverCount = Math.max(0, (dashboard.currentUser.serverCount || 0) - 1);
            }
            
            // Refresh servers and dashboard data
            await dashboard.loadServers();
            await dashboard.loadResourceUsage();
            dashboard.updateDashboardStats();
        } else {
            dashboard.showNotification(data.error || 'Failed to delete server', 'error');
        }
    } catch (error) {
        console.error('Error deleting server:', error);
        dashboard.showNotification('Error deleting server', 'error');
    }
}

// Add CSS animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .btn-danger {
        background: #ef4444;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .btn-danger:hover {
        background: #dc2626;
    }
`;
document.head.appendChild(style);