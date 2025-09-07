# BlazeNode Dashboard - cPanel Deployment Guide

## Files Structure for cPanel
```
blazenode-dashboard/
├── index.js          # Main application file (renamed from server.js)
├── app.js            # cPanel entry point
├── startup.js        # cPanel startup script
├── config.js         # Configuration (replaces .env)
├── .htaccess         # Apache configuration
├── package.json      # Dependencies
├── dashboard.html    # Frontend files
├── dashboard.js
├── dashboard.css
├── models/           # Database models
└── ...
```

## cPanel Deployment Steps

### 1. Upload Files
- Upload all files to your cPanel public_html directory
- Make sure Node.js is enabled in cPanel

### 2. cPanel Node.js Setup
- Go to cPanel → Node.js
- Create new Node.js app
- Set Application Root: `/public_html` (or your domain folder)
- Set Application URL: your domain
- Set Application Startup File: `app.js`
- Node.js Version: 18.x or higher

### 3. Install Dependencies
In cPanel Terminal or File Manager:
```bash
npm install
```

### 4. Configuration
- Edit `config.js` with your actual values:
  - MongoDB connection string
  - Pterodactyl API credentials
  - Session secrets

### 5. Start Application
- In cPanel Node.js interface, click "Start App"
- Or use Terminal: `node app.js`

## Important Notes

### ✅ What's Changed for cPanel:
- ❌ Removed `.env` files (not supported by cPanel)
- ✅ Added `config.js` for configuration
- ✅ Renamed `server.js` to `index.js`
- ✅ Added `app.js` as cPanel entry point
- ✅ Removed port configuration (cPanel handles this)
- ✅ Added `.htaccess` for Apache
- ✅ Removed `dotenv` dependency

### 🔧 Configuration Files:
- **config.js**: Contains all environment variables
- **app.js**: cPanel entry point with port handling
- **index.js**: Main application logic
- **.htaccess**: Apache rewrite rules and security headers

### 🚀 Ready for Production:
- All security features intact
- Database connections working
- API endpoints functional
- Static file serving configured
- CORS headers properly set

## Troubleshooting

### Common Issues:
1. **Node.js not starting**: Check cPanel Node.js logs
2. **Database connection**: Verify MongoDB URI in config.js
3. **Static files not loading**: Check .htaccess configuration
4. **API errors**: Verify Pterodactyl credentials in config.js

### Support:
- Check cPanel Error Logs
- Monitor Node.js application logs
- Verify all dependencies are installed