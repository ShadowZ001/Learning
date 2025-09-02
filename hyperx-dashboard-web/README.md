# HyperX Dashboard

Web dashboard for HyperX hosting platform with Discord authentication.

## Features
- Discord OAuth login
- Wallet system with transactions
- Server management
- Resource store
- Mobile responsive design

## Setup
1. Copy `.env.example` to `.env`
2. Fill in Discord app credentials
3. Run `npm install`
4. Run `npm start`

## Hosting
- **Netlify**: Static hosting (frontend only)
- **Railway/Heroku**: Full hosting (with backend)

## Environment Variables
- `DISCORD_CLIENT_ID`: Discord app client ID
- `DISCORD_CLIENT_SECRET`: Discord app client secret
- `DISCORD_REDIRECT_URI`: OAuth redirect URL
- `SESSION_SECRET`: Session encryption key
- `PORT`: Server port (default: 4000)