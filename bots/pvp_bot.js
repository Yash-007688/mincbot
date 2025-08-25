import dotenv from 'dotenv'
import { createBot } from 'mineflayer'
import pkg from 'mineflayer-pathfinder'
const { pathfinder, Movements, goals } = pkg
import { plugin as pvp } from 'mineflayer-pvp'

dotenv.config()

const HOST = process.env.HOST || '127.0.0.1'
const PORT = process.env.PORT ? Number(process.env.PORT) : 25565
const VERSION = process.env.VERSION || false
const BOT_COUNT = process.env.BOT_COUNT ? Number(process.env.BOT_COUNT) : 20
const BASE_NAME = process.env.BASE_NAME || 'PvPBot_'
const ATTACK_RANGE = process.env.ATTACK_RANGE ? Number(process.env.ATTACK_RANGE) : 16
const RETARGET_MS = process.env.RETARGET_MS ? Number(process.env.RETARGET_MS) : 2500
const LOG_PREFIX = process.env.LOG_PREFIX || '[PvP]'
const EXCLUDE_NAMES = new Set((process.env.EXCLUDE_NAMES || '').split(',').map(s => s.trim()).filter(Boolean))

// Authentication settings
const AUTH_MODE = process.env.AUTH_MODE || 'offline' // 'offline', 'microsoft', 'mojang'
const EMAIL = process.env.EMAIL || ''
const PASSWORD = process.env.PASSWORD || ''

/**
 * Create a single bot instance with PvP + pathfinder behavior
 */
function spawnBot(index) {
  const username = `${BASE_NAME}${index}`
  
  // Bot configuration with authentication
  const botConfig = {
    host: HOST,
    port: PORT,
    username,
    version: VERSION || undefined
  }
  
  // Add authentication if configured
  if (AUTH_MODE === 'microsoft' && EMAIL && PASSWORD) {
    botConfig.auth = 'microsoft'
    botConfig.email = EMAIL
    botConfig.password = PASSWORD
  } else if (AUTH_MODE === 'mojang' && EMAIL && PASSWORD) {
    botConfig.auth = 'mojang'
    botConfig.email = EMAIL
    botConfig.password = PASSWORD
  }
  
  const bot = createBot(botConfig)

  bot.loadPlugin(pathfinder)
  bot.loadPlugin(pvp)

  let currentTarget = null
  let lastTargetAt = 0

  function log(...args) {
    // eslint-disable-next-line no-console
    console.log(`${LOG_PREFIX} [${bot.username}]`, ...args)
  }

  bot.once('login', () => {
    log('Logged in.')
  })

  bot.on('spawn', () => {
    const mcData = bot.registry
    const movements = new Movements(bot, mcData)
    bot.pathfinder.setMovements(movements)
    log('Spawned and ready.')
  })

  // Retarget loop
  const interval = setInterval(() => {
    try {
      if (!bot.entity || !bot.player) return
      const now = Date.now()
      if (now - lastTargetAt < RETARGET_MS) return
      lastTargetAt = now

      // Find nearest non-bot player within ATTACK_RANGE
      const players = Object.values(bot.players || {})
        .filter(p => p?.entity && p.username && p.username !== bot.username && !p.username.startsWith(BASE_NAME) && !EXCLUDE_NAMES.has(p.username))

      if (players.length === 0) return

      // Sort by distance
      players.sort((a, b) => {
        const da = a.entity.position.distanceTo(bot.entity.position)
        const db = b.entity.position.distanceTo(bot.entity.position)
        return da - db
      })

      const candidate = players[0]
      if (!candidate?.entity) return
      const distance = candidate.entity.position.distanceTo(bot.entity.position)
      if (distance > ATTACK_RANGE) return

      if (!currentTarget || currentTarget.username !== candidate.username) {
        currentTarget = candidate
        log('Targeting', currentTarget.username, 'at', vectorToString(currentTarget.entity.position))
        // Move toward target and engage PvP
        try {
          bot.pvp.attack(currentTarget.entity)
        } catch (err) {
          log('Error starting PvP:', err?.message || err)
        }
      }
    } catch (e) {
      log('Retarget loop error:', e?.message || e)
    }
  }, 1000)

  // Log when our current target dies near us (approximate "kill")
  bot.on('entityDead', (entity) => {
    try {
      if (!entity || entity.type !== 'player') return
      if (!currentTarget || !currentTarget.entity) return
      if (entity.id !== currentTarget.entity.id) return

      const pos = entity.position || bot.entity?.position
      const coords = vectorToString(pos)
      log(`Eliminated ${currentTarget.username} at ${coords}`)
      currentTarget = null
    } catch (e) {
      log('entityDead handler error:', e?.message || e)
    }
  })

  bot.on('kicked', (reason) => {
    log('Kicked:', reason)
    clearInterval(interval)
  })

  bot.on('end', () => {
    log('Disconnected')
    clearInterval(interval)
  })

  bot.on('error', (err) => {
    log('Error:', err?.message || err)
  })

  return bot
}

function vectorToString(vec) {
  if (!vec) return '(unknown, unknown, unknown)'
  const x = Math.round(vec.x)
  const y = Math.round(vec.y)
  const z = Math.round(vec.z)
  return `(${x}, ${y}, ${z})`
}

// Spawn N bots
const bots = []
for (let i = 0; i < BOT_COUNT; i += 1) {
  bots.push(spawnBot(i))
}

process.on('SIGINT', () => {
  for (const b of bots) {
    try { b.quit('Shutting down') } catch {}
  }
  setTimeout(() => process.exit(0), 250)
})