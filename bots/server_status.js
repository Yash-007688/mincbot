const mineflayer = require('mineflayer');
const ping = require('minecraft-server-util');

class ServerStatus {
    constructor() {
        this.serverHost = process.env.SERVER_HOST;
        this.serverPort = parseInt(process.env.SERVER_PORT);
        this.isOnline = false;
        this.lastCheck = null;
        this.errorCount = 0;
        this.maxRetries = 3;
        this.checkInterval = 60000; // Check every minute
    }

    async checkServerStatus() {
        try {
            // Check if server is online using minecraft-server-util
            const result = await ping.status(this.serverHost, this.serverPort);
            
            if (result) {
                this.isOnline = true;
                this.errorCount = 0;
                this.lastCheck = new Date();
                console.log(`[✅] Server is online! Players: ${result.players.online}/${result.players.max}`);
                return true;
            }
        } catch (error) {
            this.handleError(error);
            return false;
        }
    }

    handleError(error) {
        this.errorCount++;
        this.isOnline = false;
        
        const errorMessage = this.getErrorMessage(error);
        console.error(`[❌] Server Error: ${errorMessage}`);
        
        if (this.errorCount >= this.maxRetries) {
            console.error('[⚠️] Maximum retry attempts reached. Server might be down.');
            // Here you can add additional error handling like:
            // - Sending notifications
            // - Attempting to restart the server
            // - Logging to a file
        }
    }

    getErrorMessage(error) {
        if (error.code === 'ECONNREFUSED') {
            return 'Connection refused - Server might be offline';
        } else if (error.code === 'ETIMEDOUT') {
            return 'Connection timed out - Server might be overloaded';
        } else if (error.code === 'ENOTFOUND') {
            return 'Server host not found - Check your server address';
        } else {
            return error.message || 'Unknown error occurred';
        }
    }

    async startMonitoring() {
        console.log(`[🔍] Starting server monitoring for ${this.serverHost}:${this.serverPort}`);
        
        // Initial check
        await this.checkServerStatus();
        
        // Set up periodic checking
        setInterval(async () => {
            await this.checkServerStatus();
        }, this.checkInterval);
    }

    // Method to check if server is ready for bot connection
    async isServerReady() {
        if (!this.isOnline) {
            await this.checkServerStatus();
        }
        return this.isOnline;
    }

    // Method to get server status information
    getStatusInfo() {
        return {
            isOnline: this.isOnline,
            lastCheck: this.lastCheck,
            errorCount: this.errorCount,
            serverHost: this.serverHost,
            serverPort: this.serverPort
        };
    }
}

module.exports = ServerStatus;
