#!/usr/bin/env node

const mineflayer = require('mineflayer');

// Set environment variables for mcfleet server
process.env.SERVER_HOST = 'play.mcfleet.net';
process.env.SERVER_PORT = '25565';

console.log(`Connecting to server: ${process.env.SERVER_HOST}:${process.env.SERVER_PORT}`);
console.log('Bot configuration:', {
    host: process.env.SERVER_HOST,
    port: parseInt(process.env.SERVER_PORT),
    username: 'Ro9ieFinder',
    version: '1.20.1'
});

const bot = mineflayer.createBot({
    host: process.env.SERVER_HOST,
    port: parseInt(process.env.SERVER_PORT),
    username: 'Ro9ieFinder',
    version: '1.20.1',
    hideErrors: false
});

bot.on('login', () => {
    console.log('✅ Bot logged in successfully!');
    console.log(`Bot name: ${bot.username}`);
    console.log(`Server: ${bot.game.levelType}`);
    
    // Look for Ro9ie in the player list
    setTimeout(() => {
        console.log('\n🔍 Looking for player Ro9ie...');
        console.log('Online players:', Object.keys(bot.players));
        
        if (bot.players['Ro9ie']) {
            console.log('✅ Found Ro9ie!');
            const ro9ie = bot.players['Ro9ie'];
            console.log('Ro9ie info:', {
                username: ro9ie.username,
                ping: ro9ie.ping,
                entity: ro9ie.entity ? 'Has entity' : 'No entity',
                position: ro9ie.entity ? ro9ie.entity.position : 'Unknown'
            });
            
            if (ro9ie.entity) {
                console.log(`Ro9ie position: ${ro9ie.entity.position.x}, ${ro9ie.entity.position.y}, ${ro9ie.entity.position.z}`);
                console.log('🎯 Moving towards Ro9ie...');
                bot.chat('Hey Ro9ie! I found you!');
            }
        } else {
            console.log('❌ Ro9ie not found online');
            console.log('Available players:', Object.keys(bot.players).filter(name => name !== bot.username));
        }
    }, 3000);
});

bot.on('playerJoined', (player) => {
    console.log(`👋 Player joined: ${player.username}`);
    if (player.username === 'Ro9ie') {
        console.log('🎉 Ro9ie just joined the server!');
        bot.chat('Hey Ro9ie! Welcome back!');
    }
});

bot.on('playerLeft', (player) => {
    console.log(`👋 Player left: ${player.username}`);
    if (player.username === 'Ro9ie') {
        console.log('😢 Ro9ie left the server');
    }
});

bot.on('chat', (username, message) => {
    if (username === 'Ro9ie') {
        console.log(`💬 Ro9ie said: ${message}`);
        bot.chat(`Hi Ro9ie! I heard you say: ${message}`);
    }
});

bot.on('spawn', () => {
    console.log('🎮 Bot spawned in the world!');
});

bot.on('error', (err) => {
    console.error('❌ Bot error:', err);
    console.error('Error details:', err.stack);
});

bot.on('end', (reason) => {
    console.log(`🛑 Bot disconnected: ${reason}`);
});

bot.on('kicked', (reason) => {
    console.log(`🚫 Bot was kicked: ${reason}`);
});

// Add connection timeout
setTimeout(() => {
    if (!bot.entity) {
        console.log('⏰ Connection timeout - bot did not spawn within 30 seconds');
        bot.quit();
    }
}, 30000);

// Keep the bot running
process.on('SIGINT', () => {
    console.log('\n👋 Shutting down bot...');
    bot.quit();
    process.exit(0);
});

console.log('🤖 Bot starting...');