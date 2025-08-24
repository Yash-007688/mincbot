// Make sure you have 'mineflayer-pathfinder' and its goals installed and available in the global scope or required appropriately
// const { GoalNear, GoalGetToBlock, GoalFollow, GoalSleep } = require('mineflayer-pathfinder').goals;
// You will also need 'minecraft-data' available
// const mcData = require('minecraft-data')(bot.version);

class BotProperties {
  static chatLog = [];

  constructor(name, teamMembers, mineflayerBot) {
    this.name = name;
    this.team = teamMembers || []; // Array of other BotProperties instances
    this.mineflayerBot = mineflayerBot; // The actual mineflayer bot instance
    this.mcData = require('minecraft-data')(this.mineflayerBot.version); // Minecraft data for the bot's version
    this.state = 'idle'; // e.g., 'idle', 'gathering_wood', 'building', 'exploring', 'attacking', 'healing', 'sleeping', 'crafting'
    this.target = null; // e.g., { type: 'entity', entity: <mineflayer.Entity> } or { type: 'position', position: <Vec3> }
    this.inventory = {}; // Simple representation: { itemName: count }
    this.health = 20;
    this.food = 20;
    this.saturation = 5; // Needed for sprinting/healing
    this.equipment = { // Simplified representation
      hand: null,
      head: null,
      torso: null,
      legs: null,
      feet: null
    };
    this.lastChatTime = 0;
    this.chatCooldown = 5000; // 5 seconds cooldown between chats

    // Resource gathering specific properties
    this.requiredWoodCount = 20; // Target amount of wood logs/planks equivalent
    this.hasCraftingTable = false;
    this.needsBasicResources = true; // Flag for initial resource gathering

    // Autonomy settings (can be toggled)
    this.canEat = true;
    this.canSleep = true;
    this.canBuild = true;
    this.canCraft = true;
    this.canFight = true;
    this.canExplore = true;

    // Following properties
    this.targetBotToFollow = null; // BotProperties instance of the bot to follow
    this.followDistance = 5; // Distance to maintain when following

    // Goal management for pathfinder
    this.currentGoal = null; // Store the current pathfinder goal
  }

  // Basic commands (using Mineflayer where available, otherwise conceptual)

  // Teleport to coordinates or another bot
  tp(target) {
    if (!this.mineflayerBot || !this.mineflayerBot.entity) {
      console.warn(`[${this.name}] Cannot teleport, bot not ready.`);
      return;
    }

    let targetPos = null;

    if (target instanceof BotProperties && target.mineflayerBot && target.mineflayerBot.entity) {
      // Teleport to another bot's position
      targetPos = target.mineflayerBot.entity.position;
      console.log(`[${this.name}] Attempting to teleport to bot ${target.name} at ${targetPos}.`);
    } else if (target && typeof target.x === 'number' && typeof target.y === 'number' && typeof target.z === 'number') {
      // Teleport to coordinates
      targetPos = new Vec3(target.x, target.y, target.z);
      console.log(`[${this.name}] Attempting to teleport to coordinates ${targetPos}.`);
      } else {
      console.warn(`[${this.name}] Invalid target for teleport.`);
      this.chat("Invalid target for teleport.");
      return;
    }

    if (targetPos) {
      try {
        // Use the built-in bot.teleport method (if available/works on server)
        // Note: Server must allow this, typically via commands or permissions.
        // A more reliable method in survival might be pathfinding or using ender pearls.
        this.mineflayerBot.entity.position = targetPos; // Directly setting position (might not work on all servers)
        console.log(`[${this.name}] Teleported to ${targetPos}.`);
        this.chat(`Teleported to ${targetPos.x.toFixed(0)}, ${targetPos.y.toFixed(0)}, ${targetPos.z.toFixed(0)}.`);
        this.setGoal(null); // Clear any previous goal after teleport
        this.state = 'idle'; // Go back to idle after teleport
      } catch (e) {
        console.error(`[${this.name}] Error during teleport:`, e.message);
        this.chat("Teleport failed.");
       }
    }
  }

  // Give an item to another bot (using Mineflayer)
  give(itemName, targetBot) {
    if (!this.mineflayerBot || !targetBot || !targetBot.mineflayerBot) return;
      // Find item by name in Mineflayer inventory
      const item = this.mineflayerBot.inventory.findInventoryItem(itemName);

      if (item) {
        console.log(`${this.name} found ${itemName} in inventory. Attempting to toss to ${targetBot.name}.`);
        // Toss the item stack towards the target bot
        this.mineflayerBot.tossStack(item, (err) => {
          if (err) {
            this.mineflayerBot.chat(`Error giving ${itemName}: ${err.message}`);
            console.error(`${this.name} Error giving ${itemName}: ${err.message}`);
          } else {
            this.mineflayerBot.chat(`Giving ${itemName} to ${targetBot.name}!`);
            console.log(`${this.name} successfully tossed ${itemName} to ${targetBot.name}.`);
            // Note: The target bot needs logic to pick up the item (Mineflayer does this automatically nearby)
          }
        });
      } else {
        this.mineflayerBot.chat(`I don't have ${itemName}.`);
        console.log(`${this.name} doesn't have ${itemName} in inventory.`);
    }
  }

  // Add an item to conceptual inventory (not used with Mineflayer for real inventory)
  add(item) {
    // This method is likely not needed if using Mineflayer for real inventory.
    // You could potentially use it to track items the bot desires or is looking for.
    console.log(`${this.name}: Conceptual add item ${item} (Mineflayer manages real inventory)`);
     // if (!this.mineflayerBot) { this.inventory.push(item); console.log(`${this.name} added ${item} to conceptual inventory.`); }
  }

  // List available commands
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
    if (this.mineflayerBot) {
        this.mineflayerBot.chat(`Commands: tp <target>, give <item> <target>, chat <msg>, status, follow <botName>, unfollow`);
    }
  }

  // Show bot's current status (using Mineflayer data)
  status() {
     if (!this.mineflayerBot || !this.mineflayerBot.entity) {
         this.chat("I am not currently connected or ready.");
         return;
     }
         const pos = this.mineflayerBot.entity.position;
    const statusMsg = `Status: ${this.state}. Pos: (${pos.x.toFixed(0)}, ${pos.y.toFixed(0)}, ${pos.z.toFixed(0)}). Health: ${this.health}, Food: ${this.food}.`;
    this.chat(statusMsg);
    console.log(`[${this.name}] ${statusMsg}`);

    // Report important inventory items (wood, crafting table, tools, food, armor)
    const importantItems = [
        'oak_log', 'spruce_log', 'birch_log', 'jungle_log', 'acacia_log', 'dark_oak_log',
        'oak_planks', 'crafting_table', 'wooden_axe', 'wooden_pickaxe', 'stone_axe', 'stone_pickaxe',
        'iron_axe', 'iron_pickaxe', 'diamond_axe', 'diamond_pickaxe', 'netherite_axe', 'netherite_pickaxe',
        'cooked_beef', 'bread', 'golden_apple', 'bed', 'red_bed' // Added 'bed' and 'red_bed'
    ];
    let inventorySummary = 'Inventory: ';
    let hasItem = false;
    for (const item of this.mineflayerBot.inventory.items()) {
        if (importantItems.includes(item.name)) {
            inventorySummary += `${item.name} x${item.count}, `;
            hasItem = true;
        }
    }
    if (hasItem) {
         // Remove trailing comma and space
        inventorySummary = inventorySummary.slice(0, -2);
         this.chat(inventorySummary);
         console.log(`[${this.name}] ${inventorySummary}`);
    } else {
         this.chat("Inventory: (No important items)");
         console.log(`[${this.name}] Inventory: (No important items)`);
    }
     // Report equipped armor
    let armorSummary = 'Equipment: ';
    let hasArmor = false;
    if (this.equipment.head) { armorSummary += `Head: ${this.equipment.head}, `; hasArmor = true; }
    if (this.equipment.torso) { armorSummary += `Torso: ${this.equipment.torso}, `; hasArmor = true; }
    if (this.equipment.legs) { armorSummary += `Legs: ${this.equipment.legs}, `; hasArmor = true; }
    if (this.equipment.feet) { armorSummary += `Feet: ${this.equipment.feet}, `; hasArmor = true; }

    if (hasArmor) {
         armorSummary = armorSummary.slice(0, -2);
         this.chat(armorSummary);
         console.log(`[${this.name}] ${armorSummary}`);
    } else {
         this.chat("Equipment: (None)");
         console.log(`[${this.name}] Equipment: (None)`);
    }
  }

  // Combat with any type of mob (using Mineflayer)
  attack(mobEntity) { // Accept Mineflayer entity
    if (!this.mineflayerBot || !mobEntity) return;
    console.log(`${this.name} attacks ${mobEntity.displayName || mobEntity.type} at (${mobEntity.position.x.toFixed(1)}, ${mobEntity.position.y.toFixed(1)}, ${mobEntity.position.z.toFixed(1)})`);
    this.mineflayerBot.attack(mobEntity);
  }

  // Respawn method (Mineflayer handles this, but can trigger movement)
  respawn(spawnPoint = { x: 0, y: 0, z: 0 }) {
    this.health = 20;
    this.food = 20;
    this.saturation = 5;
    this.position = { ...spawnPoint }; // Conceptual position update
    console.log(`${this.name} has respawned at (${spawnPoint.x}, ${spawnPoint.y}, ${spawnPoint.z})`);
    // Mineflayer handles respawning automatically.
    // You could add logic here to pathfind back to a base or team if needed.
     if (this.mineflayerBot) {
         // Example movement towards spawn point (requires pathfinder GoalNear)
         // this.mineflayerBot.pathfinder.goto(new GoalNear(spawnPoint.x, spawnPoint.y, spawnPoint.z, 5));
     }
  }

  // Method to update the bot's state and actions autonomously
  update() {
    if (!this.mineflayerBot || !this.mineflayerBot.entity) {
      return;
    }

    this.health = this.mineflayerBot.health;
    this.food = this.mineflayerBot.food;
    this.saturation = this.mineflayerBot.saturation;

    // Update inventory representation (simplified, doesn't track NBT, etc.)
    this.inventory = {};
    for (const item of this.mineflayerBot.inventory.items()) {
      this.inventory[item.name] = (this.inventory[item.name] || 0) + item.count;
    }

    // Update equipment representation (simplified)
    this.equipment = {
      hand: this.mineflayerBot.heldItem ? this.mineflayerBot.heldItem.name : null,
      head: this.mineflayerBot.armor[3] ? this.mineflayerBot.armor[3].name : null,
      torso: this.mineflayerBot.armor[2] ? this.mineflayerBot.armor[2].name : null,
      legs: this.mineflayerBot.armor[1] ? this.mineflayerBot.armor[1].name : null,
      feet: this.mineflayerBot.armor[0] ? this.mineflayerBot.armor[0].name : null
    };

    // --- Autonomous Action Logic ---

    // 1. Prioritize survival actions
    this.handleEating();
    this.handleSleeping();
    // this.handleFighting(); // Implement fighting logic

    // 2. Handle initial resource gathering (like a new player)
    this.handleBasicResourceGathering();

    // 3. Handle following if a target bot is set
    this.handleFollowing();

    // 4. Perform state-specific actions
    switch (this.state) {
      case 'idle':
        // If idle, check if basic resources are needed
        if (this.needsBasicResources) {
          this.state = 'gathering_wood';
        } else {
          // If not needing basic resources, maybe start exploring or mining
          // this.state = 'exploring'; // Or other default behavior
        }
        break;
      case 'gathering_wood':
        this.gatherWood();
        break;
      // Implement other states (building, crafting, exploring, etc.)
       case 'moving_to_sleep':
           // Wait for goal to complete
           break;
    }

    // Debugging: Log current state and goal
   // console.log(`[${this.name}] State: ${this.state}, Goal: ${this.currentGoal ? this.currentGoal.constructor.name : 'None'}`);
  }

  // Method to set a new pathfinder goal safely
  setGoal(goal) {
    // Check if the current goal is the same as the new goal
    if (this.currentGoal && goal && this.currentGoal.constructor === goal.constructor &&
      JSON.stringify(this.currentGoal.destination) === JSON.stringify(goal.destination)) {
      // Goal is the same, do nothing to avoid GoalChanged error
      // console.log(`[${this.name}] Goal is already set to the same target.`);
      return;
    }

    // If a goal is currently active, clear it before setting a new one
    if (this.mineflayerBot.pathfinder.goal) {
      // This might trigger the GoalChanged error, but it's necessary to stop the previous path
      this.mineflayerBot.pathfinder.stop();
      // console.log(`[${this.name}] Stopping current goal before setting a new one.`);
    }

    this.currentGoal = goal; // Store the new goal
    if (goal) {
      console.log(`[${this.name}] Setting new goal: ${goal.constructor.name} to ${JSON.stringify(goal.destination)}`);
      try {
        this.mineflayerBot.pathfinder.setGoal(goal);
            } catch (e) {
        console.error(`[${this.name}] Error setting pathfinder goal:`, e.message);
        this.currentGoal = null; // Clear the goal if setting failed
        this.state = 'idle'; // Go back to idle state
      }
        } else {
      console.log(`[${this.name}] Clearing pathfinder goal.`);
    }
  }

  // Check if the bot needs to eat and if it has food
  needsToEat() {
    // Eat if food is low (e.g., 14 or less for saturation regeneration, or lower for health)
    // Also consider saturation level for sprinting/healing
    return this.food < 20 || this.saturation <= 0;
  }

  // Find suitable food in inventory
  findFood() {
    const foodItems = [
      'cooked_beef', 'cooked_porkchop', 'cooked_chicken', 'cooked_mutton',
      'cooked_rabbit', 'cooked_salmon', 'cooked_cod', 'bread', 'carrot',
      'baked_potato', 'apple', 'golden_apple', 'enchanted_golden_apple',
      'melon_slice', 'sweet_berries', 'dried_kelp', 'mushroom_stew',
      'beetroot_soup', 'rabbit_stew'
    ];
    for (const item of this.mineflayerBot.inventory.items()) {
      if (foodItems.includes(item.name) && item.count > 0) {
        // Prioritize golden apples for emergencies? Or just return the first found?
        return item;
      }
    }
    return null; // No food found
  }

  // Handle eating logic
  async handleEating() {
    if (!this.canEat || !this.needsToEat()) {
      return;
    }

    const food = this.findFood();
    if (food) {
      // Check if the bot is currently busy with pathfinding or digging/building
      // Eating might interrupt other actions. Decide if eating is a high priority interrupt.
      // For now, let's assume eating is high priority and interrupts current action.
      // Consider if the bot is in a safe location to eat.
      console.log(`[${this.name}] Needs to eat. Found ${food.name}.`);

      try {
        // Ensure the food item is in the hotbar
        const item = this.mineflayerBot.inventory.findInventoryItem(food.type);
        if (item) {
          await this.mineflayerBot.equip(item, 'hand');
           console.log(`[${this.name}] Equipped ${food.name}. Eating...`);
           // Use bot.consume() for eating
           await this.mineflayerBot.consume();
           console.log(`[${this.name}] Finished eating ${food.name}. Food level: ${this.mineflayerBot.food}`);
           // Maybe announce they ate?
            if (Math.random() < 0.3) { // 30% chance to announce
              this.chat(`Ah, that ${food.name} hit the spot! Hunger: ${this.mineflayerBot.food}`);
            }
        } else {
            console.warn(`[${this.name}] Found ${food.name} in inventory, but not in hotbar? Equip failed.`);
        }
      } catch (e) {
        console.error(`[${this.name}] Error while eating:`, e.message);
        // What to do on error? Maybe try again later or find different food?
           }
      } else {
      // console.log(`[${this.name}] Needs to eat but has no food.`);
      // If no food, the bot should potentially seek out food sources
      // This could transition to a 'gathering_food' state
      // If hunger is critically low, maybe passive mode or seek help?
    }
  }

  // Handle sleeping logic
  async handleSleeping() {
    if (!this.canSleep || !this.mineflayerBot.time.isDay && !this.mineflayerBot.isSleeping) {
      // It's night and the bot is not already sleeping
      // Check if the bot has a bed
      const bed = this.mineflayerBot.inventory.findInventoryItem(this.mcData.itemsByName.red_bed.id); // Assume red bed ID

      if (bed) {
        console.log(`[${this.name}] It's night. Attempting to find a bed location.`);
        // Find a suitable location to place the bed
        // This is a complex task requiring building/placement logic
        // For now, let's simplify: try to find an existing bed block nearby
         const bedBlock = this.mineflayerBot.findBlock({
           matching: this.mcData.blocksByName.red_bed.id,
           maxDistance: 16 // Search radius for existing bed
         });

         if (bedBlock) {
           console.log(`[${this.name}] Found an existing bed at ${bedBlock.position}. Moving to sleep.`);
           this.state = 'moving_to_sleep';
           // Use GoalGetToBlock to move to the bed block
           const goal = new GoalGetToBlock(bedBlock.position.x, bedBlock.position.y, bedBlock.position.z);
           this.setGoal(goal);

         } else {
           console.log(`[${this.name}] No existing bed found nearby. Need to place one.`);
           // Implement logic to find a safe spot and place a bed
           // This requires build plugin or manual block placement logic
           // For now, stay in idle/survival mode
            if (Math.random() < 0.2) { // 20% chance to complain
              this.chat("It's getting dark, I need a bed!");
            }
         }

      } else {
        // console.log(`[${this.name}] It's night but I don't have a bed.`);
        // If no bed, the bot might need to craft one or find materials
        // This could transition to a 'gathering_wool' or 'crafting_bed' state
        if (Math.random() < 0.2) { // 20% chance to complain
          this.chat("I need wool and wood to craft a bed for the night.");
        }
      }
    } else if (this.mineflayerBot.isSleeping) {
      // Bot is currently sleeping, do nothing or check for wake conditions
      // console.log(`[${this.name}] Zzzzzzz...`);
    } else if (this.state === 'moving_to_sleep' && !this.mineflayerBot.pathfinder.goal) {
      // Bot was moving to sleep but goal completed. Try to sleep if near a bed.
       const bedBlock = this.mineflayerBot.findBlock({
          matching: this.mcData.blocksByName.red_bed.id,
          maxDistance: 3 // Check blocks within 3 blocks
       });

       if (bedBlock && this.mineflayerBot.entity.position.distanceTo(bedBlock.position) < 3) {
         console.log(`[${this.name}] Reached bed location. Attempting to sleep.`);
         try {
            await this.mineflayerBot.sleep(bedBlock);
            console.log(`[${this.name}] Successfully started sleeping.`);
            this.state = 'sleeping';
         } catch (e) {
            console.error(`[${this.name}] Error trying to sleep:`, e.message);
             this.chat("Couldn't sleep right now."); // Let the player/team know
            this.state = 'idle'; // Go back to idle
            this.setGoal(null); // Clear the goal
         }
       } else {
          console.log(`[${this.name}] Arrived at location but no bed found or too far. Going idle.`);
         this.state = 'idle'; // Didn't find a bed, go back to idle
         this.setGoal(null); // Clear the goal
       }
    }
  }

  // Handle initial resource gathering (wood -> crafting table -> tools)
  async handleBasicResourceGathering() {
    if (!this.needsBasicResources) {
      return; // No longer need basic resources
    }

    // Check if we have enough wood
    const woodItems = ['oak_log', 'spruce_log', 'birch_log', 'jungle_log', 'acacia_log', 'dark_oak_log'];
    let woodCount = 0;
    for (const item of this.mineflayerBot.inventory.items()) {
      if (woodItems.includes(item.name)) {
        woodCount += item.count;
      } else if (item.name.endsWith('_planks')) {
        woodCount += item.count / 4;
      }
    }

    // Check for crafting table in inventory or placed nearby
    const craftingTableItem = this.mineflayerBot.inventory.findInventoryItem(this.mcData.itemsByName.crafting_table.id);
    const craftingTableBlock = this.mineflayerBot.findBlock({
      matching: this.mcData.blocksByName.crafting_table.id,
      maxDistance: 16 // Search radius for placed crafting table
    });
    this.hasCraftingTable = craftingTableItem !== null || craftingTableBlock !== null;

    console.log(`[${this.name}] Needs basic resources (wood, crafting table). Current wood equivalent: ${woodCount}/${this.requiredWoodCount}. Has crafting table: ${this.hasCraftingTable}.`);

    // State progression for basic resources:
    // 1. Gather wood if needed
    // 2. Craft/find crafting table if needed
    // 3. Craft basic tools (axe, pickaxe)

    if (woodCount < this.requiredWoodCount) {
      // Need more wood, transition to or stay in gathering_wood state
      if (this.state !== 'gathering_wood') {
        console.log(`[${this.name}] Transitioning to gathering_wood state.`);
        this.state = 'gathering_wood';
        this.setGoal(null); // Clear any previous goal
      }
    } else if (!this.hasCraftingTable) {
      // Have enough wood, but need a crafting table
       console.log(`[${this.name}] Have enough wood, need a crafting table.`);
      if (craftingTableItem) {
        // Have item, need to place it. Requires placement logic.
         if (this.state !== 'placing_crafting_table') {
             this.state = 'placing_crafting_table';
              // Implement placing logic here - requires a location and placement function
             console.warn(`[${this.name}] Placing crafting table logic not yet implemented.`);
             this.chat("I have a crafting table, but don't know where to place it yet!");
             this.state = 'idle'; // Go back to idle for now
         }
      } else {
        // Need to craft a crafting table
        if (this.state !== 'crafting_crafting_table') {
          console.log(`[${this.name}] Attempting to craft a crafting table.`);
          // Crafting requires having planks (derived from wood) and a crafting recipe
          const planksCount = this.inventory['oak_planks'] || 0; // Assume oak planks for now
          if (planksCount >= 4) { // Crafting table requires 4 planks
            try {
              const craftingTableRecipe = this.mineflayerBot.recipesFor(this.mcData.itemsByName.crafting_table.id)[0];
              if (craftingTableRecipe) {
                console.log(`[${this.name}] Found recipe for crafting table. Crafting...`);
                await this.mineflayerBot.craft(craftingTableRecipe, 1, null); // Craft 1 crafting table
                console.log(`[${this.name}] Successfully crafted a crafting table.`);
                this.hasCraftingTable = true; // Update status
                 this.state = 'idle'; // Or transition to placing state
                 this.chat("I crafted a crafting table!");
              } else {
                console.warn(`[${this.name}] Could not find crafting recipe for crafting table.`);
                this.chat("Hmm, I can't figure out how to craft a crafting table.");
                this.state = 'idle'; // Can't craft, go back to idle
              }
            } catch (e) {
              console.error(`[${this.name}] Error crafting crafting table:`, e.message);
               this.chat("Crafting failed for some reason.");
              this.state = 'idle'; // Crafting failed, go back to idle
            }
          } else {
            console.log(`[${this.name}] Need more planks to craft a crafting table. Have ${planksCount}.`);
            // Need to convert logs to planks first - this could be a sub-step
            // For now, let's just report it and stay idle or go back to wood gathering if logs are low
            if (woodCount > 0 && planksCount < 4) {
              // Need to craft planks from logs
              const logItem = this.mineflayerBot.inventory.items().find(item => woodItems.includes(item.name));
              if (logItem) {
                console.log(`[${this.name}] Attempting to craft planks from ${logItem.name}.`);
                try {
                  const plankRecipe = this.mineflayerBot.recipesFor(this.mcData.itemsByName.oak_planks.id).find(recipe => recipe.ingredients.some(ing => ing.id === logItem.type));
                  if (plankRecipe) {
                    // Craft planks until we have enough for a crafting table (or more)
                    // Calculate how many planks we need (at least 4)
                    const neededPlanks = 4 - planksCount;
                    // Calculate how many logs needed (at least 1 log gives 4 planks)
                    const neededLogs = Math.ceil(neededPlanks / 4);
                    // Craft planks from available logs
                    const logsToCraft = Math.min(logItem.count, neededLogs);

                    if (logsToCraft > 0) {
                      await this.mineflayerBot.craft(plankRecipe, logsToCraft, null); // Craft planks
                      console.log(`[${this.name}] Successfully crafted ${logsToCraft * 4} planks.`);
                       this.state = 'crafting_crafting_table'; // Go back to trying to craft the table
                    } else {
                      console.log(`[${this.name}] Not enough logs to craft planks.`);
                       this.state = 'idle';
                    }

                  } else {
                    console.warn(`[${this.name}] Could not find plank crafting recipe for ${logItem.name}.`);
                     this.state = 'idle';
                  }
                } catch (e) {
                  console.error(`[${this.name}] Error crafting planks:`, e.message);
                   this.state = 'idle';
                }
              } else {
                console.warn(`[${this.name}] Need planks but no logs found to craft them.`);
                this.state = 'idle'; // Can't get planks, go back to idle
              }

            } else {
              // Don't have enough wood, report and go back to gathering
              this.chat(`I need ${this.requiredWoodCount} wood logs to get started.`);
              this.state = 'gathering_wood';
            }
          }
        }
      }
    } else {
      // Have enough wood and a crafting table. Now craft tools.
       // Check for wooden axe and wooden pickaxe
      const hasWoodAxe = this.mineflayerBot.inventory.findInventoryItem(this.mcData.itemsByName.wooden_axe.id) !== null;
      const hasWoodPickaxe = this.mineflayerBot.inventory.findInventoryItem(this.mcData.itemsByName.wooden_pickaxe.id) !== null;

      if (!hasWoodAxe || !hasWoodPickaxe) {
        console.log(`[${this.name}] Have resources, need basic tools (Axe: ${hasWoodAxe}, Pickaxe: ${hasWoodPickaxe}).`);
        if (this.state !== 'crafting_tools') {
          this.state = 'crafting_tools';
          this.craftBasicTools(); // Attempt to craft tools
        }
      } else {
        // Have wood, crafting table, and basic tools
        console.log(`[${this.name}] Basic resource gathering complete.`);
        this.needsBasicResources = false; // Basic gathering complete!
        this.state = 'idle'; // Transition to the next phase (e.g., mining, building)
        this.chat("Okay, I'm geared up with basic tools!");
      }
    }
  }

  async craftBasicTools() {
    const neededTools = [];
    if (this.mineflayerBot.inventory.findInventoryItem(this.mcData.itemsByName.wooden_axe.id) === null) neededTools.push('wooden_axe');
    if (this.mineflayerBot.inventory.findInventoryItem(this.mcData.itemsByName.wooden_pickaxe.id) === null) neededTools.push('wooden_pickaxe');

    if (neededTools.length === 0) {
      console.log(`[${this.name}] Already have basic tools.`);
      this.state = 'idle'; // Or next state
      return;
    }

    console.log(`[${this.name}] Attempting to craft needed tools: ${neededTools.join(', ')}`);

    // Crafting requires a crafting table to be accessible
    const craftingTableBlock = this.mineflayerBot.findBlock({
      matching: this.mcData.blocksByName.crafting_table.id,
      maxDistance: 3 // Needs to be nearby to use
    });

    if (!craftingTableBlock) {
      console.warn(`[${this.name}] Cannot craft tools, no crafting table found nearby.`);
       this.chat("I need a crafting table to craft tools.");
       this.state = 'idle'; // Can't craft, go back to idle
      return;
    }

    // Ensure bot is near the crafting table
     const distanceToTable = this.mineflayerBot.entity.position.distanceTo(craftingTableBlock.position);
     if (distanceToTable > 3) {
       console.log(`[${this.name}] Moving closer to crafting table at ${craftingTableBlock.position}.`);
       this.setGoal(new GoalNear(craftingTableBlock.position.x, craftingTableBlock.position.y, craftingTableBlock.position.z, 1)); // Get within 1 block
       this.state = 'moving_to_crafting_table';
       return;
     }

    // Craft tools one by one
    for (const toolName of neededTools) {
      const itemId = this.mcData.itemsByName[toolName].id;
      const recipe = this.mineflayerBot.recipesFor(itemId)[0]; // Get the first recipe

      if (recipe) {
        console.log(`[${this.name}] Found recipe for ${toolName}. Crafting...`);
        try {
          // Use the crafting table block to craft
          await this.mineflayerBot.craft(recipe, 1, craftingTableBlock);
          console.log(`[${this.name}] Successfully crafted ${toolName}.`);
           // Small delay to prevent potential issues with rapid crafting
          await this.mineflayerBot.waitForTicks(10); // Wait 0.5 seconds
        } catch (e) {
          console.error(`[${this.name}] Error crafting ${toolName}:`, e.message);
           this.chat(`Failed to craft ${toolName}.`);
          this.state = 'idle'; // Crafting failed, go back to idle
          return; // Stop trying to craft other tools for now
        }
      } else {
        console.warn(`[${this.name}] Could not find crafting recipe for ${toolName}.`);
         this.chat(`Don't know how to craft ${toolName}.`);
         this.state = 'idle'; // Can't find recipe, go back to idle
         return; // Stop trying to craft other tools for now
      }
    }

     // If we successfully crafted all needed tools
     console.log(`[${this.name}] Finished crafting basic tools.`);
     this.state = 'idle'; // Basic gathering complete, go back to idle
     this.handleBasicResourceGathering(); // Re-evaluate state after crafting
  }

  // Gather wood logs
  async gatherWood() {
    // Check if we still need wood
    const woodItems = ['oak_log', 'spruce_log', 'birch_log', 'jungle_log', 'acacia_log', 'dark_oak_log'];
    let woodCount = 0;
    for (const item of this.mineflayerBot.inventory.items()) {
      if (woodItems.includes(item.name)) {
        woodCount += item.count;
      } else if (item.name.endsWith('_planks')) {
        woodCount += item.count / 4;
      }
    }

    if (woodCount >= this.requiredWoodCount) {
      console.log(`[${this.name}] Have enough wood. Transitioning from gathering_wood.`);
      this.state = 'idle'; // Or next state like 'crafting_crafting_table'
      this.setGoal(null); // Clear any digging/pathfinding goal
      this.handleBasicResourceGathering(); // Re-evaluate basic resources
      return;
    }

    // Find the nearest wood log block
    const treeLog = this.mineflayerBot.findBlock({
      matching: (block) => woodItems.includes(block.name),
      maxDistance: 32 // Search radius for trees
    });

    if (treeLog) {
      console.log(`[${this.name}] Found ${treeLog.name} at ${treeLog.position}. Pathing to dig.`);
      // Set the goal to get to the block
      const goal = new GoalGetToBlock(treeLog.position.x, treeLog.position.y, treeLog.position.z);

      // Check if the current goal is already to get to this block
      if (this.currentGoal && this.currentGoal instanceof GoalGetToBlock &&
        this.currentGoal.destination.equals(goal.destination)) {
        // Already pathing to this block, do nothing
        // console.log(`[${this.name}] Already pathing to ${treeLog.name}.`);
        return;
      }

      this.setGoal(goal);

      // Once the bot reaches the block (pathfinder goal completes), it needs to dig it.
      // The 'goal_reached' or similar pathfinder event would be used for this.
      // Or, check distance in the update loop and trigger dig if close enough and state is 'gathering_wood'
      if (this.mineflayerBot.entity.position.distanceTo(treeLog.position) < 4) { // Within a few blocks
        // Check if the block is still there and diggable
        const blockToDig = this.mineflayerBot.blockAt(treeLog.position);
         if (blockToDig && woodItems.includes(blockToDig.name) && this.mineflayerBot.canDigBlock(blockToDig)) {
          console.log(`[${this.name}] Close enough to ${blockToDig.name}. Attempting to dig.`);
           this.setGoal(null); // Stop pathfinding once close
          try {
            await this.mineflayerBot.dig(blockToDig);
            console.log(`[${this.name}] Successfully dug ${blockToDig.name}.`);
            // Item will be added to inventory automatically
            // Re-evaluate wood count after digging
             this.gatherWood(); // Recursively call to check if more wood is needed or find next tree
             this.chat(`Found and dug some ${blockToDig.name}!`); // Announce finding
          } catch (e) {
            console.error(`[${this.name}] Error digging ${blockToDig.name}:`, e.message);
             this.chat(`Couldn't dig ${blockToDig.name}.`);
            this.state = 'idle'; // Digging failed, go back to idle
            this.setGoal(null);
          }
        } else {
          console.log(`[${this.name}] Block at ${treeLog.position} is no longer wood or not diggable.`);
           this.state = 'idle'; // Block changed or not diggable, go back to idle
           this.setGoal(null);
        }
      }

    } else {
      // No wood found nearby
      // console.log(`[${this.name}] No wood logs found nearby.`);
      // If no wood, the bot might need to explore further or report to the team
      if (Math.random() < 0.1) { // 10% chance to report
        this.chat("Can't find any trees nearby. Need to explore.");
      }
       this.state = 'exploring'; // Transition to exploring state to find trees
       this.setGoal(null); // Clear any previous goal
    }
  }

  // Announce finding items (simplified - can be expanded)
   announceFinding(itemName, count) {
     // Only announce if not on cooldown and finding a non-trivial amount/type
     if (Date.now() - this.lastChatTime > this.chatCooldown && count > 0) {
        // Avoid announcing very common items unless it's early game
        const commonItems = ['dirt', 'cobblestone', 'stone']; // Add more common items
        if (!commonItems.includes(itemName) || this.needsBasicResources) {
          this.chat(`Found ${count} x ${itemName}!`);
          this.lastChatTime = Date.now(); // Reset cooldown
        }
     }
   }

   // Handle item collection event (this needs to be called from the mineflayer bot's 'collect' event)
  handleItemCollected(entity) {
    if (entity.type === 'item') {
      const item = entity.metadata[this.mcData.entityMetadata.items.id]; // Get item metadata
      if (item) {
        const itemName = this.mcData.items[item.itemId].name;
        const itemCount = item.itemCount;
        // console.log(`[${this.name}] Collected ${itemCount} x ${itemName}`);
        this.announceFinding(itemName, itemCount); // Announce the finding
        // The inventory is updated automatically by mineflayer
      }
    }
  }

  // Handle following another bot
  handleFollowing() {
    if (this.targetBotToFollow && this.targetBotToFollow.mineflayerBot && this.targetBotToFollow.mineflayerBot.entity) {
      const targetPos = this.targetBotToFollow.mineflayerBot.entity.position;
      const distance = this.mineflayerBot.entity.position.distanceTo(targetPos);

      if (distance > this.followDistance) {
        // If far away, set goal to follow
        const goal = new GoalFollow(this.targetBotToFollow.mineflayerBot.entity, this.followDistance);

        // Check if the current goal is already to follow this bot
        if (this.currentGoal && this.currentGoal instanceof GoalFollow && this.currentGoal.entity === this.targetBotToFollow.mineflayerBot.entity) {
          // Already following this bot, do nothing
          // console.log(`[${this.name}] Already following ${this.targetBotToFollow.name}.`);
          return;
        }
        console.log(`[${this.name}] Following ${this.targetBotToFollow.name}. Moving to ${targetPos}.`);
        this.setGoal(goal);
        this.state = 'following';
      } else {
        // If close enough, stop pathfinding and stay idle or do something else near the target
         if (this.state === 'following' && this.mineflayerBot.pathfinder.goal) {
            console.log(`[${this.name}] Reached follow distance. Stopping pathfinder.`);
           this.setGoal(null); // Stop pathfinding
            this.state = 'idle'; // Go back to idle near the target
         }
      }
    } else if (this.state === 'following') {
      console.log(`[${this.name}] Target bot to follow is no longer available.`);
      this.clearTargetBotToFollow(); // Clear the target
      this.state = 'idle'; // Go back to idle
      this.setGoal(null); // Clear any pathfinding goal
    }
  }

  // Set the target bot to follow
  setTargetBotToFollow(targetBotProps) {
    if (targetBotProps && targetBotProps !== this && targetBotProps instanceof BotProperties) {
      this.targetBotToFollow = targetBotProps;
      this.chat(`Following ${targetBotProps.name}!`);
       this.state = 'following'; // Transition to following state
    } else {
      this.chat("Invalid bot specified to follow.");
    }
  }

  // Clear the target bot to follow
  clearTargetBotToFollow() {
    if (this.targetBotToFollow) {
      this.chat(`No longer following ${this.targetBotToFollow.name}.`);
      this.targetBotToFollow = null;
       if (this.state === 'following') {
           this.state = 'idle'; // Go back to idle
           this.setGoal(null); // Clear pathfinding goal
       }
    } else {
      this.chat("I wasn't following anyone.");
    }
  }

  // Simplified chat method with cooldown
  chat(message) {
    if (Date.now() - this.lastChatTime > this.chatCooldown) {
      this.mineflayerBot.chat(message);
      this.lastChatTime = Date.now();
    }
  }

  // Implement other actions: build, craft, fight, explore, mine, etc.
  // Example: mine a specific block
  async mineBlock(block) {
    if (!this.mineflayerBot || !this.mineflayerBot.entity) return;
    if (!block || !this.mineflayerBot.canDigBlock(block)) {
      console.warn(`[${this.name}] Cannot mine invalid or undiggable block.`);
      return;
    }

    console.log(`[${this.name}] Mining block ${block.name} at ${block.position}.`);
     this.state = 'mining';
     this.setGoal(new GoalNear(block.position.x, block.position.y, block.position.z, 1)); // Move close to the block

     // Wait for goal to complete before digging, or check distance in update loop
     // For now, simplified: assume goal is reached quickly if close enough
     if (this.mineflayerBot.entity.position.distanceTo(block.position) < 4) {
       this.setGoal(null); // Stop pathfinding
       try {
         await this.mineflayerBot.dig(block);
         console.log(`[${this.name}] Successfully mined ${block.name}.`);
         this.state = 'idle'; // Mining complete, go back to idle
          this.announceFinding(block.name, 1); // Announce mining the block
       } catch (e) {
         console.error(`[${this.name}] Error mining ${block.name}:`, e.message);
         this.chat(`Failed to mine ${block.name}.`);
         this.state = 'idle'; // Mining failed, go back to idle
       }
     }
  }

  // Add other action methods here (e.g., async buildHouse(), async craftItem(itemId), async attack(entity), async exploreArea())
}

module.exports = BotProperties;

