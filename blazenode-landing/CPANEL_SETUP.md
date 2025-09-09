# 🚀 cPanel Deployment Guide

## 📋 **What You Need to Replace in config.js**

### 🔧 **Required Changes:**

1. **MONGODB_URI** - Replace with your MongoDB connection string
   ```js
   MONGODB_URI: 'mongodb+srv://username:password@cluster.mongodb.net/database'
   ```

2. **SESSION_SECRET** - Generate a random secret key
   ```js
   SESSION_SECRET: 'your_random_32_character_secret_key'
   ```

3. **PTERODACTYL_API_KEY** - Your Pterodactyl panel API key
   ```js
   PTERODACTYL_API_KEY: 'ptla_your_api_key_here'
   ```

4. **PTERODACTYL_URL** - Your Pterodactyl panel URL
   ```js
   PTERODACTYL_URL: 'https://panel.yourdomain.com'
   ```

5. **BOT_API_KEY** - Your Discord bot token
   ```js
   BOT_API_KEY: 'your_discord_bot_token'
   ```

6. **DISCORD_REDIRECT_URI** - Update to your domain
   ```js
   DISCORD_REDIRECT_URI: 'https://yourdomain.com/auth/callback'
   ```

### ✅ **Keep These Values (Already Configured):**
- `DISCORD_CLIENT_ID`
- `DISCORD_CLIENT_SECRET` 
- `DISCORD_GUILD_ID`
- `DISCORD_INVITE_LINK`
- `ADMIN_EMAIL`

## 📁 **cPanel Upload Instructions**

1. **Upload all files** to your cPanel public_html directory
2. **Install dependencies** via cPanel Terminal or SSH:
   ```bash
   npm install
   ```
3. **Edit config.js** with your values
4. **Start the application**:
   ```bash
   node app.js
   ```

## 🔑 **Required Services Setup**

### 1. **MongoDB Database**
- Create MongoDB Atlas account
- Create cluster and database
- Get connection string
- Replace `MONGODB_URI` in config.js

### 2. **Pterodactyl Panel**
- Install Pterodactyl panel
- Generate API key from admin panel
- Replace `PTERODACTYL_API_KEY` and `PTERODACTYL_URL`

### 3. **Discord Bot**
- Create Discord application at https://discord.com/developers
- Create bot and get token
- Replace `BOT_API_KEY`
- Invite bot to your Discord server

### 4. **Domain Configuration**
- Update `DISCORD_REDIRECT_URI` to your actual domain
- Configure DNS to point to your cPanel server

## 🚀 **Quick Start Commands**

```bash
# 1. Upload files to cPanel
# 2. SSH into cPanel or use Terminal

# Install dependencies
npm install

# Start application
node app.js

# Or use PM2 for production
npm install -g pm2
pm2 start app.js --name "blazenode-dashboard"
```

## ✅ **Verification Checklist**

- [ ] MongoDB connection working
- [ ] Pterodactyl API responding
- [ ] Discord OAuth2 redirecting correctly
- [ ] Bot joining users to Discord server
- [ ] Admin panel accessible with admin email
- [ ] All pages loading without errors

## 🆘 **Common Issues**

1. **MongoDB Connection Failed**
   - Check connection string format
   - Verify database credentials
   - Ensure IP whitelist includes your server

2. **Discord OAuth2 Not Working**
   - Verify redirect URI matches exactly
   - Check Discord application settings
   - Ensure bot has proper permissions

3. **Pterodactyl API Errors**
   - Verify API key is correct
   - Check panel URL format
   - Ensure API key has admin permissions

## 📞 **Support**

If you need help with deployment, contact the development team or check the main README.md for detailed documentation.