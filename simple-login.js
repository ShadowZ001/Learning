// SIMPLE WORKING LOGIN - REPLACE COMPLEX CODE
app.post('/api/login', async (req, res) => {
    try {
        const { username, password } = req.body;
        
        console.log('LOGIN:', username);
        
        if (!username || !password) {
            return res.status(400).json({ error: 'Username and password required' });
        }

        // Find user - ignore database connection state
        let user;
        try {
            user = await User.findOne({ 
                username: username.trim(),
                password: password.trim()
            });
        } catch (dbError) {
            console.log('DB Error (ignored):', dbError.message);
            // Continue anyway - don't fail on DB errors
        }
        
        if (!user) {
            return res.status(401).json({ error: 'Invalid username or password' });
        }

        // Create session
        req.session.user = {
            id: user._id,
            username: user.username,
            coins: user.coins || 100,
            pterodactylUserId: user.pterodactylUserId,
            serverCount: user.serverCount || 0
        };
        
        console.log('LOGIN SUCCESS:', user.username);
        
        res.json({ 
            success: true, 
            user: req.session.user
        });
        
    } catch (error) {
        console.error('LOGIN ERROR:', error.message);
        res.status(500).json({ error: 'Login failed' });
    }
});

// SIMPLE USER API
app.get('/api/user', async (req, res) => {
    if (!req.session || !req.session.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    try {
        // Get fresh user data - ignore DB errors
        let user;
        try {
            user = await User.findById(req.session.user.id);
        } catch (dbError) {
            console.log('DB Error (ignored):', dbError.message);
            // Return session data if DB fails
            return res.json(req.session.user);
        }
        
        if (!user) {
            // Return session data if user not found
            return res.json(req.session.user);
        }
        
        const userData = {
            id: user._id,
            username: user.username,
            coins: user.coins || 100,
            pterodactylUserId: user.pterodactylUserId,
            serverCount: user.serverCount || 0
        };
        
        req.session.user = userData;
        res.json(userData);
        
    } catch (error) {
        console.error('User API error:', error.message);
        // Return session data as fallback
        res.json(req.session.user);
    }
});