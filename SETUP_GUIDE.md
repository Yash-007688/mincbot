# Minecraft PvP Bot Setup Guide

## Quick Setup

1. **Edit the configuration file:**
   ```bash
   nano /workspace/.env
   ```

2. **Update these settings with your server details:**
   ```
   # Your Minecraft server details
   HOST=your_server_ip_or_domain
   PORT=25565
   VERSION=1.20.4
   
   # Your bot username prefix
   BASE_NAME=YourID_
   
   # Authentication (if using premium account)
   AUTH_MODE=offline
   EMAIL=your_email@example.com
   PASSWORD=your_password
   ```

3. **Run the bot:**
   ```bash
   cd /workspace/bots
   npm start
   ```

## Configuration Options

### Server Settings
- `HOST`: Your Minecraft server IP address or domain name
- `PORT`: Server port (usually 25565)
- `VERSION`: Minecraft protocol version (e.g., 1.20.4)

### Bot Settings
- `BOT_COUNT`: Number of bots to spawn (default: 20)
- `BASE_NAME`: Username prefix for bots (e.g., "YourID_" creates "YourID_0", "YourID_1", etc.)
- `ATTACK_RANGE`: How far bots will target players (default: 16 blocks)
- `EXCLUDE_NAMES`: Comma-separated list of players to never attack

### Authentication
- `AUTH_MODE`: 
  - `offline` - For cracked servers or offline mode
  - `microsoft` - For Microsoft account authentication
  - `mojang` - For legacy Mojang account authentication
- `EMAIL`: Your Minecraft account email
- `PASSWORD`: Your Minecraft account password

## What the Bot Does

1. **Spawns 20 bots** with usernames like "YourID_0", "YourID_1", etc.
2. **Automatically targets** the nearest player within attack range
3. **Attacks players** using PvP mechanics
4. **Logs kills** with player names and coordinates when they die

## Example Output
```
[PvP] [YourID_0] Logged in.
[PvP] [YourID_0] Spawned and ready.
[PvP] [YourID_0] Targeting PlayerName at (100, 64, 200)
[PvP] [YourID_0] Eliminated PlayerName at (100, 64, 200)
```

## Troubleshooting

- **Connection refused**: Check your server IP and port
- **Authentication failed**: Verify your email/password for premium accounts
- **Bots not attacking**: Check if players are within ATTACK_RANGE
- **Server kicks bots**: Some servers have anti-bot protection

## Important Notes

- Make sure your server allows multiple connections
- Some servers may have anti-bot measures
- Use responsibly and follow server rules
- The bot uses offline mode by default (no authentication required)