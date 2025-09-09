const User = require('../models/User');

// Enhanced authentication middleware
const requireAuth = (req, res, next) => {
    if (!req.session || !req.session.user) {
        return res.status(401).json({ 
            error: 'Authentication required',
            redirect: '/'
        });
    }
    next();
};

// Admin authentication middleware
const requireAdmin = async (req, res, next) => {
    if (!req.session || !req.session.user) {
        return res.status(401).json({ 
            error: 'Authentication required',
            redirect: '/'
        });
    }
    
    try {
        const user = await User.findById(req.session.user.id);
        if (!user || !user.isAdmin) {
            return res.status(403).json({ 
                error: 'Admin access required'
            });
        }
        
        req.user = user;
        next();
    } catch (error) {
        return res.status(500).json({ 
            error: 'Authentication error'
        });
    }
};

// Rate limiting middleware
const rateLimiter = (maxRequests = 10, windowMs = 60000) => {
    const requests = new Map();
    
    return (req, res, next) => {
        const ip = req.ip || req.connection.remoteAddress;
        const now = Date.now();
        
        if (!requests.has(ip)) {
            requests.set(ip, { count: 1, resetTime: now + windowMs });
            return next();
        }
        
        const requestData = requests.get(ip);
        
        if (now > requestData.resetTime) {
            requestData.count = 1;
            requestData.resetTime = now + windowMs;
            return next();
        }
        
        if (requestData.count >= maxRequests) {
            return res.status(429).json({
                error: 'Too many requests',
                retryAfter: Math.ceil((requestData.resetTime - now) / 1000)
            });
        }
        
        requestData.count++;
        next();
    };
};

module.exports = {
    requireAuth,
    requireAdmin,
    rateLimiter
};