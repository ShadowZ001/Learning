# BlazeNode Panel Bot

Discord bot for automated Pterodactyl server creation.

## Features
- `/server create [nest] [egg]` - Creates a new server with 3GB RAM, 100% CPU, 5GB disk
- One server per user limit
- Automatic account creation with username@gmail.com
- Credentials sent via DM

## Setup
1. `npm install`
2. Configure `.env` file
3. `npm start`

## Requirements
- Node.js 16+
- MongoDB
- Pterodactyl Panel API access