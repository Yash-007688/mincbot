#!/usr/bin/env node

const mineflayer = require('mineflayer');

console.log('🤖 Starting bot connection test...');

const bot = mineflayer.createBot({
    host: 'play.mcfleet.net',
    port: 25565,
    username: 'TestBot',
    version: '1.20.1',
    hideErrors: false
});

console.log('📡 Attempting to connect to play.mcfleet.net:25565...');

bot.on('login', () => {
    console.log('✅ Successfully logged in!');
    console.log('Bot username:', bot.username);
    console.log('Server version:', bot.game.version);
    console.log('Level type:', bot.game.levelType);
    
    // Look for Ro9ie
    setTimeout(() => {
        console.log('\n🔍 Checking for player Ro9ie...');
        console.log('All players:', Object.keys(bot.players));
        
        if (bot.players['Ro9ie']) {
            console.log('🎉 Found Ro9ie!');
            const ro9ie = bot.players['Ro9ie'];
            console.log('Ro9ie details:', {
                username: ro9ie.username,
                ping: ro9ie.ping,
                hasEntity: !!ro9ie.entity,
                position: ro9ie.entity ? ro9ie.entity.position : 'Not available'
            });
        } else {
            console.log('❌ Ro9ie not found in current players');
            console.log('Available players:', Object.keys(bot.players).filter(name => name !== 'TestBot'));
        }
        
        // Try to navigate to survival-2 if it's a server command
        console.log('\n🎮 Trying to navigate to survival-2...');
        bot.chat('/server survival-2');
        
    }, 5000);
});

bot.on('spawn', () => {
    console.log('🎮 Bot spawned in the world!');
});

bot.on('chat', (username, message) => {
    console.log(`💬 ${username}: ${message}`);
    if (username === 'Ro9ie') {
        console.log('🎯 Ro9ie is talking!');
    }
});

bot.on('playerJoined', (player) => {
    console.log(`👋 Player joined: ${player.username}`);
    if (player.username === 'Ro9ie') {
        console.log('🎉 Ro9ie joined!');
    }
});

bot.on('playerLeft', (player) => {
    console.log(`👋 Player left: ${player.username}`);
    if (player.username === 'Ro9ie') {
        console.log('😢 Ro9ie left');
    }
});

bot.on('error', (err) => {
    console.error('❌ Connection error:', err.message);
    console.error('Full error:', err);
});

bot.on('end', (reason) => {
    console.log(`🛑 Connection ended: ${reason}`);
});

bot.on('kicked', (reason) => {
    console.log(`🚫 Kicked from server: ${reason}`);
});

// Timeout after 60 seconds
setTimeout(() => {
    console.log('⏰ Test completed after 60 seconds');
    bot.quit();
    process.exit(0);
}, 60000);

console.log('⏱️ Test will run for 60 seconds...');