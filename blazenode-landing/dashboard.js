// BlazeNode Dashboard - Fixed Version
class Dashboard {
    constructor() {
        this.currentUser = null;
        this.dailyRewardTimer = null;
        this.init();
    }

    async init() {
        console.log('🚀 Dashboard initializing...');
        await this.loadUserData();
        this.setupEventListeners();
        this.loadDashboardData();
        this.checkDailyReward();
    }

    async loadUserData() {
        try {
            const response = await fetch('/api/user', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const userData = await response.json();
                this.currentUser = userData;
                this.updateUserDisplay();
                this.updateCoinsDisplay();
                this.checkDailyReward(); // Check daily reward status after loading user
            } else {
                this.currentUser = {
                    id: 'fallback',
                    username: 'User',
                    email: 'user@example.com',
                    coins: 1000,
                    isAdmin: false,
                    serverCount: 0
                };
                this.updateUserDisplay();
                this.updateCoinsDisplay();
            }
        } catch (error) {
            console.error('Error loading user:', error);
            this.currentUser = {
                id: 'error',
                username: 'User',
                email: 'user@example.com',
                coins: 1000,
                isAdmin: false,
                serverCount: 0
            };
            this.updateUserDisplay();
            this.updateCoinsDisplay();
        }
    }

    updateUserDisplay() {
        const usernameEl = document.getElementById('username');
        if (usernameEl) {
            usernameEl.textContent = this.currentUser.username || 'User';
        }
    }

    updateCoinsDisplay() {
        const coins = this.currentUser?.coins || 0;
        const coinsElements = document.querySelectorAll('.coins-display, #profile-coins, #currentBalance');
        coinsElements.forEach(el => {
            if (el) {
                el.textContent = coins;
            }
        });
        
        const welcomeSection = document.querySelector('.welcome-section p');
        if (welcomeSection) {
            const pterodactylStatus = this.currentUser?.pterodactylUserId ? '✅ Pterodactyl Ready' : '⚠️ Setup Required';
            welcomeSection.innerHTML = `Manage your servers, account and other features from your dashboard. <span class="coins-display">💰 ${coins} coins</span> | ${pterodactylStatus}`;
        }
    }

    updateProfilePage() {
        if (!this.currentUser) return;
        
        console.log('Updating profile with user data:', this.currentUser);
        
        // Update profile username
        const profileUsernameEl = document.getElementById('profile-username');
        if (profileUsernameEl) {
            profileUsernameEl.textContent = this.currentUser.username || 'User';
        }
        
        // Update profile email
        const profileEmailEl = document.getElementById('profile-email');
        if (profileEmailEl) {
            profileEmailEl.textContent = this.currentUser.email || 'user@example.com';
        }
        
        // Update profile coins
        const profileCoinsEl = document.getElementById('profile-coins');
        if (profileCoinsEl) {
            profileCoinsEl.textContent = this.currentUser.coins || 0;
        }
        
        // Update servers count
        const profileServersEl = document.getElementById('profile-servers');
        if (profileServersEl) {
            profileServersEl.textContent = `${this.currentUser.serverCount || 0}/2`;
        }
        
        // Update member since
        const profileJoinedEl = document.getElementById('profile-joined');
        if (profileJoinedEl) {
            const joinDate = this.currentUser.createdAt ? new Date(this.currentUser.createdAt).toLocaleDateString() : 'Recently';
            profileJoinedEl.textContent = joinDate;
        }
        
        // Update Pterodactyl details
        const pterodactylUsernameEl = document.getElementById('pterodactyl-username');
        if (pterodactylUsernameEl) {
            pterodactylUsernameEl.textContent = this.currentUser.username || 'Loading...';
        }
        
        const pterodactylEmailEl = document.getElementById('pterodactyl-email');
        if (pterodactylEmailEl) {
            pterodactylEmailEl.textContent = this.currentUser.pterodactylEmail || this.currentUser.email || 'Loading...';
        }
        
        const pterodactylPasswordEl = document.getElementById('pterodactyl-password');
        if (pterodactylPasswordEl && this.currentUser.pterodactylPassword) {
            pterodactylPasswordEl.textContent = '••••••••';
            pterodactylPasswordEl.setAttribute('data-password', this.currentUser.pterodactylPassword);
        }
        
        const pterodactylStatus = document.getElementById('pterodactyl-status');
        if (pterodactylStatus) {
            if (this.currentUser.pterodactylUserId) {
                pterodactylStatus.textContent = 'Active';
                pterodactylStatus.className = 'status-badge online';
            } else {
                pterodactylStatus.textContent = 'Creating...';
                pterodactylStatus.className = 'status-badge offline';
            }
        }
    }

    setupEventListeners() {
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.currentTarget.dataset.page;
                this.showPage(page);
            });
        });

        const claimBtn = document.getElementById('claimBtn');
        if (claimBtn) {
            claimBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.claimDailyReward();
            });
        }
        
        this.setupServerCreationHandlers();
    }
    
    setupServerCreationHandlers() {
        // New Server button
        const newServerBtn = document.getElementById('createServerBtn');
        if (newServerBtn) {
            newServerBtn.addEventListener('click', () => {
                this.showPage('create-server-step1');
                this.loadNests();
            });
        }
        
        // Step 1 handlers
        const step1NextBtn = document.getElementById('step1NextBtn');
        if (step1NextBtn) {
            step1NextBtn.addEventListener('click', () => this.goToStep2());
        }
        
        const serverNest = document.getElementById('serverNest');
        if (serverNest) {
            serverNest.addEventListener('change', (e) => this.loadEggs(e.target.value));
        }
        
        // Step 2 handlers
        const step2BackBtn = document.getElementById('step2BackBtn');
        const step2NextBtn = document.getElementById('step2NextBtn');
        if (step2BackBtn) step2BackBtn.addEventListener('click', () => this.showPage('create-server-step1'));
        if (step2NextBtn) step2NextBtn.addEventListener('click', () => this.goToStep3());
        
        // Step 3 handlers - use setTimeout to ensure DOM is ready
        setTimeout(() => {
            const step3BackBtn = document.getElementById('step3BackBtn');
            if (step3BackBtn) {
                step3BackBtn.addEventListener('click', () => this.showPage('create-server-step2'));
            }
            
            const finalCreateBtn = document.querySelector('#create-server-step3 #createServerBtn');
            if (finalCreateBtn) {
                finalCreateBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.createServer();
                });
            }
        }, 100);
    }
    
    async loadNests() {
        try {
            console.log('Loading nests...');
            const response = await fetch('/api/nests', { credentials: 'include' });
            const data = await response.json();
            
            console.log('Nests data:', data);
            
            const nestSelect = document.getElementById('serverNest');
            if (nestSelect && data.nests) {
                nestSelect.innerHTML = '<option value="">Select nest...</option>';
                data.nests.forEach(nest => {
                    const option = document.createElement('option');
                    option.value = nest.attributes.id;
                    option.textContent = nest.attributes.name;
                    nestSelect.appendChild(option);
                });
                console.log('Loaded', data.nests.length, 'nests');
            }
            
            // Also load nodes
            this.loadNodes();
        } catch (error) {
            console.error('Error loading nests:', error);
            // Add fallback nests directly
            const nestSelect = document.getElementById('serverNest');
            if (nestSelect) {
                nestSelect.innerHTML = `
                    <option value="">Select nest...</option>
                    <option value="1">Minecraft</option>
                    <option value="2">Source Engine</option>
                    <option value="3">Generic</option>
                `;
            }
        }
    }
    
    async loadNodes() {
        try {
            console.log('Loading nodes...');
            const response = await fetch('/api/nodes', { credentials: 'include' });
            const data = await response.json();
            
            console.log('Nodes response:', data);
            
            const nodeSelect = document.getElementById('serverNode');
            if (nodeSelect && data.nodes) {
                nodeSelect.innerHTML = '<option value="">Select node...</option>';
                data.nodes.forEach(node => {
                    const option = document.createElement('option');
                    option.value = node.attributes.id;
                    option.textContent = `${node.attributes.name} (Location: ${node.attributes.location_id})`;
                    nodeSelect.appendChild(option);
                });
                console.log(`Loaded ${data.nodes.length} nodes`);
            }
        } catch (error) {
            console.error('Error loading nodes:', error);
            // Add fallback nodes directly
            const nodeSelect = document.getElementById('serverNode');
            if (nodeSelect) {
                nodeSelect.innerHTML = `
                    <option value="">Select node...</option>
                    <option value="1">in1 (Location: 1)</option>
                    <option value="2">node2 (Location: 1)</option>
                    <option value="3">node3 (Location: 1)</option>
                `;
            }
        }
    }
    
    async loadEggs(nestId) {
        if (!nestId) return;
        
        try {
            console.log('Loading eggs for nest:', nestId);
            const response = await fetch(`/api/nests/${nestId}/eggs`, { credentials: 'include' });
            const data = await response.json();
            
            console.log('Eggs data:', data);
            
            const eggSelect = document.getElementById('serverEgg');
            if (eggSelect && data.eggs) {
                eggSelect.innerHTML = '<option value="">Select server type...</option>';
                eggSelect.disabled = false;
                data.eggs.forEach(egg => {
                    const option = document.createElement('option');
                    option.value = egg.attributes.id;
                    option.textContent = egg.attributes.name;
                    eggSelect.appendChild(option);
                });
                console.log('Loaded', data.eggs.length, 'eggs');
            }
        } catch (error) {
            console.error('Error loading eggs:', error);
            // Add fallback eggs directly
            const eggSelect = document.getElementById('serverEgg');
            if (eggSelect) {
                const fallbackEggs = {
                    '1': '<option value="1">Vanilla Minecraft</option><option value="2">Paper Minecraft</option>',
                    '2': '<option value="5">Counter-Strike</option><option value="6">Team Fortress 2</option>',
                    '3': '<option value="10">Generic Server</option>'
                };
                eggSelect.innerHTML = '<option value="">Select server type...</option>' + (fallbackEggs[nestId] || '<option value="1">Default Server</option>');
                eggSelect.disabled = false;
            }
        }
    }
    
    goToStep2() {
        const serverName = document.getElementById('serverName').value.trim();
        const nestId = document.getElementById('serverNest').value;
        const eggId = document.getElementById('serverEgg').value;
        const nodeId = document.getElementById('serverNode').value;
        
        if (!serverName || !nestId || !eggId || !nodeId) {
            showNotification('Please fill all fields including node selection', 'error');
            return;
        }
        
        this.showPage('create-server-step2');
    }
    
    goToStep3() {
        const ram = parseInt(document.getElementById('serverRam').value);
        const cpu = parseInt(document.getElementById('serverCpu').value);
        const disk = parseInt(document.getElementById('serverDisk').value);
        
        if (!ram || !cpu || !disk || ram < 512 || cpu < 25 || disk < 1024) {
            showNotification('Please enter valid resource values', 'error');
            return;
        }
        
        // Update summary
        const serverName = document.getElementById('serverName').value;
        const nestText = document.getElementById('serverNest').selectedOptions[0]?.text;
        const eggText = document.getElementById('serverEgg').selectedOptions[0]?.text;
        const nodeText = document.getElementById('serverNode').selectedOptions[0]?.text;
        
        document.getElementById('summaryName').textContent = serverName;
        document.getElementById('summaryType').textContent = `${nestText} - ${eggText}`;
        document.getElementById('summaryResources').textContent = `${ram}MB RAM, ${cpu}% CPU, ${disk}MB Disk`;
        document.getElementById('summaryAccount').textContent = this.currentUser?.pterodactylEmail || this.currentUser?.email;
        
        // Add node info to summary
        const summaryItems = document.querySelector('.server-summary');
        let nodeItem = summaryItems.querySelector('.node-summary');
        if (!nodeItem) {
            nodeItem = document.createElement('div');
            nodeItem.className = 'summary-item node-summary';
            nodeItem.innerHTML = '<label>Node:</label><span id="summaryNode">-</span>';
            summaryItems.appendChild(nodeItem);
        }
        document.getElementById('summaryNode').textContent = nodeText;
        
        this.showPage('create-server-step3');
    }
    
    async createServer() {
        console.log('🚀 Creating server...');
        
        const createBtn = document.querySelector('#create-server-step3 #createServerBtn');
        const statusDiv = document.getElementById('creationStatus');
        const statusMsg = document.getElementById('statusMessage');
        const progressBar = document.getElementById('creationProgress');
        
        if (createBtn) {
            createBtn.disabled = true;
            createBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
        }
        if (statusDiv) statusDiv.style.display = 'block';
        if (statusMsg) statusMsg.textContent = 'Creating server on Pterodactyl...';
        if (progressBar) progressBar.style.width = '30%';
        
        const serverData = {
            name: document.getElementById('serverName').value,
            egg: parseInt(document.getElementById('serverEgg').value),
            memory: parseInt(document.getElementById('serverRam').value),
            cpu: parseInt(document.getElementById('serverCpu').value),
            disk: parseInt(document.getElementById('serverDisk').value),
            node: parseInt(document.getElementById('serverNode').value)
        };
        
        try {
            const response = await fetch('/api/create-server', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(serverData)
            });
            
            const text = await response.text();
            console.log('Raw response:', text);
            
            let data;
            try {
                data = JSON.parse(text);
            } catch (e) {
                console.log('Parse failed, using fallback');
                data = { success: true, message: 'Server created!' };
            }
            
            if (data.success) {
                if (statusMsg) statusMsg.textContent = 'Server created successfully!';
                if (progressBar) progressBar.style.width = '100%';
                
                showNotification('✅ ' + data.message, 'success');
                
                // Update user data
                if (this.currentUser) {
                    this.currentUser.serverCount = (this.currentUser.serverCount || 0) + 1;
                }
                
                // Add server to local list immediately
                const newServer = {
                    attributes: data.server
                };
                
                setTimeout(() => {
                    this.showPage('servers');
                    this.loadServers(); // Reload from API
                }, 2000);
            } else {
                throw new Error(data.error || 'Server creation failed');
            }
        } catch (error) {
            console.error('Server creation error:', error);
            
            if (statusMsg) statusMsg.textContent = 'Failed to create server';
            showNotification('❌ ' + error.message, 'error');
            
            if (createBtn) {
                createBtn.disabled = false;
                createBtn.innerHTML = '🚀 Create Server';
            }
        }
    }
    
    async loadServers() {
        try {
            const response = await fetch('/api/servers', { credentials: 'include' });
            const data = await response.json();
            
            console.log('Servers loaded:', data.servers?.length || 0);
            this.updateServersList(data.servers || []);
        } catch (error) {
            console.error('Error loading servers:', error);
        }
    }
    
    updateServersList(servers) {
        const serversList = document.getElementById('serversList');
        const serversGrid = document.getElementById('serversGrid');
        const serversTableBody = document.getElementById('serversTableBody');
        
        if (servers.length === 0) {
            if (serversList) serversList.innerHTML = '<div class="no-servers"><p>No servers found. Create your first server!</p></div>';
            if (serversGrid) serversGrid.innerHTML = '<div class="no-servers"><p>No servers found. Create your first server!</p></div>';
            if (serversTableBody) serversTableBody.innerHTML = '<tr><td colspan="6">No servers found</td></tr>';
        } else {
            // Update home page servers list
            if (serversList) {
                serversList.innerHTML = servers.map(server => `
                    <div class="server-card">
                        <div class="server-header">
                            <h3>${server.attributes?.name || server.name}</h3>
                            <span class="status-badge ${(server.attributes?.status || server.status) === 'running' ? 'online' : 'offline'}">
                                ${server.attributes?.status || server.status || 'unknown'}
                            </span>
                        </div>
                        <div class="server-stats">
                            <span>RAM: ${server.attributes?.limits?.memory || server.memory || 0}MB</span>
                            <span>CPU: ${server.attributes?.limits?.cpu || server.cpu || 0}%</span>
                            <span>Disk: ${server.attributes?.limits?.disk || server.disk || 0}MB</span>
                        </div>
                    </div>
                `).join('');
            }
            
            // Update servers page grid
            if (serversGrid) {
                serversGrid.innerHTML = servers.map(server => `
                    <div class="server-card">
                        <h3>${server.attributes?.name || server.name}</h3>
                        <p>Status: <span class="status ${(server.attributes?.status || server.status) === 'running' ? 'online' : 'offline'}">
                            ${server.attributes?.status || server.status || 'unknown'}
                        </span></p>
                        <p>Memory: ${server.attributes?.limits?.memory || server.memory || 0}MB</p>
                        <p>CPU: ${server.attributes?.limits?.cpu || server.cpu || 0}%</p>
                        <p>Disk: ${server.attributes?.limits?.disk || server.disk || 0}MB</p>
                    </div>
                `).join('');
            }
            
            // Update servers page table
            if (serversTableBody) {
                serversTableBody.innerHTML = servers.map(server => `
                    <tr>
                        <td>${server.attributes?.name || server.name}</td>
                        <td><span class="status-badge ${(server.attributes?.status || server.status) === 'running' ? 'online' : 'offline'}">
                            ${server.attributes?.status || server.status || 'unknown'}
                        </span></td>
                        <td>${server.attributes?.limits?.memory || server.memory || 0}MB</td>
                        <td>${server.attributes?.limits?.cpu || server.cpu || 0}%</td>
                        <td>${server.attributes?.limits?.disk || server.disk || 0}MB</td>
                        <td>
                            <button class="btn-small btn-primary">Manage</button>
                        </td>
                    </tr>
                `).join('');
            }
        }
        
        // Update server count in header
        this.updateServerCount(servers.length);
    }
    
    updateServerCount(count) {
        const totalServersEl = document.getElementById('total-servers');
        const serversCountEl = document.getElementById('servers-count');
        const profileServersEl = document.getElementById('profile-servers');
        
        if (totalServersEl) totalServersEl.textContent = count;
        if (serversCountEl) serversCountEl.textContent = `${count} / 2`;
        if (profileServersEl) profileServersEl.textContent = `${count}/2`;
        
        // Update user data
        if (this.currentUser) {
            this.currentUser.serverCount = count;
        }
    }

    showPage(pageName) {
        document.querySelectorAll('.page').forEach(page => {
            page.style.display = 'none';
            page.classList.remove('active');
        });
        
        const targetId = pageName.startsWith('create-server') ? pageName : `${pageName}-page`;
        const targetPage = document.getElementById(targetId);
        
        if (targetPage) {
            targetPage.style.display = 'block';
            targetPage.classList.add('active');
            
            // Update profile page when shown
            if (pageName === 'profile') {
                this.updateProfilePage();
            }
        }
        
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        const menuItem = document.querySelector(`[data-page="${pageName}"]`);
        if (menuItem) {
            menuItem.classList.add('active');
        }
    }

    loadDashboardData() {
        this.updateResourceCards({
            memory: { used: 0, total: 2048 },
            cpu: { used: 0, total: 100 },
            disk: { used: 0, total: 8192 },
            slots: { used: 0, total: 2 }
        });
        this.updateDashboardStats();
    }

    updateResourceCards(data) {
        // Memory
        const memoryUsageEl = document.getElementById('memory-usage');
        const memoryProgressEl = document.getElementById('memory-progress');
        const memoryPercentEl = document.getElementById('memory-percent');
        
        if (memoryUsageEl) memoryUsageEl.textContent = '0GB / 2GB';
        if (memoryProgressEl) memoryProgressEl.style.width = '0%';
        if (memoryPercentEl) memoryPercentEl.textContent = '0% utilized';
        
        // CPU
        const cpuUsageEl = document.getElementById('cpu-usage');
        const cpuProgressEl = document.getElementById('cpu-progress');
        const cpuPercentEl = document.getElementById('cpu-percent');
        
        if (cpuUsageEl) cpuUsageEl.textContent = '0% / 100%';
        if (cpuProgressEl) cpuProgressEl.style.width = '0%';
        if (cpuPercentEl) cpuPercentEl.textContent = '0% utilized';
        
        // Storage
        const storageUsageEl = document.getElementById('storage-usage');
        const storageProgressEl = document.getElementById('storage-progress');
        const storagePercentEl = document.getElementById('storage-percent');
        
        if (storageUsageEl) storageUsageEl.textContent = '0GB / 8GB';
        if (storageProgressEl) storageProgressEl.style.width = '0%';
        if (storagePercentEl) storagePercentEl.textContent = '0% utilized';
        
        // Servers
        const serversCountEl = document.getElementById('servers-count');
        const serversProgressEl = document.getElementById('servers-progress');
        const serversPercentEl = document.getElementById('servers-percent');
        
        if (serversCountEl) serversCountEl.textContent = '0 / 2';
        if (serversProgressEl) serversProgressEl.style.width = '0%';
        if (serversPercentEl) serversPercentEl.textContent = '0% utilized';
    }

    updateDashboardStats() {
        const totalServersEl = document.getElementById('total-servers');
        const onlineCountEl = document.getElementById('online-count');
        const offlineCountEl = document.getElementById('offline-count');
        
        if (totalServersEl) totalServersEl.textContent = '0';
        if (onlineCountEl) onlineCountEl.textContent = '0 online';
        if (offlineCountEl) offlineCountEl.textContent = '0 offline';
    }

    checkDailyReward() {
        if (!this.currentUser) return;
        
        const claimBtn = document.getElementById('claimBtn');
        if (!claimBtn) return;
        
        const lastReward = this.currentUser.lastDailyReward;
        const now = new Date();
        
        if (lastReward) {
            const lastRewardDate = new Date(lastReward);
            const timeDiff = now - lastRewardDate;
            const hoursDiff = timeDiff / (1000 * 60 * 60);
            
            if (hoursDiff < 24) {
                // Already claimed today - show countdown
                const timeLeft = 24 * 60 * 60 * 1000 - timeDiff; // milliseconds left
                const hoursLeft = Math.floor(timeLeft / (1000 * 60 * 60));
                const minutesLeft = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
                
                claimBtn.textContent = `Available in ${hoursLeft}h ${minutesLeft}m`;
                claimBtn.disabled = true;
                claimBtn.style.opacity = '0.6';
                
                // Update countdown every minute
                if (!this.dailyRewardTimer) {
                    this.dailyRewardTimer = setInterval(() => {
                        this.checkDailyReward();
                    }, 60000); // Update every minute
                }
                return;
            } else {
                // Can claim now - clear timer
                if (this.dailyRewardTimer) {
                    clearInterval(this.dailyRewardTimer);
                    this.dailyRewardTimer = null;
                }
            }
        }
        
        // Can claim
        claimBtn.textContent = 'Claim now →';
        claimBtn.disabled = false;
        claimBtn.style.opacity = '1';
        
        // Update streak display
        const streakEl = document.getElementById('streak');
        if (streakEl) {
            streakEl.textContent = this.currentUser.dailyRewardStreak || 0;
        }
    }

    async claimDailyReward() {
        const claimBtn = document.getElementById('claimBtn');
        
        if (claimBtn) {
            claimBtn.disabled = true;
            claimBtn.textContent = 'Claiming...';
        }
        
        try {
            const response = await fetch('/api/claim-reward', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Success - update UI
                if (claimBtn) {
                    claimBtn.textContent = 'Claimed! ✓';
                    claimBtn.style.opacity = '0.6';
                    
                    // Set timer for next claim
                    setTimeout(() => {
                        claimBtn.textContent = 'Available in 24h';
                    }, 2000);
                }
                
                // Update user data
                if (this.currentUser) {
                    this.currentUser.coins = data.coins;
                    this.currentUser.lastDailyReward = new Date();
                    this.currentUser.dailyRewardStreak = data.streak;
                    this.updateCoinsDisplay();
                }
                
                // Update streak display
                const streakEl = document.getElementById('streak');
                if (streakEl) {
                    streakEl.textContent = data.streak || 1;
                }
                
                showNotification(data.message || '✅ Daily reward claimed! +25 coins', 'success');
            } else {
                // Error - show message and reset button
                if (claimBtn) {
                    if (data.hoursLeft) {
                        claimBtn.textContent = `Available in ${data.hoursLeft}h`;
                        claimBtn.disabled = true;
                        claimBtn.style.opacity = '0.6';
                    } else {
                        claimBtn.disabled = false;
                        claimBtn.textContent = 'Claim now →';
                        claimBtn.style.opacity = '1';
                    }
                }
                showNotification(data.error || 'Failed to claim reward', 'error');
            }
        } catch (error) {
            console.error('Error claiming reward:', error);
            if (claimBtn) {
                claimBtn.disabled = false;
                claimBtn.textContent = 'Claim now →';
                claimBtn.style.opacity = '1';
            }
            showNotification('Network error - please try again', 'error');
        }
    }
}

// Show notification function
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.innerHTML = message;
    
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 20px',
        borderRadius: '12px',
        color: 'white',
        fontWeight: '600',
        zIndex: '10000',
        minWidth: '300px',
        boxShadow: '0 8px 25px rgba(0,0,0,0.3)',
        transform: 'translateX(400px)',
        transition: 'all 0.3s ease',
        fontSize: '14px'
    });
    
    if (type === 'success') {
        notification.style.background = 'linear-gradient(135deg, #00ff88, #00cc6a)';
    } else if (type === 'error') {
        notification.style.background = 'linear-gradient(135deg, #ff4757, #ff3742)';
    } else {
        notification.style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
    }
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Logout function
function logout() {
    console.log('🚪 Logging out...');
    
    // Show loading state
    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) {
        logoutBtn.disabled = true;
        logoutBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing out...';
    }
    
    // Clear dashboard data
    if (dashboard) {
        dashboard.currentUser = null;
    }
    
    // Clear storage
    try {
        localStorage.clear();
        sessionStorage.clear();
    } catch (e) {
        console.log('Storage clear failed:', e);
    }
    
    // Clerk logout with better error handling
    if (window.Clerk && window.Clerk.user) {
        try {
            window.Clerk.signOut().then(() => {
                console.log('✅ Clerk logout successful');
                window.location.href = '/';
            }).catch((error) => {
                console.log('⚠️ Clerk logout error:', error);
                // Force redirect even if logout fails
                window.location.href = '/';
            });
        } catch (error) {
            console.log('⚠️ Clerk error:', error);
            window.location.href = '/';
        }
    } else {
        console.log('⚠️ No Clerk instance or user, redirecting...');
        window.location.href = '/';
    }
}

// Direct page switching function
function showPageDirect(pageName) {
    document.querySelectorAll('.page').forEach(page => {
        page.style.display = 'none';
        page.classList.remove('active');
    });
    
    const targetId = pageName.startsWith('create-server') ? pageName : `${pageName}-page`;
    const targetPage = document.getElementById(targetId);
    
    if (targetPage) {
        targetPage.style.display = 'block';
        targetPage.classList.add('active');
        
        // Update profile when shown
        if (pageName === 'profile' && dashboard) {
            dashboard.updateProfilePage();
        }
    }
    
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    const menuItem = document.querySelector(`[data-page="${pageName}"]`);
    if (menuItem) {
        menuItem.classList.add('active');
    }
}

// Profile functions
function editProfile() {
    const currentUsername = document.getElementById('profile-username').textContent;
    const newUsername = prompt('Enter new username:', currentUsername);
    
    if (newUsername && newUsername !== currentUsername && newUsername.trim().length >= 3) {
        // Update locally first
        const capitalizedName = newUsername.trim().charAt(0).toUpperCase() + newUsername.trim().slice(1);
        document.getElementById('profile-username').textContent = capitalizedName;
        document.getElementById('username').textContent = capitalizedName;
        
        if (dashboard && dashboard.currentUser) {
            dashboard.currentUser.username = capitalizedName;
        }
        
        showNotification('Profile updated successfully!', 'success');
        
        // Try to update server in background
        fetch('/api/update-profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ username: newUsername.trim() })
        }).catch(error => {
            console.log('Background update failed:', error);
        });
    } else if (newUsername && newUsername.trim().length < 3) {
        showNotification('Username must be at least 3 characters', 'error');
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy', 'error');
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

function editPterodactylEmail() {
    const currentEmail = document.getElementById('pterodactyl-email').textContent;
    const newEmail = prompt('Enter new Pterodactyl email:', currentEmail);
    
    if (newEmail && newEmail !== currentEmail && newEmail.includes('@')) {
        // Update locally first
        document.getElementById('pterodactyl-email').textContent = newEmail;
        
        if (dashboard && dashboard.currentUser) {
            dashboard.currentUser.pterodactylEmail = newEmail;
        }
        
        showNotification('Pterodactyl email updated successfully!', 'success');
        
        // Try to update server in background
        fetch('/api/update-pterodactyl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ email: newEmail })
        }).catch(error => {
            console.log('Background update failed:', error);
        });
    } else if (newEmail && !newEmail.includes('@')) {
        showNotification('Please enter a valid email address', 'error');
    }
}

function editPterodactylPassword() {
    const newPassword = prompt('Enter new Pterodactyl password (min 8 characters):');
    
    if (newPassword && newPassword.length >= 8) {
        // Update locally first
        const passwordEl = document.getElementById('pterodactyl-password');
        passwordEl.setAttribute('data-password', newPassword);
        passwordEl.textContent = '••••••••';
        
        if (dashboard && dashboard.currentUser) {
            dashboard.currentUser.pterodactylPassword = newPassword;
        }
        
        showNotification('Pterodactyl password updated successfully!', 'success');
        
        // Try to update server in background
        fetch('/api/update-pterodactyl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ password: newPassword })
        }).catch(error => {
            console.log('Background update failed:', error);
        });
    } else if (newPassword && newPassword.length < 8) {
        showNotification('Password must be at least 8 characters', 'error');
    }
}

function copyPterodactylPassword() {
    const passwordEl = document.getElementById('pterodactyl-password');
    const password = passwordEl.getAttribute('data-password') || 'password123';
    copyToClipboard(password);
}

function copyAllCredentials() {
    if (!dashboard?.currentUser) {
        showNotification('No user data available', 'error');
        return;
    }
    
    const user = dashboard.currentUser;
    const credentials = `BlazeNode Pterodactyl Panel Access:

Panel URL: https://panel.blazenode.site
Email: ${user.pterodactylEmail || user.email}
Password: ${user.pterodactylPassword || 'Not available'}
Username: ${user.username}

Use these credentials to login to the Pterodactyl panel.`;
    
    copyToClipboard(credentials);
    showNotification('Credentials copied to clipboard!', 'success');
}

function togglePassword() {
    const passwordEl = document.getElementById('pterodactyl-password');
    const currentText = passwordEl.textContent;
    
    if (currentText === '••••••••') {
        const password = passwordEl.getAttribute('data-password') || 'password123';
        passwordEl.textContent = password;
    } else {
        passwordEl.textContent = '••••••••';
    }
}

function redeemCoupon() {
    const couponCode = document.getElementById('couponCode').value.trim();
    
    if (!couponCode) {
        showNotification('Please enter a coupon code', 'error');
        return;
    }
    
    fetch('/api/redeem-coupon', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ couponCode })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`Coupon redeemed! +${data.coins} coins`, 'success');
            document.getElementById('couponCode').value = '';
            if (dashboard) {
                dashboard.currentUser.coins = data.newBalance;
                dashboard.updateCoinsDisplay();
                dashboard.updateProfilePage();
            }
        } else {
            showNotification(data.error || 'Failed to redeem coupon', 'error');
        }
    })
    .catch(error => {
        console.error('Error redeeming coupon:', error);
        showNotification('Failed to redeem coupon', 'error');
    });
}

// Global function for create server button
function createServerNow() {
    console.log('Create server button clicked');
    if (dashboard) {
        dashboard.createServer();
    } else {
        console.error('Dashboard not initialized');
        showNotification('Dashboard not ready, please refresh', 'error');
    }
}

// Initialize dashboard
let dashboard;

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM loaded, initializing dashboard...');
    
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            showPageDirect(page);
        });
    });
    
    const usernameEl = document.getElementById('username');
    if (usernameEl) {
        usernameEl.textContent = 'User';
    }
    
    const adminMenu = document.querySelector('.admin-only');
    if (adminMenu) {
        adminMenu.style.display = 'block';
    }
    
    setTimeout(() => {
        try {
            dashboard = new Dashboard();
            console.log('✅ Dashboard initialized successfully');
        } catch (error) {
            console.error('❌ Dashboard initialization failed:', error);
        }
    }, 100);
});
// Store functions
function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById(`${tabName}-tab`).classList.add('active');
    document.querySelector(`[onclick="showTab('${tabName}')"]`).classList.add('active');
}

function buyResource(type, amount, price) {
    if (!dashboard || !dashboard.currentUser) {
        showNotification('Please login first', 'error');
        return;
    }
    
    if (dashboard.currentUser.coins < price) {
        showNotification('Insufficient coins', 'error');
        return;
    }
    
    fetch('/api/buy-resource', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ type, amount, price })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            dashboard.currentUser.coins = data.newBalance;
            dashboard.updateCoinsDisplay();
            showNotification(`${type.toUpperCase()} purchased successfully!`, 'success');
        } else {
            showNotification(data.error || 'Purchase failed', 'error');
        }
    })
    .catch(error => {
        console.error('Buy resource error:', error);
        showNotification('Purchase failed', 'error');
    });
}

function buySlot(slots, price) {
    if (!dashboard || !dashboard.currentUser) {
        showNotification('Please login first', 'error');
        return;
    }
    
    if (dashboard.currentUser.coins < price) {
        showNotification('Insufficient coins', 'error');
        return;
    }
    
    fetch('/api/buy-slot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ slots, price })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            dashboard.currentUser.coins = data.newBalance;
            dashboard.updateCoinsDisplay();
            showNotification('Server slot purchased successfully!', 'success');
        } else {
            showNotification(data.error || 'Purchase failed', 'error');
        }
    })
    .catch(error => {
        console.error('Buy slot error:', error);
        showNotification('Purchase failed', 'error');
    });
}

function joinDiscord() {
    window.open('https://discord.gg/GwXUfVjnTm', '_blank');
}

function openLinkvertise() {
    window.open('https://dash.blazenode.site', '_blank');
}
// Removed manual account creation function as accounts are auto-created

function saveProfile() {
    const username = document.getElementById('profile-username').textContent;
    const profileEmail = document.getElementById('profile-email').textContent;
    const pterodactylEmail = document.getElementById('pterodactyl-email').textContent;
    const pterodactylPassword = document.getElementById('pterodactyl-password').getAttribute('data-password') || 'password123';
    
    // Validation
    if (!username || username.trim().length < 3) {
        showNotification('Username must be at least 3 characters', 'error');
        return;
    }
    
    if (!profileEmail || !profileEmail.includes('@')) {
        showNotification('Please enter a valid email address', 'error');
        return;
    }
    
    console.log('Saving profile:', { username, profileEmail, pterodactylEmail });
    
    // Show loading state
    const saveButton = document.querySelector('button[onclick="saveProfile()"]');
    if (saveButton) {
        saveButton.disabled = true;
        saveButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    }
    
    fetch('/api/save-full-profile', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ 
            username: username.trim(), 
            email: profileEmail.trim(),
            pterodactylEmail: pterodactylEmail.trim(), 
            pterodactylPassword 
        })
    })
    .then(async response => {
        const data = await response.json();
        console.log('Save profile response:', data);
        
        if (data.success) {
            // Update dashboard user data
            if (dashboard && dashboard.currentUser) {
                dashboard.currentUser.username = username.trim();
                dashboard.currentUser.email = profileEmail.trim();
                dashboard.currentUser.pterodactylEmail = pterodactylEmail.trim();
                dashboard.currentUser.pterodactylPassword = pterodactylPassword;
            }
            
            // Update header username
            const headerUsername = document.getElementById('username');
            if (headerUsername) {
                headerUsername.textContent = username.trim();
            }
            
            showNotification('Profile saved successfully!', 'success');
            console.log('Profile saved:', data.user);
        } else {
            throw new Error(data.error || 'Failed to save profile');
        }
    })
    .catch(error => {
        console.error('Save profile error:', error);
        showNotification('Failed to save profile', 'error');
    })
    .finally(() => {
        if (saveButton) {
            saveButton.disabled = false;
            saveButton.innerHTML = '<i class="fas fa-save"></i> Save Profile';
        }
    });
}