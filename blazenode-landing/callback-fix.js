// Discord OAuth callback - FIXED VERSION
app.get('/auth/callback', (req, res, next) => {
    passport.authenticate('discord', (err, user, info) => {
        if (err) {
            console.error("Auth error:", err);
            return res.redirect('/?error=auth_failed');
        }
        if (!user) {
            console.error("No user returned:", info);
            return res.redirect('/?error=no_user');
        }
        req.logIn(user, (loginErr) => {
            if (loginErr) {
                console.error("Login error:", loginErr);
                return next(loginErr);
            }
            console.log("✅ User logged in:", user.id);
            
            // Create session
            req.session.authenticated = true;
            req.session.user = {
                id: user._id.toString(),
                username: user.discordUsername,
                email: user.email,
                discordId: user.discordId,
                coins: user.coins || 1000,
                isAdmin: user.isAdmin || false,
                serverCount: user.serverCount || 0
            };
            
            // Redirect to dashboard
            return res.redirect('/dashboard');
        });
    })(req, res, next);
});

// Dashboard route (if dashboard.html is in root)
app.get('/dashboard.html', (req, res) => {
    if (!req.isAuthenticated || !req.isAuthenticated()) {
        return res.redirect('/?error=not_logged_in');
    }
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});