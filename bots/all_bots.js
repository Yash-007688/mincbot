require('dotenv').config();

const BotProperties = require('./botProperties');
const ServerStatus = require('./server_status');

// Debug: Log the server host and port
console.log(`Server Host: ${process.env.SERVER_HOST}`);
console.log(`Server Port: ${process.env.SERVER_PORT}`);

const mineflayer = require('mineflayer');
const fs = require('fs');
const path = require('path');

// --- Required Plugins ---
// Make sure you have installed these packages:
// npm install mineflayer-pathfinder minecraft-data prismarine-world prismarine-physics vec3
// NOTE: '@nxg-xl/mineflayer-util-plugin' seems to be unavailable. Removed from list.
// You might need 'prismarine-physics', and 'prismarine-world' for more advanced behaviors like building.
// 'vec3' is often needed for position handling.
const pathfinder = require('mineflayer-pathfinder').plugin;
const Movements = require('mineflayer-pathfinder').Movements;
const { GoalNear, GoalGetToBlock, GoalFollow, GoalSleep } = require('mineflayer-pathfinder').goals;
const mcData = require('minecraft-data'); // Require minecraft-data here
const Vec3 = require('vec3').Vec3; // Often needed for position handling

// Define the number of bots
const NUM_BOTS = 19;

// Create an array to store all bot instances (Mineflayer bots)
const bots = [];
// Also keep a map or array of BotProperties instances for easy access by name
const botPropertiesInstances = {};

// Create server status instance
const serverStatus = new ServerStatus();

// Start monitoring
serverStatus.startMonitoring();

// Command processing system
class CommandProcessor {
    constructor() {
        this.commands = this.loadCommands();
        this.bots = new Map(); // Store active bots
        this.teams = new Map(); // Store bot teams
        this.savedLocations = new Map(); // Store saved locations
        this.admins = new Set(['CodeDevPro']); // Initialize with CodeDevPro as admin
        this.adminPermissions = new Map();
        this.initializeAdminPermissions();
        this.commandCategories = this.loadCommandCategories();
        this.commandParameters = this.loadCommandParameters();
        this.activeTasks = new Map(); // Track active tasks
        this.taskProgress = new Map(); // Track progress of each task
        this.taskUpdates = new Map(); // Store update history
    }

    initializeAdminPermissions() {
        // Set up default admin permissions
        this.adminPermissions.set('CodeDevPro', {
            level: 'super_admin',
            permissions: [
                'all_commands',
                'manage_admins',
                'manage_bots',
                'manage_teams',
                'teleport_anywhere',
                'override_limits'
            ],
            addedBy: 'system',
            addedAt: Date.now()
        });
    }

    loadCommands() {
        try {
            const commandsPath = path.join(__dirname, '../ai_commands/commands/actions/action_commands.json');
            const commandsData = JSON.parse(fs.readFileSync(commandsPath, 'utf8'));
            return commandsData.commands;
        } catch (error) {
            console.error('Error loading commands:', error);
            return {};
        }
    }

    // Process incoming commands
    async processCommand(commandData) {
        const { type, action, target, params, username } = commandData;
        
        // Check if command requires admin privileges
        const command = this.commands[action];
        if (command?.admin_only && !this.isAdmin(username)) {
            console.error(`User ${username} is not authorized to use admin command: ${action}`);
            return false;
        }

        switch (type) {
            case 'message':
                await this.handleMessage(action, target, params);
                break;
            case 'action':
                await this.handleAction(action, target, params);
                break;
            case 'status':
                await this.handleStatus(action, target, params);
                break;
            case 'team':
                await this.handleTeam(action, target, params);
                break;
            case 'admin':
                await this.handleAdminCommand(action, target, params);
                break;
            default:
                console.error('Unknown command type:', type);
        }
    }

    // Handle message commands
    async handleMessage(action, target, params) {
        if (target === 'all') {
            // Broadcast to all bots
            for (const [botName, bot] of this.bots) {
                await bot.chat(params.message);
            }
        } else {
            // Send to specific bot
            const bot = this.bots.get(target);
            if (bot) {
                await bot.chat(params.message);
            }
        }
    }

    // Handle action commands (mine, build, collect, etc.)
    async handleAction(action, target, params) {
        const bot = this.bots.get(target);
        if (!bot) return;

        switch (action) {
            case 'mine':
                await this.handleMine(bot, params);
                break;
            case 'build':
                await this.handleBuild(bot, params);
                break;
            case 'collect':
                await this.handleCollect(bot, params);
                break;
            case 'teleport':
                await this.handleTeleport(bot, params);
                break;
            case 'goto':
                await this.handleGoto(bot, params);
                break;
            case 'follow_coords':
                await this.handleFollowCoords(bot, params);
                break;
            case 'save_location':
                await this.handleSaveLocation(bot, params);
                break;
            case 'goto_location':
                await this.handleGotoLocation(bot, params);
                break;
            // Add other action handlers...
        }
    }

    // Handle status commands
    async handleStatus(action, target, params) {
        if (target === 'all') {
            for (const [botName, bot] of this.bots) {
                await this.sendBotStatus(bot);
            }
        } else {
            const bot = this.bots.get(target);
            if (bot) {
                await this.sendBotStatus(bot);
            }
        }
    }

    // Handle team commands
    async handleTeam(action, target, params) {
        switch (action) {
            case 'add':
                this.addToTeam(params.botName, params.targetBot);
                break;
            case 'remove':
                this.removeFromTeam(params.botName, params.targetBot);
                break;
            case 'list':
                this.listTeam(params.botName);
                break;
        }
    }

    // Bot creation with enhanced features
    async createBot(botId) {
        const BOT_NAME = `Bot${botId}`;
        
        // Check environment variables
        if (!process.env.SERVER_HOST || !process.env.SERVER_PORT) {
            console.error(`[❌] ${BOT_NAME} Error: SERVER_HOST or SERVER_PORT is not set in .env file.`);
            return;
        }

        // Create bot instance
        const bot = mineflayer.createBot({
            host: process.env.SERVER_HOST,
            port: parseInt(process.env.SERVER_PORT),
            username: BOT_NAME,
            version: '1.20.1',
            hideErrors: false,
        });

        // Load plugins
        bot.loadPlugin(pathfinder);

        // Set up event handlers
        this.setupBotEvents(bot, BOT_NAME);

        // Store bot instance
        this.bots.set(BOT_NAME, bot);

        return bot;
    }

    // Set up bot event handlers
    setupBotEvents(bot, botName) {
        bot.on('error', err => {
            console.error(`[❌] ${botName} Error:`, err.message || err);
            this.handleBotError(bot, err);
        });

        bot.on('end', (reason) => {
            console.log(`[🛑] ${botName} disconnected. Reason: ${reason}`);
            this.handleBotDisconnect(bot, reason);
        });

        // Add more event handlers as needed
    }

    // Helper methods for specific actions
    async handleMine(bot, params) {
        const { block_type } = params;
        // Implement mining logic
        console.log(`[${bot.username}] Mining ${block_type}`);
        // Add actual mining implementation
    }

    async handleBuild(bot, params) {
        const { structure_type } = params;
        // Implement building logic
        console.log(`[${bot.username}] Building ${structure_type}`);
        // Add actual building implementation
    }

    async handleCollect(bot, params) {
        const { item_type } = params;
        // Implement collection logic
        console.log(`[${bot.username}] Collecting ${item_type}`);
        // Add actual collection implementation
    }

    async sendBotStatus(bot) {
        const status = {
            name: bot.username,
            health: bot.health,
            food: bot.food,
            position: bot.entity.position,
            inventory: bot.inventory.items(),
            equipment: bot.inventory.armor
        };
        console.log(`[${bot.username}] Status:`, status);
        return status;
    }

    // Team management methods
    addToTeam(botName, targetBot) {
        if (!this.teams.has(botName)) {
            this.teams.set(botName, new Set());
        }
        this.teams.get(botName).add(targetBot);
        console.log(`[${botName}] Added ${targetBot} to team`);
    }

    removeFromTeam(botName, targetBot) {
        if (this.teams.has(botName)) {
            this.teams.get(botName).delete(targetBot);
            console.log(`[${botName}] Removed ${targetBot} from team`);
        }
    }

    listTeam(botName) {
        if (this.teams.has(botName)) {
            const team = Array.from(this.teams.get(botName));
            console.log(`[${botName}] Team members:`, team);
            return team;
        }
        return [];
    }

    // Add these new methods to handle coordinate commands

    async handleTeleport(bot, params) {
        const { x, y, z } = params;
        try {
            await bot.entity.position.set(x, y, z);
            console.log(`[${bot.username}] Teleported to (${x}, ${y}, ${z})`);
            return true;
        } catch (error) {
            console.error(`[${bot.username}] Teleport failed:`, error);
            return false;
        }
    }

    async handleGoto(bot, params) {
        const { x, y, z } = params;
        try {
            const goal = new pathfinder.goals.GoalBlock(x, y, z);
            await bot.pathfinder.setGoal(goal);
            console.log(`[${bot.username}] Moving to (${x}, ${y}, ${z})`);
            return true;
        } catch (error) {
            console.error(`[${bot.username}] Goto failed:`, error);
            return false;
        }
    }

    async handleFollowCoords(bot, params) {
        const { coordinates } = params;
        try {
            for (const [x, y, z] of coordinates) {
                const goal = new pathfinder.goals.GoalBlock(x, y, z);
                await bot.pathfinder.setGoal(goal);
                // Wait until bot reaches the point
                await this.waitForGoal(bot);
                console.log(`[${bot.username}] Reached point (${x}, ${y}, ${z})`);
            }
            return true;
        } catch (error) {
            console.error(`[${bot.username}] Follow coordinates failed:`, error);
            return false;
        }
    }

    async handleSaveLocation(bot, params) {
        const { location_name } = params;
        const position = bot.entity.position;
        this.savedLocations.set(location_name, {
            x: position.x,
            y: position.y,
            z: position.z,
            savedBy: bot.username,
            timestamp: Date.now()
        });
        console.log(`[${bot.username}] Saved location '${location_name}' at (${position.x}, ${position.y}, ${position.z})`);
        return true;
    }

    async handleGotoLocation(bot, params) {
        const { location_name } = params;
        const location = this.savedLocations.get(location_name);
        if (!location) {
            console.error(`[${bot.username}] Location '${location_name}' not found`);
            return false;
        }
        return await this.handleGoto(bot, location);
    }

    // Helper method to wait for bot to reach goal
    async waitForGoal(bot, timeout = 30000) {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();
            const checkInterval = setInterval(() => {
                if (!bot.pathfinder.isMoving()) {
                    clearInterval(checkInterval);
                    resolve(true);
                } else if (Date.now() - startTime > timeout) {
                    clearInterval(checkInterval);
                    reject(new Error('Timeout waiting for goal'));
                }
            }, 1000);
        });
    }

    // Add method to get saved locations
    getSavedLocations() {
        return Array.from(this.savedLocations.entries()).map(([name, data]) => ({
            name,
            ...data
        }));
    }

    // Admin command handlers
    async handleAdminCommand(action, target, params) {
        const { command, admin_name } = params;
        
        switch (command) {
            case 'list':
                return this.listAdmins();
            case 'add':
                return this.addAdmin(admin_name);
            case 'remove':
                return this.removeAdmin(admin_name);
            case 'permissions':
                return this.getAdminPermissions(admin_name);
            case 'status':
                return this.getAdminStatus(admin_name);
            default:
                console.error('Unknown admin command:', command);
                return false;
        }
    }

    // Admin management methods
    listAdmins() {
        const adminList = Array.from(this.admins).map(admin => ({
            name: admin,
            permissions: this.adminPermissions.get(admin)
        }));
        console.log('Current Admins:', adminList);
        return adminList;
    }

    addAdmin(adminName) {
        if (this.admins.has(adminName)) {
            console.log(`Admin ${adminName} already exists`);
            return false;
        }
        this.admins.add(adminName);
        this.adminPermissions.set(adminName, {
            level: 'admin',
            permissions: [
                'basic_commands',
                'manage_bots',
                'manage_teams'
            ],
            addedBy: 'CodeDevPro',
            addedAt: Date.now()
        });
        console.log(`Added new admin: ${adminName}`);
        return true;
    }

    removeAdmin(adminName) {
        if (adminName === 'CodeDevPro') {
            console.log('Cannot remove super admin CodeDevPro');
            return false;
        }
        this.admins.delete(adminName);
        this.adminPermissions.delete(adminName);
        console.log(`Removed admin: ${adminName}`);
        return true;
    }

    getAdminPermissions(adminName) {
        const permissions = this.adminPermissions.get(adminName);
        if (!permissions) {
            console.log(`No permissions found for ${adminName}`);
            return null;
        }
        console.log(`Permissions for ${adminName}:`, permissions);
        return permissions;
    }

    getAdminStatus(adminName) {
        const isAdmin = this.admins.has(adminName);
        const permissions = this.adminPermissions.get(adminName);
        const status = {
            isAdmin,
            permissions,
            level: permissions?.level || 'user'
        };
        console.log(`Status for ${adminName}:`, status);
        return status;
    }

    // Check if user is admin
    isAdmin(username) {
        return this.admins.has(username);
    }

    // Check if user has specific permission
    hasPermission(username, permission) {
        const userPermissions = this.adminPermissions.get(username);
        if (!userPermissions) return false;
        
        if (userPermissions.permissions.includes('all_commands')) return true;
        return userPermissions.permissions.includes(permission);
    }

    // Process natural language commands
    async processNaturalCommand(command, username) {
        console.log(`Processing natural command: "${command}" from ${username}`);
        
        // Parse the command
        const parsedCommand = this.parseNaturalCommand(command);
        
        // Generate detailed analysis
        const analysis = await this.analyzeCommand(parsedCommand);
        
        // Create task ID
        const taskId = this.generateTaskId();
        
        // Initialize task tracking
        this.initializeTaskTracking(taskId, parsedCommand, analysis);
        
        // Send detailed response
        await this.sendCommandAnalysis(analysis, taskId);
        
        // Execute the command with progress tracking
        return await this.executeWithProgressTracking(parsedCommand, username, taskId);
    }

    parseNaturalCommand(command) {
        const commandLower = command.toLowerCase();
        
        // Extract bot name(s)
        const botNames = this.extractBotNames(commandLower);
        
        // Extract action
        const action = this.extractAction(commandLower);
        
        // Extract parameters
        const parameters = this.extractParameters(commandLower);
        
        // Extract location if present
        const location = this.extractLocation(commandLower);
        
        return {
            bots: botNames,
            action: action,
            parameters: parameters,
            location: location,
            originalCommand: command
        };
    }

    extractBotNames(command) {
        const botRegex = /(?:bot|bots?)\s*(\d+)/gi;
        const matches = [...command.matchAll(botRegex)];
        
        if (command.includes('all bots')) {
            return Array.from(this.bots.keys());
        }
        
        return matches.map(match => `Bot${match[1]}`);
    }

    extractAction(command) {
        for (const [category, actions] of Object.entries(this.commandCategories)) {
            for (const action of actions) {
                if (command.includes(action)) {
                    return {
                        type: category,
                        action: action
                    };
                }
            }
        }
        return null;
    }

    extractParameters(command) {
        const parameters = {};
        
        // Extract items
        for (const item of this.commandParameters.items) {
            if (command.includes(item)) {
                parameters.item = item;
            }
        }
        
        // Extract quantities
        for (const quantity of this.commandParameters.quantities) {
            if (command.includes(quantity)) {
                parameters.quantity = quantity;
            }
        }
        
        return parameters;
    }

    extractLocation(command) {
        for (const location of this.commandParameters.locations) {
            if (command.includes(location)) {
                return location;
            }
        }
        return null;
    }

    async executeWithProgressTracking(parsedCommand, username, taskId) {
        const taskInfo = this.activeTasks.get(taskId);
        
        try {
            // Start progress tracking
            this.startProgressTracking(taskId);
            
            // Execute the command
            const result = await this.executeParsedCommand(parsedCommand, username);
            
            // Update final status
            this.updateTaskStatus(taskId, 'completed', 100);
            
            return result;
        } catch (error) {
            this.updateTaskStatus(taskId, 'failed', this.taskProgress.get(taskId).overall);
            throw error;
        }
    }

    startProgressTracking(taskId) {
        const taskInfo = this.activeTasks.get(taskId);
        const progressInterval = setInterval(() => {
            this.updateProgress(taskId);
        }, 1000); // Update every second

        taskInfo.progressInterval = progressInterval;
    }

    async updateProgress(taskId) {
        const taskInfo = this.activeTasks.get(taskId);
        const progress = this.taskProgress.get(taskId);
        
        // Update bot progress
        for (const bot of taskInfo.bots) {
            const botProgress = await this.getBotProgress(bot, taskInfo);
            progress.bots.set(bot, botProgress);
        }

        // Update resource progress
        const resourceProgress = await this.getResourceProgress(taskInfo);
        progress.resources = resourceProgress;

        // Update coordinate progress
        const coordinateProgress = await this.getCoordinateProgress(taskInfo);
        progress.coordinates = coordinateProgress;

        // Calculate overall progress
        progress.overall = this.calculateOverallProgress(progress);

        // Update current step
        if (progress.overall >= (taskInfo.currentStep + 1) * (100 / taskInfo.totalSteps)) {
            taskInfo.currentStep++;
        }

        // Store update
        this.storeProgressUpdate(taskId, progress);

        // Send progress update
        await this.sendProgressUpdate(taskId);
    }

    async getBotProgress(bot, taskInfo) {
        // Get real-time bot status
        const botInstance = this.bots.get(bot);
        if (!botInstance) return 0;

        const botStatus = await botInstance.getStatus();
        return this.calculateBotProgress(botStatus, taskInfo);
    }

    async getResourceProgress(taskInfo) {
        const progress = new Map();
        
        // Calculate progress for each required resource
        for (const [resource, required] of taskInfo.analysis.execution_plan.required_resources.materials) {
            const current = await this.getCurrentResourceCount(resource);
            const percentage = (current / required) * 100;
            progress.set(resource, Math.min(percentage, 100));
        }

        return progress;
    }

    async getCoordinateProgress(taskInfo) {
        const progress = new Map();
        
        if (taskInfo.location) {
            const currentLocation = await this.getCurrentLocation(taskInfo.bots[0]);
            const targetLocation = taskInfo.analysis.execution_plan.coordinate_plan.target_location;
            const distance = this.calculateDistance(currentLocation, targetLocation);
            const totalDistance = taskInfo.analysis.execution_plan.coordinate_plan.distance;
            const percentage = ((totalDistance - distance) / totalDistance) * 100;
            progress.set('travel', Math.min(percentage, 100));
        }

        return progress;
    }

    calculateOverallProgress(progress) {
        const weights = {
            bots: 0.4,
            resources: 0.3,
            coordinates: 0.3
        };

        let overall = 0;
        
        // Calculate bot progress
        const botProgress = Array.from(progress.bots.values()).reduce((a, b) => a + b, 0) / progress.bots.size;
        overall += botProgress * weights.bots;

        // Calculate resource progress
        const resourceProgress = Array.from(progress.resources.values()).reduce((a, b) => a + b, 0) / progress.resources.size;
        overall += resourceProgress * weights.resources;

        // Calculate coordinate progress
        const coordinateProgress = Array.from(progress.coordinates.values()).reduce((a, b) => a + b, 0) / progress.coordinates.size;
        overall += coordinateProgress * weights.coordinates;

        return Math.min(overall, 100);
    }

    storeProgressUpdate(taskId, progress) {
        const update = {
            timestamp: Date.now(),
            progress: progress.overall,
            botProgress: Object.fromEntries(progress.bots),
            resourceProgress: Object.fromEntries(progress.resources),
            coordinateProgress: Object.fromEntries(progress.coordinates)
        };

        this.taskUpdates.get(taskId).push(update);
    }

    async sendProgressUpdate(taskId) {
        const taskInfo = this.activeTasks.get(taskId);
        const progress = this.taskProgress.get(taskId);
        
        const update = {
            taskId: taskId,
            command: taskInfo.command,
            status: taskInfo.status,
            progress: {
                overall: progress.overall,
                currentStep: taskInfo.currentStep,
                totalSteps: taskInfo.totalSteps,
                stepDescription: taskInfo.analysis.step_by_step_plan[taskInfo.currentStep],
                bots: Object.fromEntries(progress.bots),
                resources: Object.fromEntries(progress.resources),
                coordinates: Object.fromEntries(progress.coordinates)
            },
            timeElapsed: (Date.now() - taskInfo.startTime) / 1000,
            estimatedTimeRemaining: this.calculateTimeRemaining(taskInfo, progress)
        };

        // Send update to Discord or other platforms
        console.log(this.formatProgressUpdate(update));
    }

    formatProgressUpdate(update) {
        return `
🔄 Task Progress Update: ${update.taskId}

📋 Command: "${update.command}"
⏱️ Time Elapsed: ${Math.round(update.timeElapsed)}s
⏳ Estimated Time Remaining: ${Math.round(update.estimatedTimeRemaining)}s

📊 Overall Progress: ${Math.round(update.progress.overall)}%

👥 Bot Progress:
${Object.entries(update.progress.bots).map(([bot, progress]) => 
    `${bot}: ${Math.round(progress)}%`
).join('\n')}

📦 Resource Progress:
${Object.entries(update.progress.resources).map(([resource, progress]) => 
    `${resource}: ${Math.round(progress)}%`
).join('\n')}

🗺️ Coordinate Progress:
${Object.entries(update.progress.coordinates).map(([type, progress]) => 
    `${type}: ${Math.round(progress)}%`
).join('\n')}

📝 Current Step: ${update.progress.currentStep + 1}/${update.progress.totalSteps}
${update.progress.stepDescription}
`;
    }

    calculateTimeRemaining(taskInfo, progress) {
        const elapsedTime = (Date.now() - taskInfo.startTime) / 1000;
        const estimatedTotalTime = taskInfo.analysis.execution_plan.estimated_time * 60;
        const remainingPercentage = 100 - progress.overall;
        return (elapsedTime / progress.overall) * remainingPercentage;
    }

    updateTaskStatus(taskId, status, progress) {
        const taskInfo = this.activeTasks.get(taskId);
        taskInfo.status = status;
        this.taskProgress.get(taskId).overall = progress;
        
        // Clear progress tracking interval
        if (taskInfo.progressInterval) {
            clearInterval(taskInfo.progressInterval);
        }
        
        // Send final update
        this.sendProgressUpdate(taskId);
    }

    generateTaskId() {
        return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    initializeTaskTracking(taskId, parsedCommand, analysis) {
        const taskInfo = {
            command: parsedCommand.originalCommand,
            startTime: Date.now(),
            bots: parsedCommand.bots,
            action: parsedCommand.action,
            parameters: parsedCommand.parameters,
            location: parsedCommand.location,
            analysis: analysis,
            status: 'initialized',
            progress: 0,
            currentStep: 0,
            totalSteps: analysis.step_by_step_plan.length,
            botProgress: new Map(),
            resourceProgress: new Map(),
            coordinateProgress: new Map(),
            lastUpdate: Date.now()
        };

        this.activeTasks.set(taskId, taskInfo);
        this.taskProgress.set(taskId, {
            overall: 0,
            steps: new Array(analysis.step_by_step_plan.length).fill(0),
            bots: new Map(parsedCommand.bots.map(bot => [bot, 0])),
            resources: new Map(),
            coordinates: new Map()
        });
        this.taskUpdates.set(taskId, []);
    }
}

// Create command processor instance
const commandProcessor = new CommandProcessor();

// Export for use in other files
module.exports = commandProcessor;

// Function to create a bot with retry logic
async function createBot(botId) {
  const BOT_NAME = `Bot${botId}`; // Simplified username format
  let updateInterval = null; // Variable to hold the update interval ID

  // Wait for server to be ready
  const isReady = await serverStatus.isServerReady();
  if (!isReady) {
    console.error('[❌] Cannot create bot - Server is not ready');
    return;
  }

  // Check if environment variables are set
  if (!process.env.SERVER_HOST || !process.env.SERVER_PORT) {
    console.error(`[❌] ${BOT_NAME} Error: SERVER_HOST or SERVER_PORT is not set in .env file.`);
    return;
  }

  let bot = mineflayer.createBot({
    host: process.env.SERVER_HOST,
    port: parseInt(process.env.SERVER_PORT),
    username: BOT_NAME,
    version: '1.20.1', // Specify Minecraft version (ensure this matches your server)
    // protocolVersion: 763, // This might be inferred from version
    hideErrors: false, // Set to true to hide some errors for easier debugging
  });

  // --- Load Plugins ---
  bot.loadPlugin(pathfinder);
  // Load other plugins here if needed, e.g.:
  // bot.loadPlugin(require('mineflayer-pvp').plugin)
  // bot.loadPlugin(require('mineflayer-collectblock').plugin)


  function reconnect() {
    console.log(`[🔄] Reconnecting ${BOT_NAME} in 10 seconds...`);
    // Clear the update interval before reconnecting
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }

    setTimeout(() => {
      createBot(botId);
    }, 10000);

    // Remove old bot from array and properties map
    const idx = bots.indexOf(bot);
    if (idx !== -1) bots.splice(idx, 1);
    if (bot && bot.username && botPropertiesInstances[bot.username]) {
        delete botPropertiesInstances[bot.username];
    }

    // Important: Remove bot listeners to prevent memory leaks on reconnect
    if (bot) {
        bot.removeAllListeners();
    }

    bot = null;
  }

  bot.on('login', () => {
    console.log(`[✅] ${BOT_NAME} logged in.`);
    bot.chat(`⚔️ ${BOT_NAME} reporting for duty!`);

    // Initialize BotProperties after login
    // Find the team members (other bots) from the 'bots' array
    const teamMembers = bots
        .filter(b => b !== bot && b.botProps) // Filter out self and bots without botProps yet
        .map(b => b.botProps); // Get their BotProperties instances

    const botProps = new BotProperties(BOT_NAME, teamMembers, bot);
    bot.botProps = botProps; // Attach BotProperties instance to mineflayer bot
    botPropertiesInstances[BOT_NAME] = botProps; // Store in map for easy lookup

    // Update team lists for all existing bots to include the new bot
    bots.forEach(existingBot => {
        if (existingBot.botProps && existingBot !== bot) {
             // Add the new bot's BotProperties instance to the existing bot's team if not already there
            if (!existingBot.botProps.team.find(member => member.name === BOT_NAME)) {
                existingBot.botProps.team.push(botProps);
            }
        }
    });

    // Set default movements for pathfinder
    try {
        const data = mcData(bot.version);
        const defaultMove = new Movements(bot, data);
         // You might want to set different speeds for different movement types
         defaultMove.canDig = true; // Allow digging for pathfinding
        // defaultMove.canOpenDoors = true; // Example
        // defaultMove.canOpenChests = true; // Example
        // defaultMove.canBreakDoors = true; // Example
        // defaultMove.allowParkour = true; // Example
        bot.pathfinder.setMovements(defaultMove);
         console.log(`[✅] ${BOT_NAME} Pathfinder movements set.`);
    } catch (e) {
        console.error(`[❌] ${BOT_NAME} Error setting pathfinder movements:`, e.message);
        console.warn(`[⚠️] Please ensure 'minecraft-data' is installed and matches bot version.`);
    }

    // --- Add event listeners for autonomous behaviors ---

    // Listen for collected items to announce findings
    bot.on('collect', (collector, entity) => {
        // Check if the collector is this bot and the entity is an item
        if (collector === bot && entity.type === 'item') {
             if (bot.botProps) {
                 bot.botProps.handleItemCollected(entity);
             }
        }
    });

    // Listen for changes in inventory to potentially trigger crafting/using items
    // bot.inventory.on('updateSlot', (slot, oldItem, newItem) => {
    //     if (bot.botProps) {
    //          // Example: Check for new food items or crafting materials
    //     }
    // });

    // --- Start the autonomous update loop ---
    // Call the update method periodically (e.g., every 500ms)
    // Adjust interval based on how frequently you need bots to react
    updateInterval = setInterval(() => {
        if (bot.botProps) {
            // Use a try-catch block to prevent errors in update() from crashing the bot
            try {
                bot.botProps.update();
            } catch (e) {
                console.error(`[❌] ${BOT_NAME} Error in update loop:`, e.message);
            }
        }
    }, 500); // 500ms = 0.5 seconds

    // Optional: Add event listeners for things that should trigger immediate action
    // For example, reacting to being attacked:
    // bot.on('entityHurt', (entity) => {
    //     if (entity === bot.entity) { // If the bot itself is hurt
    //         console.log(`${BOT_NAME} is hurt! Health: ${bot.health}`);
                // Trigger immediate healing logic if needed
    //     } else if (bot.botProps.team.some(member => member.mineflayerBot?.entity === entity)) {
    //         console.log(`${BOT_NAME} sees team member ${entity.username || entity.type} is hurt!`);
                // Trigger immediate help logic
    //     }
    // });
  });

  bot.on('error', err => {
    console.error(`[❌] ${BOT_NAME} Error:`, err.message || err);
    // Clear the update interval on error
     if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
    reconnect();
  });

  bot.on('end', (reason) => {
    console.log(`[🛑] ${BOT_NAME} disconnected. Reason: ${reason}`);
    // Clear the update interval on disconnect
     if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
    reconnect();
  });

   // Add the mineflayer bot to the array immediately
  bots.push(bot);


  // Command fetcher for this bot
  // This interval runs for each bot instance
  // Consider a centralized command processing system for better performance and control
  setInterval(() => {
    try {
        // Read the command file from the new location
        if (!bot || !bot.botProps || !bot.entity) return;

        const command = fs.readFileSync('./ai_commands/input/command_queue.txt', 'utf8').trim();
        if (!command) return;

        // Example: prefix specific commands to this bot
        // Check if the command is targeted at this specific bot or ALL bots
        if (command.startsWith(`${BOT_NAME}:`) || command.startsWith("ALL:")) {
          const actualCommand = command.replace(`${BOT_NAME}:`, '').replace('ALL:', '').trim();
          console.log(`[${BOT_NAME}] Processing command: ${actualCommand}`);
          // You might want more sophisticated command parsing here

          // Example command handling: tp
          if (actualCommand.startsWith('tp ')) {
            const parts = actualCommand.split(' ');
            const targetIdentifier = parts[1]; // Can be a bot name or coordinates

            if (targetIdentifier) {
                // Check if the target is a bot name
                const targetBotProps = botPropertiesInstances[targetIdentifier];
                if (targetBotProps) {
                    console.log(`[${BOT_NAME}] Attempting to teleport to bot: ${targetIdentifier}`);
                    bot.botProps.tp(targetBotProps); // Use the BotProperties tp method
                } else {
                    // Attempt to parse as coordinates (x y z)
                    const coords = actualCommand.substring(3).trim().split(' ').map(Number);
                    if (coords.length === 3 && coords.every(Number.isFinite)) {
                        const targetPos = { x: coords[0], y: coords[1], z: coords[2] };
                        console.log(`[${BOT_NAME}] Attempting to teleport to coordinates: (${targetPos.x}, ${targetPos.y}, ${targetPos.z})`);
                        bot.botProps.tp(targetPos); // Use the BotProperties tp method
                    } else {
                        bot.chat(`Invalid tp target: ${targetIdentifier}. Use bot name or x y z coordinates.`);
                        console.log(`[${BOT_NAME}] Invalid tp target format: ${actualCommand}`);
                    }
                }
            } else {
                 bot.chat('tp command requires a target (bot name or coordinates).');
                 console.log(`[${BOT_NAME}] tp command missing target.`);
            }
             // Clear command after processing by this bot/ALL bots
             // NOTE: This clears the command for ALL bots if any bot processes it.
             // A centralized command system would be better.
             fs.writeFileSync('./ai_commands/input/command_queue.txt', '');

          }
           // Example command handling: chat
           else if (actualCommand.startsWith('chat ')) {
               const message = actualCommand.substring(5).trim();
               if (message) {
                   bot.botProps.chat(message); // Use the BotProperties chat method
               } else {
                   console.log(`[${BOT_NAME}] Chat command requires a message.`);
               }
                // Clear command after processing
                fs.writeFileSync('./ai_commands/input/command_queue.txt', '');
           }
           // Example command handling: status
           else if (actualCommand === 'status') {
               bot.botProps.status(); // Use the BotProperties status method
                // Don't clear command, let other bots report status too
           }
           // Example command handling: follow <botName>
           else if (actualCommand.startsWith('follow ')) {
                const targetName = actualCommand.substring(7).trim();
                const targetBotProps = botPropertiesInstances[targetName];
                if (targetBotProps) {
                    bot.botProps.setTargetBotToFollow(targetBotProps);
                } else {
                    bot.chat(`Could not find bot '${targetName}' to follow.`);
                }
                 fs.writeFileSync('./ai_commands/input/command_queue.txt', '');
                 fs.writeFileSync('gpt-input.txt', '');
           }
            // Example command handling: unfollow
           else if (actualCommand === 'unfollow') {
                bot.botProps.clearTargetBotToFollow();
                 fs.writeFileSync('gpt-input.txt', '');
           }
           // Add other command handlers here...
        }
    } catch (err) {
        // Ignore error if file doesn't exist yet
        if (err.code !== 'ENOENT') {
            console.error(`[❌] ${BOT_NAME} Error reading gpt-input.txt:`, err.message);
        }
    }
  }, 1000); // Check for commands every 1 second
}

// Create all bots with a delay between each spawn
console.log(`Initializing ${NUM_BOTS} bots with a delay...`);
for (let i = 1; i <= NUM_BOTS; i++) {
  setTimeout(() => {
    createBot(i);
  }, i * 10000); // 10000ms (10 seconds) delay between each bot spawn
}

console.log(`All bots will attempt to connect.`);