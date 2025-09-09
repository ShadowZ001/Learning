# 🚀 cPanel Node.js Deployment Guide

## Required Files for cPanel

### ✅ Entry Points
- **`app.js`** - Main entry point for cPanel
- **`startup.js`** - Alternative startup file
- **`.htaccess`** - URL rewriting for cPanel

### ✅ cPanel Node.js Setup

#### 1. **Node.js App Settings**
```
Application Root: /public_html/blazenode-landing
Application URL: https://yourdomain.com
Application Startup File: app.js
```

#### 2. **Environment Variables**
Set these in cPanel Node.js interface:
```
NODE_ENV=production
PORT=3000
MONGODB_URI=your_mongodb_connection_string
SESSION_SECRET=your_session_secret
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_REDIRECT_URI=https://yourdomain.com/auth/callback
DISCORD_GUILD_ID=your_discord_server_id
BOT_API_KEY=your_discord_bot_token
PTERODACTYL_URL=https://panel.blazenode.site
PTERODACTYL_API_KEY=your_pterodactyl_api_key
ADMIN_EMAIL=dereckrich8@gmail.com
```

#### 3. **File Structure**
```
/public_html/blazenode-landing/
├── app.js              # cPanel entry point
├── index.js            # Main application
├── startup.js          # Alternative startup
├── .htaccess           # URL rewriting
├── package.json        # Dependencies
├── config.js           # Configuration
├── dashboard.html      # Dashboard page
├── dashboard.js        # Dashboard logic
├── dashboard.css       # Styles
├── index.html          # Login page
├── script.js           # Login logic
├── styles.css          # Login styles
├── auth/               # Discord auth utilities
├── models/             # Database models
└── middleware/         # Express middleware
```

## 🔧 Deployment Steps

### 1. **Upload Files**
- Upload all files to `/public_html/blazenode-landing/`
- Ensure file permissions are correct (644 for files, 755 for directories)

### 2. **Install Dependencies**
In cPanel Terminal:
```bash
cd /public_html/blazenode-landing
npm install --production
```

### 3. **Configure Node.js App**
- Go to cPanel → Node.js
- Create new application
- Set startup file to `app.js`
- Add environment variables

### 4. **Start Application**
- Click "Start" in cPanel Node.js interface
- Check logs for any errors

## ✅ Verification

### Test URLs:
- **Login**: `https://yourdomain.com/`
- **Dashboard**: `https://yourdomain.com/dashboard.html`
- **Health Check**: `https://yourdomain.com/api/health`

### Expected Response:
```json
{
  "status": "OK",
  "timestamp": "2025-01-27T...",
  "server": { "uptime": 123, "memory": "45MB" },
  "database": { "connected": true },
  "session": { "exists": true }
}
```

## 🚨 Common Issues

### Issue 1: Module Not Found
**Solution**: Run `npm install` in correct directory

### Issue 2: Database Connection Failed
**Solution**: Check MONGODB_URI environment variable

### Issue 3: Discord OAuth Not Working
**Solution**: Verify Discord app settings and redirect URI

### Issue 4: Session Issues
**Solution**: Check SESSION_SECRET is set

## 📞 Support

If deployment fails:
1. Check cPanel error logs
2. Verify all environment variables
3. Test database connection
4. Check Discord app configuration

---
**Status**: Production Ready ✅  
**Last Updated**: 2025-01-27