class BotProperties {
  static chatLog = []; // Shared chat log for all bots

  constructor(name, team = [], mineflayerBot = null) {
    this.name = name;
    this.team = team; // Array of BotProperties instances
    this.isAlive = true;
    this.position = { x: 0, y: 0, z: 0 };
    this.inventory = [];
    this.mineflayerBot = mineflayerBot; // Mineflayer bot instance
    this.targetBotToFollow = null; // Property to store bot to follow
  }

  // --- Chat functionality ---
  chat(message) {
    const chatMessage = `[${this.name}]: ${message}`;
    BotProperties.chatLog.push(chatMessage);
    console.log(chatMessage);
  }

  static showChatLog() {
    console.log('--- Chat Log ---');
    BotProperties.chatLog.forEach(msg => console.log(msg));
    console.log('----------------');
  }

  // --- Basic commands ---
  tp(target) {
    if (typeof target === 'object' && target.x !== undefined) {
      this.teleport(target);
    } else if (target instanceof BotProperties) {
      this.teleport(target.position);
    } else {
      console.log('Invalid teleport target.');
    }
  }

  give(item, targetBot) {
    this.transferItemToBot(item, targetBot);
  }

  add(item) {
    this.addItemToInventory(item);
  }

  help() {
    console.log(`Available commands for ${this.name}:
    - tp(target): Teleport to coordinates or another bot
    - give(item, targetBot): Give an item to another bot
    - add(item): Add an item to inventory
    - chat(message): Send a message to chat
    - showChatLog(): Show chat history (static)
    - help(): List available commands
    - status(): Show bot's current status
    `);
  }

  status() {
    console.log(`Status of ${this.name}:
    Alive: ${this.isAlive}
    Position: (${this.position.x}, ${this.position.y}, ${this.position.z})
    Inventory: ${this.inventory.join(', ') || 'Empty'}
    Team: ${this.team.map(bot => bot.name).join(', ') || 'None'}
    `);
  }

  // --- Existing methods below ---

  attack(mob) {
    if (!this.isAlive) return;
    console.log(`${this.name} attacks ${mob.type} at (${mob.position.x}, ${mob.position.y}, ${mob.position.z})`);
  }

  respawn(spawnPoint = { x: 0, y: 0, z: 0 }) {
    this.isAlive = true;
    this.position = { ...spawnPoint };
    console.log(`${this.name} has respawned at (${spawnPoint.x}, ${spawnPoint.y}, ${spawnPoint.z})`);
  }

  teleport(targetPosition) {
    if (!this.isAlive) return;
    this.position = { ...targetPosition };
    console.log(`${this.name} teleported to (${targetPosition.x}, ${targetPosition.y}, ${targetPosition.z})`);
  }

  coordinateWithTeam(action) {
    if (!this.isAlive) return;
    this.team.forEach(member => {
      console.log(`${this.name} coordinates with ${member.name || member} to ${action}`);
    });
  }

  helpTeamMemberInTrouble() {
    this.team.forEach(member => {
      if (member.isInTrouble) {
        console.log(`${this.name} is helping ${member.name}`);
        this.teleport(member.position);
      }
    });
  }

  addItemToInventory(item) {
    this.inventory.push(item);
    console.log(`${this.name} added ${item} to inventory.`);
  }

  transferItemToBot(item, targetBot) {
    const index = this.inventory.indexOf(item);
    if (index !== -1) {
      this.inventory.splice(index, 1);
      targetBot.addItemToInventory(item);
      console.log(`${this.name} transferred ${item} to ${targetBot.name}.`);
    } else {
      console.log(`${item} not found in ${this.name}'s inventory.`);
    }
  }

  makeArmor(targetBot = this) {
    const armor = 'Armor';
    targetBot.addItemToInventory(armor);
    console.log(`${this.name} made armor for ${targetBot.name}.`);
  }

  grind(task, times = 1) {
    for (let i = 0; i < times; i++) {
      console.log(`${this.name} is grinding: ${task} (${i + 1}/${times})`);
    }
  }

  update() {
    if (!this.isAlive || !this.mineflayerBot) return; // Only update if alive and has a Mineflayer instance

    const bot = this.mineflayerBot;
    const mcData = require('minecraft-data')(bot.version); // Assuming mcData is available

    // --- Autonomous Behavior Logic ---

    // 1. Attack nearby hostile mobs
    // Find nearest hostile mob within a certain range
    const hostileMob = bot.nearestEntity(entity => {
        return entity.type === 'mob' && entity.hostile; // Check if it's a hostile mob
    });

    if (hostileMob) {
        const distance = bot.entity.position.distanceTo(hostileMob.position);
        if (distance < 6) { // Attack if within 6 blocks
            console.log(`${this.name} is attacking ${hostileMob.mobType}`);
            bot.attack(hostileMob);
        } else { // Move closer if mob is detected but too far
            console.log(`${this.name} moving towards ${hostileMob.mobType}`);
            // Requires mineflayer-pathfinder plugin
            // bot.pathfinder.goto(new GoalNear(hostileMob.position.x, hostileMob.position.y, hostileMob.position.z, 3));
        }
    } else {
        // If no hostile mob, perform other actions
    }

    // 2. Mine specific resources when needed (Example: Coal Ore)
    // You would need logic to decide *when* mining is needed (e.g., low on coal, need fuel)
    // For demonstration, let's just look for nearby coal ore if not attacking
    if (!hostileMob) {
        const coalOre = bot.findBlock({
            matching: mcData.blocksByName.coal_ore?.id, // Find Coal Ore block
            maxDistance: 16, // Search within 16 blocks
            useExtraInfo: true, // Needed to check if reachable
        });

        if (coalOre) {
            console.log(`${this.name} found Coal Ore at (${coalOre.position.x}, ${coalOre.position.y}, ${coalOre.position.z})`);
            // Requires mineflayer-pathfinder and tool logic
            // bot.pathfinder.goto(new GoalGetToBlock(coalOre.position.x, coalOre.position.y, coalOre.position.z));
            // Once near, check if we have a pickaxe and dig
            // if (bot.hasTool(coalOre)) { // Conceptual check
            //   bot.dig(coalOre);
            // }
        }
    }


    // 3. Follow or guard another bot (if targetBotToFollow is set)
    if (this.targetBotToFollow && this.targetBotToFollow.mineflayerBot) {
        const targetPos = this.targetBotToFollow.mineflayerBot.entity.position;
        const distanceToTarget = bot.entity.position.distanceTo(targetPos);

        if (distanceToTarget > 3) { // If further than 3 blocks, move closer
            console.log(`${this.name} is following ${this.targetBotToFollow.name}`);
            // Requires mineflayer-pathfinder plugin
            // bot.pathfinder.goto(new GoalFollow(this.targetBotToFollow.mineflayerBot.entity, 3)); // Follow within 3 blocks
        } else {
            // console.log(`${this.name} is guarding ${this.targetBotToFollow.name}`);
            // Stand guard or perform other actions while close
        }
    }

    // 4. Heal themselves or others
    // Check own health
    if (bot.health < 15) { // If health is below 15 (out of 20)
        console.log(`${this.name} is trying to heal. Current health: ${bot.health}`);
        // Requires having food in inventory and logic to eat it
        // const foodItem = bot.inventory.findInventoryItem(item => mcData.foodsByName[item.name]);
        // if (foodItem) {
        //     bot.equip(foodItem, 'hand');
        //     bot.consume();
        // }
    }

    // Check team members' health and heal them (requires proximity and healing items/abilities)
    this.team.forEach(member => {
       if (member.mineflayerBot && member.mineflayerBot.health < 10) { // If team member health is low
           console.log(`${this.name} sees ${member.name}'s health is low (${member.mineflayerBot.health}).`);
           // Logic to move to the member and use a healing item/ability
           // Requires mineflayer-pathfinder and healing item usage
           // bot.pathfinder.goto(new GoalNear(member.mineflayerBot.entity.position.x, member.mineflayerBot.entity.position.y, member.mineflayerBot.entity.position.z, 3));
           // Once near, use healing item (e.g., splash potion)
           // const healingItem = bot.inventory.findInventoryItem(item => item.name === 'splash_potion'); // Example
           // if (healingItem) {
           //     bot.equip(healingItem, 'hand');
           //     bot.activateItem(); // Use the potion
           // }
       }
    });


    // Existing autonomous logic examples:
    // If a team member is in trouble, go help them
    this.team.forEach(member => {
      // Assume member has an 'isInTrouble' flag set elsewhere
      if (member.isInTrouble) {
        console.log(`${this.name} detects ${member.name} is in trouble and is moving to help.`);
        // This currently uses the conceptual tp, should use Mineflayer pathfinding
        // this.tp(member.position); // Use the tp method which uses chat command
        // Or better, use pathfinding:
        // if (member.mineflayerBot) {
        //     bot.pathfinder.goto(new GoalNear(member.mineflayerBot.entity.position.x, member.mineflayerBot.entity.position.y, member.mineflayerBot.entity.position.z, 1));
        // }
      }
    });

    // Add other autonomous behaviors here based on game state and bot goals...
  }

  // Method to set a bot to follow
  setTargetBotToFollow(targetBot) {
      if (targetBot instanceof BotProperties) {
          this.targetBotToFollow = targetBot;
          console.log(`${this.name} is now targeting ${targetBot.name} to follow.`);
      } else {
          console.log(`${this.name}: Invalid target for following.`);
      }
  }

  // Method to clear the target bot to follow
  clearTargetBotToFollow() {
      this.targetBotToFollow = null;
      console.log(`${this.name} is no longer following a target.`);
  }
}

// Example usage:
const bravo = new BotProperties('Bravo');
const charlie = new BotProperties('Charlie');
const alpha = new BotProperties('Alpha', [bravo, charlie]);

alpha.chat('Hello team!');
bravo.chat('Hi Alpha!');
charlie.chat('Ready for action!');
BotProperties.showChatLog();

module.exports = BotProperties; 