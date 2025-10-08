require('dotenv').config();
const { Client, GatewayIntentBits, SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, StringSelectMenuBuilder, AttachmentBuilder } = require('discord.js');
const mongoose = require('mongoose');
const axios = require('axios');

const User = require('./models/User');
const RedeemCode = require('./models/RedeemCode');
const Admin = require('./models/Admin');
const Blacklist = require('./models/Blacklist');

const OWNER_ID = '1037768611126841405';
const ADMIN_IDS = ['1037768611126841405', '1417151491482980385'];

async function isAdmin(userId) {
  if (ADMIN_IDS.includes(userId)) return true;
  const admin = await Admin.findOne({ discordId: userId });
  return !!admin;
}

async function isBlacklisted(userId) {
  const blacklisted = await Blacklist.findOne({ discordId: userId });
  return !!blacklisted;
}

const client = new Client({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent]
});

const PREFIX = '₹';
const coinflipCooldowns = new Map();
const userMessageCounts = new Map();
let chatCoinsEnabled = true;
const CHAT_CHANNEL_ID = '1413785935207727113';

const COIN_ROLES = [
  { threshold: 15000, name: 'Diamond Collector', color: 0xB9F2FF, roleId: null },
  { threshold: 10000, name: 'Platinum Collector', color: 0xE5E4E2, roleId: null },
  { threshold: 8000, name: 'Gold Collector', color: 0xFFD700, roleId: null },
  { threshold: 5000, name: 'Collector', color: 0x87CEEB, roleId: null },
  { threshold: 3000, name: 'Bronze Collector', color: 0xCD7F32, roleId: null },
  { threshold: 1000, name: 'Coin Starter', color: 0x90EE90, roleId: null }
];

mongoose.connect(process.env.MONGODB_URI);

async function updateUserRoles(user, guild, userId) {
  try {
    const member = await guild.members.fetch(userId);
    const currentBalance = user.balance;
    
    // Find appropriate role
    const newRole = COIN_ROLES.find(role => currentBalance >= role.threshold);
    const currentCoinRoles = member.roles.cache.filter(role => 
      COIN_ROLES.some(coinRole => role.name === coinRole.name)
    );
    
    const congratsChannel = guild.channels.cache.get('1420323441378328646');
    
    if (newRole) {
      // Check if user already has this role
      const hasRole = member.roles.cache.some(role => role.name === newRole.name);
      
      if (!hasRole) {
        // Remove old coin roles
        await member.roles.remove(currentCoinRoles);
        
        // Create or get the new role
        let role = guild.roles.cache.find(r => r.name === newRole.name);
        if (!role) {
          role = await guild.roles.create({
            name: newRole.name,
            color: newRole.color,
            reason: 'Coin collector role'
          });
        }
        
        // Add new role
        await member.roles.add(role);
        
        // Send congratulations message
        if (congratsChannel) {
          const congratsEmbed = new EmbedBuilder()
            .setTitle('🎉 Role Achievement Unlocked!')
            .setColor(newRole.color)
            .setDescription(`Congratulations <@${userId}>! You've earned the **${newRole.name}** role!`)
            .addFields(
              { name: '💰 Balance Required', value: `${newRole.threshold.toLocaleString()} coins`, inline: true },
              { name: '💳 Current Balance', value: `${currentBalance.toLocaleString()} coins`, inline: true },
              { name: '🏆 Achievement', value: `You've reached ${newRole.threshold.toLocaleString()} coins!`, inline: false }
            )
            .setThumbnail(member.user.displayAvatarURL({ dynamic: true }))
            .setTimestamp();
          
          await congratsChannel.send({ embeds: [congratsEmbed] });
        }
      }
    } else {
      // Remove all coin roles if balance is too low
      if (currentCoinRoles.size > 0) {
        const oldRole = currentCoinRoles.first();
        await member.roles.remove(currentCoinRoles);
        
        // Send streak breakdown message
        if (congratsChannel) {
          const breakdownEmbed = new EmbedBuilder()
            .setTitle('💔 Streak Breakdown')
            .setColor(0xff0000)
            .setDescription(`<@${userId}> has lost their **${oldRole.name}** role due to insufficient balance.`)
            .addFields(
              { name: '📉 Previous Role', value: oldRole.name, inline: true },
              { name: '💳 Current Balance', value: `${currentBalance.toLocaleString()} coins`, inline: true },
              { name: '💪 Keep Going!', value: 'Earn more coins to get your role back!', inline: false }
            )
            .setThumbnail(member.user.displayAvatarURL({ dynamic: true }))
            .setTimestamp();
          
          await congratsChannel.send({ embeds: [breakdownEmbed] });
        }
      }
    }
  } catch (error) {
    console.error('Role update error:', error.message);
  }
}

function generatePassword() {
  return Math.random().toString(36).slice(-12);
}

async function getNests() {
  try {
    const response = await axios.get(`${process.env.PTERODACTYL_URL}/api/application/nests`, {
      headers: {
        'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    console.log('Nests response:', response.data);
    return response.data.data || [];
  } catch (error) {
    console.error('Nest fetch error:', error.response?.data || error.message);
    throw new Error(`Failed to fetch nests: ${error.response?.data?.message || error.message}`);
  }
}

async function getEggs(nestId) {
  try {
    const response = await axios.get(`${process.env.PTERODACTYL_URL}/api/application/nests/${nestId}/eggs`, {
      headers: {
        'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    console.log('Eggs response:', response.data);
    return response.data.data || [];
  } catch (error) {
    console.error('Eggs fetch error:', error.response?.data || error.message);
    throw new Error(`Failed to fetch eggs: ${error.response?.data?.message || error.message}`);
  }
}

async function createPterodactylUser(username, email, password) {
  try {
    // Check if user already exists
    try {
      const existingResponse = await axios.get(`${process.env.PTERODACTYL_URL}/api/application/users?filter[email]=${email}`, {
        headers: {
          'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
          'Accept': 'application/json'
        }
      });
      if (existingResponse.data.data.length > 0) {
        return existingResponse.data.data[0].attributes;
      }
    } catch (e) {}
    
    const response = await axios.post(`${process.env.PTERODACTYL_URL}/api/application/users`, {
      email,
      username,
      first_name: username,
      last_name: 'User',
      password
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    console.log('User creation response:', response.data);
    return response.data.attributes;
  } catch (error) {
    console.error('User creation error:', error.response?.data || error.message);
    if (error.response?.data?.errors) {
      console.error('Detailed errors:', error.response.data.errors);
    }
    const errorMsg = error.response?.data?.errors ? 
      Object.values(error.response.data.errors).flat().join(', ') : 
      error.response?.data?.message || error.message;
    throw new Error(`Failed to create user: ${errorMsg}`);
  }
}

async function createPterodactylServer(userId, name, nest, egg, customSpecs = null) {
  try {
    // Get first available node and allocation
    let nodeId = 1;
    let allocationId = null;
    
    try {
      const nodesResponse = await axios.get(`${process.env.PTERODACTYL_URL}/api/application/nodes`, {
        headers: {
          'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
          'Accept': 'application/json'
        }
      });
      
      if (nodesResponse.data.data && nodesResponse.data.data.length > 0) {
        nodeId = nodesResponse.data.data[0].attributes.id;
        console.log(`Using node ID: ${nodeId}`);
        
        // Get available allocation from the node
        const allocationsResponse = await axios.get(`${process.env.PTERODACTYL_URL}/api/application/nodes/${nodeId}/allocations`, {
          headers: {
            'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
            'Accept': 'application/json'
          }
        });
        
        const availableAllocation = allocationsResponse.data.data.find(alloc => !alloc.attributes.assigned);
        if (availableAllocation) {
          allocationId = availableAllocation.attributes.id;
          console.log(`Using allocation ID: ${allocationId}`);
        }
      }
    } catch (e) {
      console.log('Error getting node/allocation, using defaults:', e.message);
    }
    
    // Get egg details for proper configuration
    let eggConfig = {
      docker_image: 'ghcr.io/pterodactyl/yolks:java_17',
      startup: 'java -Xms128M -Xmx{{SERVER_MEMORY}}M -jar server.jar',
      environment: {}
    };
    
    try {
      const eggResponse = await axios.get(`${process.env.PTERODACTYL_URL}/api/application/nests/${nest}/eggs/${egg}?include=variables`, {
        headers: {
          'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
          'Accept': 'application/json'
        }
      });
      
      const eggData = eggResponse.data.attributes;
      eggConfig.docker_image = eggData.docker_image;
      eggConfig.startup = eggData.startup;
      
      // Set default environment variables
      if (eggResponse.data.attributes.relationships?.variables?.data) {
        eggResponse.data.attributes.relationships.variables.data.forEach(variable => {
          const varData = variable.attributes;
          eggConfig.environment[varData.env_variable] = varData.default_value || '';
        });
      }
    } catch (e) {
      console.log('Using default egg configuration');
    }
    
    const serverData = {
      name: name,
      user: parseInt(userId),
      egg: parseInt(egg),
      docker_image: eggConfig.docker_image,
      startup: eggConfig.startup,
      environment: eggConfig.environment,
      limits: {
        memory: customSpecs?.memory || 3072,
        swap: 0,
        disk: customSpecs?.disk || 5120,
        io: 500,
        cpu: customSpecs?.cpu || 100
      },
      feature_limits: {
        databases: 1,
        backups: 1
      }
    };
    
    // Add allocation if found, otherwise use deploy method
    if (allocationId) {
      serverData.allocation = {
        default: parseInt(allocationId)
      };
    } else {
      serverData.deploy = {
        locations: [parseInt(nodeId)],
        dedicated_ip: false,
        port_range: []
      };
    }
    
    console.log('Creating server with data:', JSON.stringify(serverData, null, 2));
    
    const response = await axios.post(`${process.env.PTERODACTYL_URL}/api/application/servers`, serverData, {
      headers: {
        'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    
    console.log('Server creation successful!');
    return response.data.attributes;
  } catch (error) {
    console.error('Server creation error:', error.response?.data || error.message);
    if (error.response?.data?.errors) {
      console.error('Detailed errors:', error.response.data.errors);
    }
    let errorMsg = 'Unknown error';
    if (error.response?.data?.errors) {
      if (Array.isArray(error.response.data.errors)) {
        errorMsg = error.response.data.errors.map(err => err.detail || err.message || err).join(', ');
      } else {
        errorMsg = Object.values(error.response.data.errors).flat().join(', ');
      }
    } else if (error.response?.data?.message) {
      errorMsg = error.response.data.message;
    } else {
      errorMsg = error.message;
    }
    throw new Error(`Server creation failed: ${errorMsg}`);
  }
}

client.once('ready', async () => {
  console.log(`Bot ready as ${client.user.tag}`);
  
  // Set rotating status
  const statuses = [
    { name: 'Made by Shadow', type: 0 },
    { name: 'BlazeNode || IT Solution', type: 0 }
  ];
  
  let statusIndex = 0;
  setInterval(() => {
    client.user.setActivity(statuses[statusIndex].name, { type: statuses[statusIndex].type });
    statusIndex = (statusIndex + 1) % statuses.length;
  }, 10000);
  
  const guild = client.guilds.cache.get(process.env.GUILD_ID);
  if (!guild) return;

  const commands = [
    new SlashCommandBuilder()
      .setName('create')
      .setDescription('Create a new server with step-by-step setup')
      .addStringOption(option =>
        option.setName('server')
          .setDescription('Start server creation')
          .setRequired(true)
          .addChoices({ name: 'server', value: 'server' })),
    new SlashCommandBuilder()
      .setName('nest')
      .setDescription('View available nests and eggs')
      .addStringOption(option =>
        option.setName('nest')
          .setDescription('Nest ID to view eggs')
          .setRequired(false)),
    new SlashCommandBuilder()
      .setName('help')
      .setDescription('Show all available commands and bot information'),
    new SlashCommandBuilder()
      .setName('shop')
      .setDescription('View and buy server resources'),
    new SlashCommandBuilder()
      .setName('resources')
      .setDescription('View your resource inventory'),
    new SlashCommandBuilder()
      .setName('balance')
      .setDescription('Check your coin balance'),
    new SlashCommandBuilder()
      .setName('coinflip')
      .setDescription('Flip a coin to win or lose coins')
      .addIntegerOption(option =>
        option.setName('amount')
          .setDescription('Amount of coins to bet')
          .setRequired(true)
          .setMinValue(1))
      .addStringOption(option =>
        option.setName('choice')
          .setDescription('Choose heads or tails')
          .setRequired(false)
          .addChoices(
            { name: 'Heads', value: 'heads' },
            { name: 'Tails', value: 'tails' }
          )),
    new SlashCommandBuilder()
      .setName('leaderboard')
      .setDescription('View top 10 richest users'),

    new SlashCommandBuilder()
      .setName('redeem')
      .setDescription('Redeem a code for coins')
      .addStringOption(option =>
        option.setName('code')
          .setDescription('Redeem code')
          .setRequired(true)),
    new SlashCommandBuilder()
      .setName('admin')
      .setDescription('Admin management commands')
      .addStringOption(option =>
        option.setName('action')
          .setDescription('Action to perform')
          .setRequired(true)
          .addChoices(
            { name: 'add', value: 'add' },
            { name: 'remove', value: 'remove' },
            { name: 'list', value: 'list' }
          ))
      .addUserOption(option =>
        option.setName('user')
          .setDescription('User to add/remove as admin')
          .setRequired(false)),
    new SlashCommandBuilder()
      .setName('coins')
      .setDescription('Coin management commands')
      .addStringOption(option =>
        option.setName('action')
          .setDescription('Action to perform')
          .setRequired(true)
          .addChoices(
            { name: 'add', value: 'add' },
            { name: 'remove', value: 'remove' }
          ))
      .addUserOption(option =>
        option.setName('user')
          .setDescription('User to add/remove coins')
          .setRequired(true))
      .addIntegerOption(option =>
        option.setName('amount')
          .setDescription('Amount of coins')
          .setRequired(true)),
    new SlashCommandBuilder()
      .setName('blacklist')
      .setDescription('Blacklist management')
      .addStringOption(option =>
        option.setName('action')
          .setDescription('Action to perform')
          .setRequired(true)
          .addChoices(
            { name: 'add', value: 'add' },
            { name: 'remove', value: 'remove' }
          ))
      .addUserOption(option =>
        option.setName('user')
          .setDescription('User to blacklist/unblacklist')
          .setRequired(true)),
    new SlashCommandBuilder()
      .setName('createcode')
      .setDescription('Create redeem codes')
      .addStringOption(option =>
        option.setName('code')
          .setDescription('Redeem code')
          .setRequired(true))
      .addIntegerOption(option =>
        option.setName('coins')
          .setDescription('Coins to give')
          .setRequired(true))
      .addIntegerOption(option =>
        option.setName('uses')
          .setDescription('Number of users who can use')
          .setRequired(true)),
    new SlashCommandBuilder()
      .setName('server')
      .setDescription('Server management for admins')
      .addStringOption(option =>
        option.setName('action')
          .setDescription('Action to perform')
          .setRequired(true)
          .addChoices(
            { name: 'show', value: 'show' }
          )),
    new SlashCommandBuilder()
      .setName('chat')
      .setDescription('Chat coins system management')
      .addStringOption(option =>
        option.setName('action')
          .setDescription('Action to perform')
          .setRequired(true)
          .addChoices(
            { name: 'on', value: 'on' },
            { name: 'off', value: 'off' },
            { name: 'status', value: 'status' }
          ))
  ];

  await guild.commands.set(commands);
  
  // Send earning coins embed to specific channel
  const earningChannel = guild.channels.cache.get('1413785935207727107');
  if (earningChannel) {
    const earningEmbed = new EmbedBuilder()
      .setTitle('💰 Earning Coins')
      .setColor(0x87CEEB)
      .setDescription('Here are the ways to earn coins on BlazeNode:')
      .addFields(
        { name: '👥 Per Invite', value: 'You will get **200 coins** for each user you invite!', inline: false },
        { name: '🎁 Redeem Codes', value: 'You can redeem codes given by the owners for free coins!', inline: false },
        { name: '🎰 Gamble Games', value: 'Play gambling games like coinflip to win more coins!', inline: false }
      )
      .setFooter({ text: 'Click Buy Coins below to purchase coins with real money' });
    
    const buyCoinsButton = new ActionRowBuilder()
      .addComponents(
        new ButtonBuilder()
          .setCustomId('buy_coins_main')
          .setLabel('Buy Coins')
          .setStyle(ButtonStyle.Primary)
          .setEmoji('💰')
      );
    
    await earningChannel.send({ embeds: [earningEmbed], components: [buyCoinsButton] });
  }
});

client.on('messageCreate', async message => {
  if (message.author.bot || message.guildId !== process.env.GUILD_ID) return;
  
  // Check if user is blacklisted for all commands
  if (await isBlacklisted(message.author.id)) {
    return;
  }
  
  // Chat coins system
  if (chatCoinsEnabled && message.channelId === CHAT_CHANNEL_ID && !message.content.startsWith(PREFIX)) {
    const userId = message.author.id;
    const currentCount = userMessageCounts.get(userId) || 0;
    const newCount = currentCount + 1;
    
    userMessageCounts.set(userId, newCount);
    
    if (newCount >= 2) {
      try {
        const user = await User.findOne({ discordId: userId });
        if (user) {
          user.balance += 1;
          await user.save();
          userMessageCounts.set(userId, 0);
        }
      } catch (error) {
        console.error('Chat coins error:', error.message);
      }
    }
  }
  
  // Handle shopping responses
  const shoppingState = global.userShopping?.[message.author.id];
  if (shoppingState && message.channelId === shoppingState.channelId && shoppingState.step === 'buying') {
    const choice = parseInt(message.content.trim());
    
    if (choice >= 1 && choice <= 6) {
      try {
        const user = await User.findOne({ discordId: message.author.id });
        if (!user) {
          await message.reply('You need to create a server first!');
          return;
        }
        
        let price = 0;
        let itemName = '';
        let resourceKey = '';
        
        switch (choice) {
          case 1:
            price = 1200;
            itemName = '1GB RAM';
            resourceKey = 'ram';
            break;
          case 2:
            price = 1000;
            itemName = '50% CPU';
            resourceKey = 'cpu';
            break;
          case 3:
            price = 800;
            itemName = '1GB Disk';
            resourceKey = 'disk';
            break;
          case 4:
            if (user.resources.serverSlots >= 2) {
              await message.reply('❌ You can only buy maximum 2 extra server slots!');
              return;
            }
            price = 1000;
            itemName = 'Extra Server Slot';
            resourceKey = 'serverSlots';
            break;
          case 5:
            price = 1000;
            itemName = '1 Backup Slot';
            resourceKey = 'backups';
            break;
          case 6:
            price = 1000;
            itemName = '1 Additional Port';
            resourceKey = 'ports';
            break;
        }
        
        if (user.balance < price) {
          await message.reply(`❌ You don't have enough coins! You need ${price} coins but only have ${user.balance} coins.`);
          return;
        }
        
        user.balance -= price;
        if (resourceKey === 'cpu') {
          user.resources[resourceKey] += 50;
        } else {
          user.resources[resourceKey] += 1;
        }
        await user.save();
        
        const purchaseEmbed = new EmbedBuilder()
          .setTitle('✅ Purchase Successful!')
          .setColor(0x00ff00)
          .addFields(
            { name: '🛒 Purchased', value: itemName, inline: true },
            { name: '💰 Cost', value: `${price} coins`, inline: true },
            { name: '💳 New Balance', value: `${user.balance} coins`, inline: true }
          );
        
        await message.reply({ embeds: [purchaseEmbed] });
        delete global.userShopping[message.author.id];
      } catch (error) {
        await message.reply('Error processing purchase.');
      }
    } else {
      await message.reply('Please enter a valid number (1-6).');
    }
    delete global.userShopping[message.author.id];
    return;
  }
  
  // Handle resource adding responses
  const addingState = global.userAddingResource?.[message.author.id];
  if (addingState && message.channelId === addingState.channelId) {
    const amount = parseInt(message.content.trim());
    
    if (amount > 0 && amount <= addingState.maxAmount) {
      try {
        const user = await User.findOne({ discordId: message.author.id });
        if (!user) {
          await message.reply('User not found!');
          return;
        }
        
        // Update server resources via Pterodactyl API
        try {
          const currentServer = await axios.get(`${process.env.PTERODACTYL_URL}/api/application/servers/${addingState.serverId}?include=allocations`, {
            headers: {
              'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
              'Accept': 'application/json'
            }
          });
          
          const currentLimits = currentServer.data.attributes.limits;
          const currentFeatureLimits = currentServer.data.attributes.feature_limits;
          const currentAllocations = currentServer.data.attributes.relationships?.allocations?.data || [];
          let updateData = {};
          
          switch (addingState.resourceType) {
            case 'ram':
              updateData = {
                memory: currentLimits.memory + (amount * 1024),
                swap: currentLimits.swap,
                disk: currentLimits.disk,
                io: currentLimits.io,
                cpu: currentLimits.cpu
              };
              break;
            case 'cpu':
              updateData = {
                memory: currentLimits.memory,
                swap: currentLimits.swap,
                disk: currentLimits.disk,
                io: currentLimits.io,
                cpu: currentLimits.cpu + amount
              };
              break;
            case 'disk':
              updateData = {
                memory: currentLimits.memory,
                swap: currentLimits.swap,
                disk: currentLimits.disk + (amount * 1024),
                io: currentLimits.io,
                cpu: currentLimits.cpu
              };
              break;
            case 'backups':
              await axios.patch(`${process.env.PTERODACTYL_URL}/api/application/servers/${addingState.serverId}/build`, {
                feature_limits: {
                  databases: currentFeatureLimits.databases,
                  backups: currentFeatureLimits.backups + amount,
                  allocations: currentFeatureLimits.allocations
                }
              }, {
                headers: {
                  'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
                  'Content-Type': 'application/json',
                  'Accept': 'application/json'
                }
              });
              
              user.resources[addingState.resourceType] -= amount;
              await user.save();
              
              const backupEmbed = new EmbedBuilder()
                .setTitle('✅ Backup Slots Added!')
                .setColor(0x00ff00)
                .addFields(
                  { name: '➕ Added', value: `${amount} Backup Slots`, inline: true },
                  { name: '🖥️ Server', value: `ID: ${addingState.serverId}`, inline: true },
                  { name: '📦 Remaining', value: `${user.resources[addingState.resourceType]} Backup Slots`, inline: true }
                );
              
              await message.reply({ embeds: [backupEmbed] });
              delete global.userAddingResource[message.author.id];
              return;
              
            case 'ports':
              // Ports need allocation management - simplified for now
              user.resources[addingState.resourceType] -= amount;
              await user.save();
              
              const portEmbed = new EmbedBuilder()
                .setTitle('✅ Port Credits Added!')
                .setColor(0x00ff00)
                .setDescription('Port allocation updated. Contact admin for manual port assignment.')
                .addFields(
                  { name: '➕ Added', value: `${amount} Port Credits`, inline: true },
                  { name: '📦 Remaining', value: `${user.resources[addingState.resourceType]} Port Credits`, inline: true }
                );
              
              await message.reply({ embeds: [portEmbed] });
              delete global.userAddingResource[message.author.id];
              return;
          }
          
          // Update server limits for RAM, CPU, Disk
          if (['ram', 'cpu', 'disk'].includes(addingState.resourceType)) {
            const buildData = {
              limits: updateData,
              feature_limits: currentFeatureLimits
            };
            
            // Add allocation if exists
            if (currentAllocations.length > 0) {
              buildData.allocation = currentAllocations[0].attributes.id;
            }
            
            await axios.patch(`${process.env.PTERODACTYL_URL}/api/application/servers/${addingState.serverId}/build`, buildData, {
              headers: {
                'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
              }
            });
          }
          
          // Update user resources
          user.resources[addingState.resourceType] -= amount;
          await user.save();
          
          const successEmbed = new EmbedBuilder()
            .setTitle('✅ Resource Added Successfully!')
            .setColor(0x00ff00)
            .addFields(
              { name: '➕ Added', value: `${amount} ${addingState.resourceType.toUpperCase()}`, inline: true },
              { name: '🖥️ Server', value: `ID: ${addingState.serverId}`, inline: true },
              { name: '📦 Remaining', value: `${user.resources[addingState.resourceType]} ${addingState.resourceType.toUpperCase()}`, inline: true }
            );
          
          await message.reply({ embeds: [successEmbed] });
        } catch (apiError) {
          console.error('Server update error:', apiError.response?.data || apiError.message);
          await message.reply(`❌ Failed to update server: ${apiError.response?.data?.errors?.[0]?.detail || apiError.message}`);
        }
        
        delete global.userAddingResource[message.author.id];
      } catch (error) {
        await message.reply('Error adding resource.');
      }
    } else {
      await message.reply(`Please enter a valid amount (1-${addingState.maxAmount}).`);
    }
    return;
  }
  
  // Handle setup responses
  const userState = global.userSetup?.[message.author.id];
  if (userState && message.channelId === userState.channelId) {
    const input = message.content.trim();
    
    if (userState.step === 'nest' && !isNaN(parseInt(input))) {
      userState.selectedNest = parseInt(input);
      userState.step = 'completed_nest';
      
      const successEmbed = new EmbedBuilder()
        .setTitle('✅ Nest Selected!')
        .setColor(0x00ff00)
        .setDescription(`You selected nest **${input}**. Now click **Step 2: Select Egg** button above.`);
      
      await message.reply({ embeds: [successEmbed] });
      
      // Update original message to unlock egg button
      try {
        const channel = message.guild.channels.cache.get(userState.channelId);
        const originalMessage = await channel.messages.fetch(userState.messageId);
        
        const updatedButtons = new ActionRowBuilder()
          .addComponents(
            new ButtonBuilder()
              .setCustomId('setup_nest')
              .setLabel('Step 1: Select Nest ✅')
              .setStyle(ButtonStyle.Success)
              .setEmoji('🗂️')
              .setDisabled(true),
            new ButtonBuilder()
              .setCustomId('setup_egg')
              .setLabel('Step 2: Select Egg')
              .setStyle(ButtonStyle.Primary)
              .setEmoji('🥚'),
            new ButtonBuilder()
              .setCustomId('setup_create')
              .setLabel('Step 3: Create Server')
              .setStyle(ButtonStyle.Secondary)
              .setEmoji('✨')
              .setDisabled(true)
          );
        
        await originalMessage.edit({ components: [updatedButtons] });
      } catch (e) {
        console.error('Failed to update buttons:', e.message);
      }
      return;
    }
    
    if (userState.step === 'egg' && !isNaN(parseInt(input))) {
      userState.selectedEgg = parseInt(input);
      userState.step = 'completed_egg';
      
      const successEmbed = new EmbedBuilder()
        .setTitle('✅ Egg Selected!')
        .setColor(0x00ff00)
        .setDescription(`You selected egg **${input}**. Now click **Step 3: Create Server** button above to finalize.`);
      
      await message.reply({ embeds: [successEmbed] });
      
      // Update original message to unlock create button
      try {
        const channel = message.guild.channels.cache.get(userState.channelId);
        const originalMessage = await channel.messages.fetch(userState.messageId);
        
        const updatedButtons = new ActionRowBuilder()
          .addComponents(
            new ButtonBuilder()
              .setCustomId('setup_nest')
              .setLabel('Step 1: Select Nest ✅')
              .setStyle(ButtonStyle.Success)
              .setEmoji('🗂️')
              .setDisabled(true),
            new ButtonBuilder()
              .setCustomId('setup_egg')
              .setLabel('Step 2: Select Egg ✅')
              .setStyle(ButtonStyle.Success)
              .setEmoji('🥚')
              .setDisabled(true),
            new ButtonBuilder()
              .setCustomId('setup_create')
              .setLabel('Step 3: Create Server')
              .setStyle(ButtonStyle.Primary)
              .setEmoji('✨')
          );
        
        await originalMessage.edit({ components: [updatedButtons] });
      } catch (e) {
        console.error('Failed to update buttons:', e.message);
      }
      return;
    }
  }
  
  if (!message.content.startsWith(PREFIX)) return;

  const args = message.content.slice(PREFIX.length).trim().split(/ +/);
  const command = args.shift().toLowerCase();

  if (command === 'create' && args[0] === 'server') {
    try {
      const existingUser = await User.findOne({ discordId: message.author.id });
      if (existingUser && existingUser.hasServer) {
        return message.reply('You already have a server!');
      }
      
      const setupEmbed = new EmbedBuilder()
        .setTitle('🎮 Server Creation Setup')
        .setColor(0x0099ff)
        .setDescription('Follow the steps below to create your server:')
        .addFields(
          { name: 'Step 1', value: 'Click **Select Nest** to choose your server type', inline: false },
          { name: 'Step 2', value: 'Click **Select Egg** to choose your server configuration', inline: false },
          { name: 'Step 3', value: 'Click **Create Server** to finalize creation', inline: false },
          { name: '💾 Server Specs', value: '**RAM:** 3GB | **CPU:** 100% | **Disk:** 5GB', inline: false }
        )
        .setFooter({ text: 'Your credentials will be sent via DM after creation' });
      
      const setupButtons = new ActionRowBuilder()
        .addComponents(
          new ButtonBuilder()
            .setCustomId('setup_nest')
            .setLabel('Step 1: Select Nest')
            .setStyle(ButtonStyle.Primary)
            .setEmoji('🗂️'),
          new ButtonBuilder()
            .setCustomId('setup_egg')
            .setLabel('Step 2: Select Egg')
            .setStyle(ButtonStyle.Secondary)
            .setEmoji('🥚')
            .setDisabled(true),
          new ButtonBuilder()
            .setCustomId('setup_create')
            .setLabel('Step 3: Create Server')
            .setStyle(ButtonStyle.Success)
            .setEmoji('✨')
            .setDisabled(true)
        );
      
      const sentMessage = await message.reply({ embeds: [setupEmbed], components: [setupButtons] });
      
      // Store message ID for button updates
      global.userSetup = global.userSetup || {};
      global.userSetup[message.author.id] = { messageId: sentMessage.id, channelId: message.channelId };
    } catch (error) {
      await message.reply('Error starting server creation.');
    }
  }

  if (command === 'help') {
    const helpEmbed = new EmbedBuilder()
      .setTitle('🤖 BlazeNode Panel Bot - Help')
      .setColor(0x00ff00)
      .setDescription('Complete Discord bot for Pterodactyl panel management')
      .addFields(
        {
          name: '📋 Available Commands',
          value: '`/create server` - Create a new server\n`/shop` - Buy server resources\n`/resources` - View your inventory\n`/balance` - Check coin balance\n`/coinflip` - Gamble coins\n`/nest` - View nests/eggs\n`/help` - Show this menu',
          inline: false
        },
        {
          name: '₹ Prefix Commands',
          value: '`₹create server` - Create server\n`₹nest` - View nests\n`₹nest <nest_id>` - View eggs\n`₹help` - Show help menu',
          inline: false
        },
        {
          name: '🎮 Server Specifications',
          value: '**RAM:** 3GB\n**CPU:** 100%\n**Disk:** 5GB\n**Databases:** 1\n**Backups:** 1',
          inline: true
        },
        {
          name: '🔧 Bot Components',
          value: '• **Discord.js v14** - Bot framework\n• **MongoDB** - Database storage\n• **Axios** - API requests\n• **Pterodactyl API** - Panel integration',
          inline: true
        },
        {
          name: '✨ Features',
          value: '• Step-by-step server creation\n• Resource shop & management\n• Coin system with gambling\n• Server resource upgrades\n• Private DM credentials',
          inline: false
        },
        {
          name: '📧 Account Details',
          value: 'Email format: `username@gmail.com`\nPassword: Auto-generated secure password\nCredentials sent via DM after server creation',
          inline: false
        }
      )
      .setFooter({ text: 'BlazeNode Panel Bot | Powered by Pterodactyl API' })
      .setTimestamp();
    
    await message.reply({ embeds: [helpEmbed] });
  }

  if (command === 'shop') {
    const shopEmbed = new EmbedBuilder()
      .setTitle('🛒 BlazeNode Resource Shop')
      .setColor(0xffd700)
      .setDescription('Purchase resources to upgrade your servers!')
      .addFields(
        { name: '💾 1GB RAM', value: '**Price:** 1,200 coins', inline: true },
        { name: '⚡ 50% CPU', value: '**Price:** 1,000 coins', inline: true },
        { name: '💿 1GB Disk', value: '**Price:** 800 coins', inline: true },
        { name: '🖥️ Extra Server Slot', value: '**Price:** 1,000 coins', inline: true },
        { name: '💾 1 Backup Slot', value: '**Price:** 1,000 coins', inline: true },
        { name: '🔌 1 Additional Port', value: '**Price:** 1,000 coins', inline: true }
      )
      .setFooter({ text: 'Click Buy Resources to purchase items' });
    
    const shopButton = new ActionRowBuilder()
      .addComponents(
        new ButtonBuilder()
          .setCustomId('buy_resources')
          .setLabel('Buy Resources')
          .setStyle(ButtonStyle.Primary)
          .setEmoji('🛒')
      );
    
    await message.reply({ embeds: [shopEmbed], components: [shopButton] });
  }

  if (command === 'resources') {
    try {
      const user = await User.findOne({ discordId: message.author.id });
      if (!user) {
        return message.reply('You need to create a server first!');
      }
      
      const resourceEmbed = new EmbedBuilder()
        .setTitle('📦 Your Resource Inventory')
        .setColor(0x00ff99)
        .addFields(
          { name: '💾 RAM', value: `${user.resources.ram} GB`, inline: true },
          { name: '⚡ CPU', value: `${user.resources.cpu}%`, inline: true },
          { name: '💿 Disk', value: `${user.resources.disk} GB`, inline: true },
          { name: '🖥️ Server Slots', value: `${user.resources.serverSlots}`, inline: true },
          { name: '💾 Backups', value: `${user.resources.backups}`, inline: true },
          { name: '🔌 Ports', value: `${user.resources.ports}`, inline: true },
          { name: '💰 Balance', value: `${user.balance} coins`, inline: true },
          { name: '📊 Total Value', value: `${(user.resources.ram * 1200) + (user.resources.cpu * 20) + (user.resources.disk * 800) + (user.resources.serverSlots * 1000) + (user.resources.backups * 1000) + (user.resources.ports * 1000)} coins`, inline: true }
        )
        .setFooter({ text: 'Use resources to upgrade your servers' });
      
      const addResourceButton = new ActionRowBuilder()
        .addComponents(
          new ButtonBuilder()
            .setCustomId('add_resource')
            .setLabel('Add Resource to Server')
            .setStyle(ButtonStyle.Success)
            .setEmoji('➕')
        );
      
      await message.reply({ embeds: [resourceEmbed], components: [addResourceButton] });
    } catch (error) {
      await message.reply('Error fetching resources.');
    }
  }

  if (command === 'balance') {
    try {
      const user = await User.findOne({ discordId: message.author.id });
      if (!user) {
        return message.reply('You need to create a server first!');
      }
      
      const balanceEmbed = new EmbedBuilder()
        .setTitle('💰 Your Balance')
        .setColor(0xffd700)
        .setDescription(`You have **${user.balance}** coins`)
        .addFields(
          { name: '🎰 Earn More', value: 'Use `₹coinflip` to gamble', inline: true },
          { name: '🛒 Spend Coins', value: 'Use `₹shop` to buy resources', inline: true }
        )
        .setTimestamp();
      
      await message.reply({ embeds: [balanceEmbed] });
    } catch (error) {
      await message.reply('Error fetching balance.');
    }
  }

  if (command === 'coinflip') {
    const amount = parseInt(args[0]);
    const choice = args[1] || (Math.random() < 0.5 ? 'heads' : 'tails');
    
    if (!amount || amount < 1) {
      return message.reply('Usage: `₹coinflip <amount> [heads/tails]`');
    }
    
    try {
      const user = await User.findOne({ discordId: message.author.id });
      if (!user) {
        return message.reply('You need to create a server first!');
      }
      
      if (user.balance < amount) {
        return message.reply(`You don't have enough coins! You have ${user.balance} coins.`);
      }
      
      const coinResult = Math.random() < 0.5 ? 'heads' : 'tails';
      const won = choice.toLowerCase() === coinResult;
      
      if (won) {
        user.balance += amount;
        await user.save();
        
        const winEmbed = new EmbedBuilder()
          .setTitle('🎉 You Won!')
          .setColor(0x00ff00)
          .setDescription(`The coin landed on **${coinResult}**! You chose **${choice}**`)
          .addFields(
            { name: '💰 Won', value: `${amount} coins`, inline: true },
            { name: '💳 New Balance', value: `${user.balance} coins`, inline: true }
          );
        
        await message.reply({ embeds: [winEmbed] });
      } else {
        user.balance -= amount;
        await user.save();
        
        const loseEmbed = new EmbedBuilder()
          .setTitle('😢 You Lost!')
          .setColor(0xff0000)
          .setDescription(`The coin landed on **${coinResult}**! You chose **${choice}**`)
          .addFields(
            { name: '💸 Lost', value: `${amount} coins`, inline: true },
            { name: '💳 New Balance', value: `${user.balance} coins`, inline: true }
          );
        
        await message.reply({ embeds: [loseEmbed] });
      }
    } catch (error) {
      await message.reply('Error processing coinflip.');
    }
  }

  if (command === 'leaderboard') {
    try {
      const totalUsers = await User.countDocuments({});
      const topUsers = await User.find({}).sort({ balance: -1 }).limit(10);
      
      if (topUsers.length === 0) {
        return message.reply('No users found!');
      }
      
      const leaderboardEmbed = new EmbedBuilder()
        .setTitle('🏆 Coin Leaderboard - Top 10')
        .setColor(0xffd700)
        .setDescription(topUsers.map((user, index) => {
          const medals = ['🥇', '🥈', '🥉', '💫', '✨'];
          const medal = medals[index] || '🔹';
          return `${medal} **${index + 1}.** ${user.username} - ${user.balance.toLocaleString()} coins`;
        }).join('\n'))
        .setFooter({ text: `Page 1 | Total Users: ${totalUsers} | Keep earning coins to climb!` })
        .setTimestamp();
      
      const navigationButtons = new ActionRowBuilder()
        .addComponents(
          new ButtonBuilder()
            .setCustomId('lb_first')
            .setEmoji('⏪')
            .setStyle(ButtonStyle.Secondary)
            .setDisabled(true),
          new ButtonBuilder()
            .setCustomId('lb_prev')
            .setEmoji('◀️')
            .setStyle(ButtonStyle.Secondary)
            .setDisabled(true),
          new ButtonBuilder()
            .setCustomId('lb_next')
            .setEmoji('▶️')
            .setStyle(ButtonStyle.Secondary)
            .setDisabled(totalUsers <= 10),
          new ButtonBuilder()
            .setCustomId('lb_last')
            .setEmoji('⏩')
            .setStyle(ButtonStyle.Secondary)
            .setDisabled(totalUsers <= 10),
          new ButtonBuilder()
            .setCustomId('lb_refresh')
            .setEmoji('🔄')
            .setStyle(ButtonStyle.Primary)
        );
      
      await message.reply({ embeds: [leaderboardEmbed], components: [navigationButtons] });
    } catch (error) {
      await message.reply('Error fetching leaderboard.');
    }
  }

  if (command === 'gamble') {
    const amount = parseInt(args[0]);
    
    if (!amount || amount < 1) {
      return message.reply('Usage: `₹gamble <amount>`');
    }
    
    try {
      const user = await User.findOne({ discordId: message.author.id });
      if (!user) {
        return message.reply('You need to create a server first!');
      }
      
      if (user.balance < amount) {
        return message.reply(`You don't have enough coins! You have ${user.balance} coins.`);
      }
      
      const gambleEmbed = new EmbedBuilder()
        .setTitle('🎰 Choose Your Game')
        .setColor(0xff6b6b)
        .setDescription(`Betting: **${amount}** coins\n\nChoose a gambling game:`)
        .addFields(
          { name: '🎲 Dice Roll', value: 'Roll higher than 50 to win!', inline: true },
          { name: '🃏 Card Draw', value: 'Draw a high card to win!', inline: true },
          { name: '🎰 Slot Machine', value: 'Match 3 symbols to win big!', inline: true }
        )
        .setFooter({ text: 'All games have 50% win chance' });
      
      const gameButtons = new ActionRowBuilder()
        .addComponents(
          new ButtonBuilder()
            .setCustomId(`dice_${amount}`)
            .setLabel('Dice Roll')
            .setStyle(ButtonStyle.Primary)
            .setEmoji('🎲'),
          new ButtonBuilder()
            .setCustomId(`card_${amount}`)
            .setLabel('Card Draw')
            .setStyle(ButtonStyle.Primary)
            .setEmoji('🃏'),
          new ButtonBuilder()
            .setCustomId(`slot_${amount}`)
            .setLabel('Slot Machine')
            .setStyle(ButtonStyle.Primary)
            .setEmoji('🎰')
        );
      
      await message.reply({ embeds: [gambleEmbed], components: [gameButtons] });
    } catch (error) {
      await message.reply('Error starting gamble.');
    }
  }

  if (command === 'nest') {
    const nestId = args[0];
    
    try {
      if (!nestId) {
        const nests = await getNests();
        const nestEmbed = new EmbedBuilder()
          .setTitle('🗂️ Available Nests')
          .setColor(0x0099ff)
          .setDescription(nests.map(nest => `**${nest.attributes.id}** - ${nest.attributes.name}`).join('\n'));
        
        const buttons = [];
        for (let i = 0; i < Math.min(nests.length, 5); i++) {
          buttons.push(
            new ButtonBuilder()
              .setCustomId(`eggs_${nests[i].attributes.id}`)
              .setLabel(`Eggs for ${nests[i].attributes.name}`)
              .setStyle(ButtonStyle.Primary)
              .setEmoji('🥚')
          );
        }
        
        const rows = [];
        for (let i = 0; i < buttons.length; i += 5) {
          rows.push(new ActionRowBuilder().addComponents(buttons.slice(i, i + 5)));
        }
        
        await message.reply({ embeds: [nestEmbed], components: rows });
      } else {
        const eggs = await getEggs(nestId);
        const eggEmbed = new EmbedBuilder()
          .setTitle(`🥚 Eggs for Nest ${nestId}`)
          .setColor(0x00ff99)
          .setDescription(eggs.map(egg => `**${egg.attributes.id}** - ${egg.attributes.name}`).join('\n'));
        
        await message.reply({ embeds: [eggEmbed] });
      }
    } catch (error) {
      console.error('Nest command error:', error.message);
      await message.reply(`Error: ${error.message}`);
    }
  }
  
  if (command === 'redeem') {
    const code = args[0];
    if (!code) {
      return message.reply('Usage: `₹redeem <code>`');
    }
    
    try {
      const redeemCode = await RedeemCode.findOne({ code });
      if (!redeemCode) {
        return message.reply('Invalid redeem code!');
      }
      
      if (redeemCode.currentUses >= redeemCode.maxUses) {
        return message.reply('This code has reached its usage limit!');
      }
      
      if (redeemCode.usedBy.includes(message.author.id)) {
        return message.reply('You have already used this code!');
      }
      
      const user = await User.findOne({ discordId: message.author.id });
      if (!user) {
        return message.reply('You need to create a server first!');
      }
      
      user.balance += redeemCode.coins;
      await user.save();
      
      redeemCode.currentUses += 1;
      redeemCode.usedBy.push(message.author.id);
      await redeemCode.save();
      
      const redeemEmbed = new EmbedBuilder()
        .setTitle('✅ Code Redeemed Successfully!')
        .setColor(0x00ff00)
        .addFields(
          { name: '🎁 Code', value: code, inline: true },
          { name: '💰 Coins Received', value: `${redeemCode.coins}`, inline: true },
          { name: '💳 New Balance', value: `${user.balance}`, inline: true }
        );
      
      await message.reply({ embeds: [redeemEmbed] });
    } catch (error) {
      await message.reply('Error redeeming code.');
    }
  }
});

client.on('interactionCreate', async interaction => {
  try {
    if (interaction.guildId !== process.env.GUILD_ID) return;
    
    // Check if user is blacklisted for all interactions
    if (await isBlacklisted(interaction.user.id)) {
      if (interaction.isCommand()) {
        return interaction.reply({ content: 'You are blacklisted from using this bot.', flags: 64 });
      }
      if (interaction.isButton() || interaction.isStringSelectMenu()) {
        return interaction.reply({ content: 'You are blacklisted from using this bot.', flags: 64 });
      }
      return;
    }
  
  if (interaction.isStringSelectMenu()) {
    if (interaction.customId === 'help_category') {
      const category = interaction.values[0];
      
      let categoryEmbed;
      
      if (category === 'server_commands') {
        categoryEmbed = new EmbedBuilder()
          .setTitle('🎮 Server Management Commands')
          .setColor(0x0099ff)
          .setDescription('Commands for creating and managing your servers:')
          .addFields(
            { name: '/create server', value: 'Create a new server with step-by-step setup', inline: false },
            { name: '/nest [nest_id]', value: 'View available nests and eggs', inline: false },
            { name: '/resources', value: 'View your resource inventory', inline: false },
            { name: '/shop', value: 'Buy server resources with coins', inline: false },
            { name: '₹create server', value: 'Prefix version of server creation', inline: false },
            { name: '₹nest [nest_id]', value: 'Prefix version of nest viewing', inline: false }
          )
          .addFields(
            { name: '💾 Server Specs (First Server)', value: '**RAM:** 3GB | **CPU:** 100% | **Disk:** 5GB', inline: false },
            { name: '💾 Additional Server Specs', value: '**RAM:** 1GB | **CPU:** 50% | **Disk:** 2GB', inline: false }
          );
      } else if (category === 'economy_commands') {
        categoryEmbed = new EmbedBuilder()
          .setTitle('💰 Economy System Commands')
          .setColor(0xffd700)
          .setDescription('Commands for earning and spending coins:')
          .addFields(
            { name: '/balance', value: 'Check your coin balance and stats', inline: false },
            { name: '/coinflip <amount> [choice]', value: 'Gamble coins with 40% win chance (4s cooldown)', inline: false },
            { name: '/leaderboard', value: 'View top 10 richest users', inline: false },
            { name: '/redeem <code>', value: 'Redeem codes for free coins', inline: false },
            { name: '₹balance', value: 'Prefix version of balance check', inline: false },
            { name: '₹coinflip <amount> [choice]', value: 'Prefix version of coinflip', inline: false }
          )
          .addFields(
            { name: '💰 Ways to Earn Coins', value: '• Invite users (200 coins each)\n• Redeem codes from owners\n• Coinflip gambling\n• Purchase with real money', inline: false }
          );
      } else if (category === 'admin_commands') {
        categoryEmbed = new EmbedBuilder()
          .setTitle('🛠️ Admin Commands')
          .setColor(0xff0000)
          .setDescription('Administrative commands (Admin only):')
          .addFields(
            { name: '/admin <add/remove/list> [user]', value: 'Manage bot administrators', inline: false },
            { name: '/coins <add/remove> <user> <amount>', value: 'Add or remove coins from users', inline: false },
            { name: '/blacklist <add/remove> <user>', value: 'Blacklist users from using the bot', inline: false },
            { name: '/createcode <code> <coins> <uses>', value: 'Create redeem codes for users', inline: false },
            { name: '/server show', value: 'View and manage all servers on panel', inline: false }
          )
          .addFields(
            { name: '👥 Current Admins', value: 'Core admins have permanent access and cannot be removed', inline: false }
          );
      } else if (category === 'general_info') {
        categoryEmbed = new EmbedBuilder()
          .setTitle('📋 General Information')
          .setColor(0x00ff99)
          .setDescription('Bot specifications and technical details:')
          .addFields(
            { name: '🔧 Tech Stack', value: '• **Discord.js v14** - Bot framework\n• **MongoDB** - Database storage\n• **Axios** - API requests\n• **Pterodactyl API** - Panel integration', inline: false },
            { name: '✨ Key Features', value: '• Step-by-step server creation\n• Resource shop & management\n• Advanced coin system\n• Server resource upgrades\n• Admin management tools', inline: false },
            { name: '📧 Account System', value: 'Email: `username@gmail.com`\nPassword: Auto-generated\nCredentials sent via DM', inline: false },
            { name: '👤 Created By', value: 'Shadow | BlazeNode IT Solutions', inline: false }
          );
      }
      
      await interaction.update({ embeds: [categoryEmbed], components: [] });
    }
    
    if (interaction.customId === 'admin_server_select') {
      if (!(await isAdmin(interaction.user.id))) {
        return interaction.reply({ content: 'You do not have permission to use this!', flags: 64 });
      }
      
      const serverId = interaction.values[0];
      
      try {
        const serverResponse = await axios.get(`${process.env.PTERODACTYL_URL}/api/application/servers/${serverId}`, {
          headers: {
            'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
            'Accept': 'application/json'
          }
        });
        
        const server = serverResponse.data.attributes;
        
        const serverManageEmbed = new EmbedBuilder()
          .setTitle(`🖥️ Server: ${server.name}`)
          .setColor(0xff6b35)
          .addFields(
            { name: '🆔 Server ID', value: `${server.id}`, inline: true },
            { name: '👤 User ID', value: `${server.user}`, inline: true },
            { name: '💾 RAM', value: `${server.limits.memory}MB`, inline: true },
            { name: '⚡ CPU', value: `${server.limits.cpu}%`, inline: true },
            { name: '💿 Disk', value: `${server.limits.disk}MB`, inline: true },
            { name: '📊 Status', value: server.suspended ? '❌ Suspended' : '✅ Active', inline: true }
          );
        
        const serverButtons = new ActionRowBuilder()
          .addComponents(
            new ButtonBuilder()
              .setCustomId(`delete_server_${serverId}`)
              .setLabel('Delete Server')
              .setStyle(ButtonStyle.Danger)
              .setEmoji('🗑️'),
            new ButtonBuilder()
              .setCustomId(`owner_info_${serverId}`)
              .setLabel('Owner Info')
              .setStyle(ButtonStyle.Primary)
              .setEmoji('👤')
          );
        
        await interaction.update({ embeds: [serverManageEmbed], components: [serverButtons] });
      } catch (error) {
        console.error('Server fetch error:', error.message);
        await interaction.reply({ content: 'Error fetching server details.', flags: 64 });
      }
    }
    
    if (interaction.customId === 'server_select') {
      const serverId = interaction.values[0];
      
      const serverEmbed = new EmbedBuilder()
        .setTitle('🖥️ Server Resource Management')
        .setColor(0x0099ff)
        .setDescription(`Selected Server ID: ${serverId}\n\nChoose which resource to add:`)
        .addFields(
          { name: '💾 RAM', value: 'Add RAM to your server', inline: true },
          { name: '⚡ CPU', value: 'Add CPU to your server', inline: true },
          { name: '💿 Disk', value: 'Add Disk to your server', inline: true },
          { name: '💾 Backups', value: 'Add backup slots', inline: true },
          { name: '🔌 Ports', value: 'Add additional ports', inline: true }
        );
      
      const resourceButtons1 = new ActionRowBuilder()
        .addComponents(
          new ButtonBuilder()
            .setCustomId('add_ram')
            .setLabel('Add RAM')
            .setStyle(ButtonStyle.Primary)
            .setEmoji('💾'),
          new ButtonBuilder()
            .setCustomId('add_cpu')
            .setLabel('Add CPU')
            .setStyle(ButtonStyle.Primary)
            .setEmoji('⚡'),
          new ButtonBuilder()
            .setCustomId('add_disk')
            .setLabel('Add Disk')
            .setStyle(ButtonStyle.Primary)
            .setEmoji('💿')
        );
      
      const resourceButtons2 = new ActionRowBuilder()
        .addComponents(
          new ButtonBuilder()
            .setCustomId('add_backups')
            .setLabel('Add Backups')
            .setStyle(ButtonStyle.Secondary)
            .setEmoji('💾'),
          new ButtonBuilder()
            .setCustomId('add_ports')
            .setLabel('Add Ports')
            .setStyle(ButtonStyle.Secondary)
            .setEmoji('🔌')
        );
      
      global.selectedServer = global.selectedServer || {};
      global.selectedServer[interaction.user.id] = serverId;
      
      await interaction.update({ embeds: [serverEmbed], components: [resourceButtons1, resourceButtons2] });
    }
  }
  
  if (interaction.isButton()) {
    const userId = interaction.user.id;
    
    if (interaction.customId === 'buy_resources') {
      const buyEmbed = new EmbedBuilder()
        .setTitle('🛒 Buy Resources')
        .setColor(0xffd700)
        .setDescription('Reply with the number of the item you want to buy:\n\n**1.** 💾 1GB RAM - 1,200 coins\n**2.** ⚡ 50% CPU - 1,000 coins\n**3.** 💿 1GB Disk - 800 coins\n**4.** 🖥️ Extra Server Slot - 1,000 coins\n**5.** 💾 1 Backup Slot - 1,000 coins\n**6.** 🔌 1 Additional Port - 1,000 coins')
        .setFooter({ text: 'Type the number (1-6) in chat' });
      
      await interaction.reply({ embeds: [buyEmbed], flags: 64 });
      
      global.userShopping = global.userShopping || {};
      global.userShopping[interaction.user.id] = { channelId: interaction.channelId, step: 'buying' };
    }
    
    if (interaction.customId === 'add_resource') {
      try {
        const user = await User.findOne({ discordId: interaction.user.id });
        if (!user || !user.hasServer) {
          return interaction.reply({ content: 'You need to have a server first!', flags: 64 });
        }
        
        const serverSelectEmbed = new EmbedBuilder()
          .setTitle('🖥️ Select Server')
          .setColor(0x0099ff)
          .setDescription('Choose which server to add resources to:')
          .addFields(
            { name: 'Your Server', value: `Server ID: ${user.serverId}`, inline: false }
          );
        
        const serverSelect = new ActionRowBuilder()
          .addComponents(
            new StringSelectMenuBuilder()
              .setCustomId('server_select')
              .setPlaceholder('Select your server')
              .addOptions({
                label: `${user.username}'s Server`,
                value: user.serverId,
                description: `Server ID: ${user.serverId}`
              })
          );
        
        await interaction.reply({ embeds: [serverSelectEmbed], components: [serverSelect], flags: 64 });
      } catch (error) {
        await interaction.reply({ content: 'Error loading servers.', flags: 64 });
      }
    }
    
    if (interaction.customId.startsWith('add_')) {
      const resourceType = interaction.customId.split('_')[1];
      const user = await User.findOne({ discordId: interaction.user.id });
      
      if (!user) {
        return interaction.reply({ content: 'User not found!', flags: 64 });
      }
      
      let availableAmount = 0;
      let resourceName = '';
      
      switch (resourceType) {
        case 'ram':
          availableAmount = user.resources.ram;
          resourceName = 'RAM (GB)';
          break;
        case 'cpu':
          availableAmount = user.resources.cpu;
          resourceName = 'CPU (%)';
          break;
        case 'disk':
          availableAmount = user.resources.disk;
          resourceName = 'Disk (GB)';
          break;
        case 'backups':
          availableAmount = user.resources.backups;
          resourceName = 'Backup Slots';
          break;
        case 'ports':
          availableAmount = user.resources.ports;
          resourceName = 'Additional Ports';
          break;
      }
      
      if (availableAmount === 0) {
        return interaction.reply({ content: `You don't have any ${resourceName} to add!`, flags: 64 });
      }
      
      const addEmbed = new EmbedBuilder()
        .setTitle(`➕ Add ${resourceName}`)
        .setColor(0x00ff99)
        .setDescription(`You have **${availableAmount}** ${resourceName} available.\n\nHow much do you want to add to your server?\n\n**Reply with the amount in chat.**`)
        .setFooter({ text: `Type a number between 1 and ${availableAmount}` });
      
      await interaction.reply({ embeds: [addEmbed], flags: 64 });
      
      global.userAddingResource = global.userAddingResource || {};
      global.userAddingResource[interaction.user.id] = {
        channelId: interaction.channelId,
        resourceType,
        serverId: global.selectedServer?.[interaction.user.id] || user.serverId,
        maxAmount: availableAmount
      };
    }
    
    if (interaction.customId === 'setup_nest') {
      try {
        await interaction.deferReply({ flags: 64 });
        const nests = await getNests();
        const nestEmbed = new EmbedBuilder()
          .setTitle('🗂️ Step 1: Select Your Nest')
          .setColor(0x0099ff)
          .setDescription('Choose a nest type for your server:\n\n' + 
            nests.map(nest => `**${nest.attributes.id}** - ${nest.attributes.name}`).join('\n') +
            '\n\n**Reply with the nest number you want to use.**')
          .setFooter({ text: 'Type the nest ID number in chat' });
        
        await interaction.editReply({ embeds: [nestEmbed] });
        
        // Store user state
        global.userSetup = global.userSetup || {};
        global.userSetup[userId] = { step: 'nest', channelId: interaction.channelId, messageId: interaction.message.id };
      } catch (error) {
        await interaction.editReply('Error fetching nests.');
      }
    }
    
    if (interaction.customId === 'setup_egg') {
      const userState = global.userSetup?.[userId];
      if (!userState?.selectedNest) {
        return interaction.reply({ content: 'Please select a nest first!', flags: 64 });
      }
      
      try {
        await interaction.deferReply({ flags: 64 });
        const eggs = await getEggs(userState.selectedNest);
        const eggEmbed = new EmbedBuilder()
          .setTitle(`🥚 Step 2: Select Your Egg (Nest ${userState.selectedNest})`)
          .setColor(0x00ff99)
          .setDescription('Choose an egg configuration:\n\n' + 
            eggs.map(egg => `**${egg.attributes.id}** - ${egg.attributes.name}`).join('\n') +
            '\n\n**Reply with the egg number you want to use.**')
          .setFooter({ text: 'Type the egg ID number in chat' });
        
        await interaction.editReply({ embeds: [eggEmbed] });
        userState.step = 'egg';
      } catch (error) {
        await interaction.editReply('Error fetching eggs.');
      }
    }
    
    if (interaction.customId === 'setup_create') {
      const userState = global.userSetup?.[userId];
      if (!userState?.selectedNest || !userState?.selectedEgg) {
        return interaction.reply({ content: 'Please complete all steps first!', flags: 64 });
      }
      
      await interaction.deferReply({ flags: 64 });
      
      try {
        const existingUser = await User.findOne({ discordId: userId });
        if (existingUser && existingUser.hasServer) {
          return interaction.editReply('You already have a server!');
        }
        
        const username = interaction.user.username;
        const email = `${username}@gmail.com`;
        const password = generatePassword();
        
        const pterodactylUser = await createPterodactylUser(username, email, password);
        
        // Check if user has server slots for additional servers
        let serverSpecs = {
          memory: 3072,
          cpu: 100,
          disk: 5120
        };
        
        const existingUserData = await User.findOne({ discordId: userId });
        if (existingUserData && existingUserData.hasServer && existingUserData.resources.serverSlots > 0) {
          // Use server slot and reduce specs for additional servers
          serverSpecs = {
            memory: 1024, // 1GB RAM
            cpu: 50,      // 50% CPU
            disk: 2048    // 2GB Disk
          };
          existingUserData.resources.serverSlots -= 1;
          await existingUserData.save();
        }
        
        const server = await createPterodactylServer(pterodactylUser.id, `${username}-server`, userState.selectedNest, userState.selectedEgg, serverSpecs);
        
        await User.findOneAndUpdate(
          { discordId: userId },
          {
            discordId: userId,
            username,
            email,
            password,
            serverId: server.id,
            hasServer: true,
            balance: 50,
            resources: {
              ram: 0,
              cpu: 0,
              disk: 0,
              serverSlots: 0,
              backups: 0,
              ports: 0
            }
          },
          { upsert: true }
        );
        
        const embed = new EmbedBuilder()
          .setTitle('🎮 Server Created Successfully!')
          .setColor(0x00ff00)
          .addFields(
            { name: '📧 Email', value: email, inline: true },
            { name: '🔑 Password', value: password, inline: true },
            { name: '🖥️ Server Name', value: server.name, inline: true },
            { name: '💾 RAM', value: `${Math.floor(serverSpecs.memory / 1024)}GB`, inline: true },
            { name: '💿 Disk', value: `${Math.floor(serverSpecs.disk / 1024)}GB`, inline: true },
            { name: '⚡ CPU', value: `${serverSpecs.cpu}%`, inline: true },
            { name: '🌐 Panel URL', value: 'https://panel.blazenode.site', inline: false },
            { name: '💰 Starting Balance', value: '50 coins', inline: true }
          )
          .setFooter({ text: 'Keep these credentials safe!' });
        
        await interaction.user.send({ embeds: [embed] });
        await interaction.editReply('✅ Server created successfully! Check your DMs for details.');
        
        // Send server creation notification to admin channel
        const notificationChannel = interaction.guild.channels.cache.get('1416664767900155995');
        if (notificationChannel) {
          const notificationEmbed = new EmbedBuilder()
            .setTitle('🎮 New Server Created')
            .setColor(0x00ff00)
            .addFields(
              { name: '👤 Owner', value: `<@${userId}> (${username})`, inline: true },
              { name: '📧 Email', value: email, inline: true },
              { name: '🖥️ Server Name', value: server.name, inline: true },
              { name: '🆔 Server ID', value: `${server.id}`, inline: true },
              { name: '💾 RAM', value: `${Math.floor(serverSpecs.memory / 1024)}GB`, inline: true },
              { name: '⚡ CPU', value: `${serverSpecs.cpu}%`, inline: true },
              { name: '💿 Disk', value: `${Math.floor(serverSpecs.disk / 1024)}GB`, inline: true },
              { name: '🗂️ Nest/Egg', value: `${userState.selectedNest}/${userState.selectedEgg}`, inline: true },
              { name: '📅 Created', value: new Date().toLocaleString(), inline: true }
            )
            .setFooter({ text: 'BlazeNode Panel Bot | Server Creation Log' })
            .setTimestamp();
          
          await notificationChannel.send({ embeds: [notificationEmbed] });
        }
        
        // Clean up user state
        delete global.userSetup[userId];
      } catch (error) {
        console.error('Server creation error:', error.message);
        await interaction.editReply(`Error: ${error.message}`);
      }
    }
    
    if (interaction.customId.startsWith('lb_')) {
      try {
        if (!interaction.replied && !interaction.deferred) {
          await interaction.deferUpdate();
        }
      } catch (error) {
        console.log('Leaderboard button error:', error.message);
      }
    }
    
    if (interaction.customId.startsWith('dice_')) {
      try {
        const amount = parseInt(interaction.customId.split('_')[1]);
        const user = await User.findOne({ discordId: interaction.user.id });
        
        const diceRoll = Math.floor(Math.random() * 100) + 1;
        const won = diceRoll > 50;
        
        if (won) {
          user.balance += amount;
          await user.save();
          
          const winEmbed = new EmbedBuilder()
            .setTitle('🎲 Dice Roll - You Won!')
            .setColor(0x00ff00)
            .setDescription(`You rolled **${diceRoll}**! (Need >50 to win)`)
            .addFields(
              { name: '💰 Won', value: `${amount} coins`, inline: true },
              { name: '💳 New Balance', value: `${user.balance} coins`, inline: true }
            );
          
          if (!interaction.replied && !interaction.deferred) {
            await interaction.update({ embeds: [winEmbed], components: [] });
          }
        } else {
          user.balance -= amount;
          await user.save();
          
          const loseEmbed = new EmbedBuilder()
            .setTitle('🎲 Dice Roll - You Lost!')
            .setColor(0xff0000)
            .setDescription(`You rolled **${diceRoll}**! (Need >50 to win)`)
            .addFields(
              { name: '💸 Lost', value: `${amount} coins`, inline: true },
              { name: '💳 New Balance', value: `${user.balance} coins`, inline: true }
            );
          
          if (!interaction.replied && !interaction.deferred) {
            await interaction.update({ embeds: [loseEmbed], components: [] });
          }
        }
      } catch (error) {
        console.log('Dice game error:', error.message);
      }
    }
    
    if (interaction.customId.startsWith('card_')) {
      try {
        const amount = parseInt(interaction.customId.split('_')[1]);
        const user = await User.findOne({ discordId: interaction.user.id });
        
        const cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];
        const suits = ['♥️', '♦️', '♣️', '♠️'];
        const userCard = cards[Math.floor(Math.random() * cards.length)];
        const userSuit = suits[Math.floor(Math.random() * suits.length)];
        const dealerCard = cards[Math.floor(Math.random() * cards.length)];
        const dealerSuit = suits[Math.floor(Math.random() * suits.length)];
        
        const cardValues = { 'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13 };
        const won = cardValues[userCard] > cardValues[dealerCard];
        
        if (won) {
          user.balance += amount;
          await user.save();
          
          const winEmbed = new EmbedBuilder()
            .setTitle('🃏 Card Draw - You Won!')
            .setColor(0x00ff00)
            .setDescription(`Your card: **${userCard}${userSuit}**\nDealer card: **${dealerCard}${dealerSuit}**`)
            .addFields(
              { name: '💰 Won', value: `${amount} coins`, inline: true },
              { name: '💳 New Balance', value: `${user.balance} coins`, inline: true }
            );
          
          if (!interaction.replied && !interaction.deferred) {
            await interaction.update({ embeds: [winEmbed], components: [] });
          }
        } else {
          user.balance -= amount;
          await user.save();
          
          const loseEmbed = new EmbedBuilder()
            .setTitle('🃏 Card Draw - You Lost!')
            .setColor(0xff0000)
            .setDescription(`Your card: **${userCard}${userSuit}**\nDealer card: **${dealerCard}${dealerSuit}**`)
            .addFields(
              { name: '💸 Lost', value: `${amount} coins`, inline: true },
              { name: '💳 New Balance', value: `${user.balance} coins`, inline: true }
            );
          
          if (!interaction.replied && !interaction.deferred) {
            await interaction.update({ embeds: [loseEmbed], components: [] });
          }
        }
      } catch (error) {
        console.log('Card game error:', error.message);
      }
    }
    
    if (interaction.customId.startsWith('slot_')) {
      try {
        const amount = parseInt(interaction.customId.split('_')[1]);
        const user = await User.findOne({ discordId: interaction.user.id });
        
        const symbols = ['🍒', '🍋', '🍇', '🔔', '💰', '⭐'];
        const slot1 = symbols[Math.floor(Math.random() * symbols.length)];
        const slot2 = symbols[Math.floor(Math.random() * symbols.length)];
        const slot3 = symbols[Math.floor(Math.random() * symbols.length)];
        
        const won = Math.random() < 0.5; // 50% chance
        
        if (won) {
          // Force a win by making all symbols match
          const winSymbol = symbols[Math.floor(Math.random() * symbols.length)];
          user.balance += amount * 2; // Slot machine pays 2x
          await user.save();
          
          const winEmbed = new EmbedBuilder()
            .setTitle('🍰 Slot Machine - JACKPOT!')
            .setColor(0x00ff00)
            .setDescription(`${winSymbol} ${winSymbol} ${winSymbol}\n\n**THREE OF A KIND!**`)
            .addFields(
              { name: '💰 Won', value: `${amount * 2} coins (2x multiplier!)`, inline: true },
              { name: '💳 New Balance', value: `${user.balance} coins`, inline: true }
            );
          
          if (!interaction.replied && !interaction.deferred) {
            await interaction.update({ embeds: [winEmbed], components: [] });
          }
        } else {
          user.balance -= amount;
          await user.save();
          
          const loseEmbed = new EmbedBuilder()
            .setTitle('🍰 Slot Machine - No Match!')
            .setColor(0xff0000)
            .setDescription(`${slot1} ${slot2} ${slot3}\n\n**Better luck next time!**`)
            .addFields(
              { name: '💸 Lost', value: `${amount} coins`, inline: true },
              { name: '💳 New Balance', value: `${user.balance} coins`, inline: true }
            );
          
          if (!interaction.replied && !interaction.deferred) {
            await interaction.update({ embeds: [loseEmbed], components: [] });
          }
        }
      } catch (error) {
        console.log('Slot game error:', error.message);
      }
    }
    
    if (interaction.customId.startsWith('buy_')) {
      if (interaction.customId === 'buy_custom') {
        const customEmbed = new EmbedBuilder()
          .setTitle('🎫 Custom Coins Purchase')
          .setColor(0x87CEEB)
          .setDescription('For custom coin amounts, please create a support ticket and our team will assist you with your purchase.')
          .addFields(
            { name: '📞 Contact', value: 'Create a ticket in the support channel', inline: true },
            { name: '💳 Payment', value: 'Multiple payment methods accepted', inline: true }
          );
        
        await interaction.reply({ embeds: [customEmbed], flags: 64 });
      } else {
        const [, coins, price] = interaction.customId.split('_');
        
        const purchaseEmbed = new EmbedBuilder()
          .setTitle('💰 Coin Purchase')
          .setColor(0x87CEEB)
          .setDescription(`You want to purchase **${coins} coins** for **₹${price}**`)
          .addFields(
            { name: '💳 Payment Methods', value: 'UPI, PayTM, PhonePe, Bank Transfer', inline: true },
            { name: '📞 Contact', value: 'Create a ticket for payment details', inline: true },
            { name: '⏱️ Processing', value: 'Coins added within 5-10 minutes', inline: true }
          )
          .setFooter({ text: 'Create a support ticket to complete your purchase' });
        
        await interaction.reply({ embeds: [purchaseEmbed], flags: 64 });
      }
    }
    
    if (interaction.customId.startsWith('delete_server_')) {
      if (!(await isAdmin(interaction.user.id))) {
        return interaction.reply({ content: 'You do not have permission to use this!', flags: 64 });
      }
      
      const serverId = interaction.customId.split('_')[2];
      
      try {
        await axios.delete(`${process.env.PTERODACTYL_URL}/api/application/servers/${serverId}`, {
          headers: {
            'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
            'Accept': 'application/json'
          }
        });
        
        const deleteEmbed = new EmbedBuilder()
          .setTitle('✅ Server Deleted')
          .setColor(0x00ff00)
          .setDescription(`Server ID ${serverId} has been successfully deleted from the panel.`);
        
        await interaction.update({ embeds: [deleteEmbed], components: [] });
      } catch (error) {
        console.error('Server delete error:', error.message);
        await interaction.reply({ content: 'Error deleting server.', flags: 64 });
      }
    }
    
    if (interaction.customId.startsWith('owner_info_')) {
      if (!(await isAdmin(interaction.user.id))) {
        return interaction.reply({ content: 'You do not have permission to use this!', flags: 64 });
      }
      
      const serverId = interaction.customId.split('_')[2];
      
      try {
        const serverResponse = await axios.get(`${process.env.PTERODACTYL_URL}/api/application/servers/${serverId}`, {
          headers: {
            'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
            'Accept': 'application/json'
          }
        });
        
        const server = serverResponse.data.attributes;
        
        const userResponse = await axios.get(`${process.env.PTERODACTYL_URL}/api/application/users/${server.user}`, {
          headers: {
            'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
            'Accept': 'application/json'
          }
        });
        
        const pterodactylUser = userResponse.data.attributes;
        const dbUser = await User.findOne({ email: pterodactylUser.email });
        
        const ownerEmbed = new EmbedBuilder()
          .setTitle(`👤 Owner Information - Server ${serverId}`)
          .setColor(0x0099ff)
          .addFields(
            { name: '💬 Discord User', value: dbUser ? `<@${dbUser.discordId}>` : 'Not found', inline: true },
            { name: '👤 Username', value: pterodactylUser.username, inline: true },
            { name: '📧 Email', value: pterodactylUser.email, inline: true },
            { name: '🆔 Panel User ID', value: `${pterodactylUser.id}`, inline: true },
            { name: '💰 Balance', value: dbUser ? `${dbUser.balance} coins` : 'N/A', inline: true },
            { name: '📅 Created', value: new Date(pterodactylUser.created_at).toLocaleDateString(), inline: true }
          );
        
        await interaction.reply({ embeds: [ownerEmbed], flags: 64 });
      } catch (error) {
        console.error('Owner info error:', error.message);
        await interaction.reply({ content: 'Error fetching owner information.', flags: 64 });
      }
    }
    
    if (interaction.customId.startsWith('eggs_')) {
      const nestId = interaction.customId.split('_')[1];
      
      try {
        await interaction.deferReply({ flags: 64 });
        const eggs = await getEggs(nestId);
        const eggEmbed = new EmbedBuilder()
          .setTitle(`🥚 Eggs for Nest ${nestId}`)
          .setColor(0x00ff99)
          .setDescription(eggs.map(egg => `**${egg.attributes.id}** - ${egg.attributes.name}`).join('\n'));
        
        await interaction.editReply({ embeds: [eggEmbed] });
      } catch (error) {
        console.error('Button eggs error:', error.message);
        try {
          if (!interaction.replied && !interaction.deferred) {
            await interaction.reply({ content: `Error: ${error.message}`, flags: 64 });
          } else {
            await interaction.editReply(`Error: ${error.message}`);
          }
        } catch (e) {
          console.error('Failed to send error message:', e.message);
        }
      }
    }
    return;
  }
  
  if (!interaction.isCommand()) return;

  if (interaction.commandName === 'create') {
    const action = interaction.options.getString('server');
    if (action !== 'server') return;
    
    try {
      const existingUser = await User.findOne({ discordId: interaction.user.id });
      if (existingUser && existingUser.hasServer) {
        return interaction.reply({ content: 'You already have a server!', flags: 64 });
      }
      
      const setupEmbed = new EmbedBuilder()
        .setTitle('🎮 Server Creation Setup')
        .setColor(0x0099ff)
        .setDescription('Follow the steps below to create your server:')
        .addFields(
          { name: 'Step 1', value: 'Click **Select Nest** to choose your server type', inline: false },
          { name: 'Step 2', value: 'Click **Select Egg** to choose your server configuration', inline: false },
          { name: 'Step 3', value: 'Click **Create Server** to finalize creation', inline: false },
          { name: '💾 Server Specs', value: '**RAM:** 3GB | **CPU:** 100% | **Disk:** 5GB', inline: false }
        )
        .setFooter({ text: 'Your credentials will be sent via DM after creation' });
      
      const setupButtons = new ActionRowBuilder()
        .addComponents(
          new ButtonBuilder()
            .setCustomId('setup_nest')
            .setLabel('Step 1: Select Nest')
            .setStyle(ButtonStyle.Primary)
            .setEmoji('🗂️'),
          new ButtonBuilder()
            .setCustomId('setup_egg')
            .setLabel('Step 2: Select Egg')
            .setStyle(ButtonStyle.Secondary)
            .setEmoji('🥚')
            .setDisabled(true),
          new ButtonBuilder()
            .setCustomId('setup_create')
            .setLabel('Step 3: Create Server')
            .setStyle(ButtonStyle.Success)
            .setEmoji('✨')
            .setDisabled(true)
        );
      
      await interaction.reply({ embeds: [setupEmbed], components: [setupButtons] });
    } catch (error) {
      await interaction.reply({ content: 'Error starting server creation.', flags: 64 });
    }
  }

  if (interaction.commandName === 'shop') {
    const shopEmbed = new EmbedBuilder()
      .setTitle('🛒 BlazeNode Resource Shop')
      .setColor(0xffd700)
      .setDescription('Purchase resources to upgrade your servers!')
      .addFields(
        { name: '💾 1GB RAM', value: '**Price:** 1,200 coins', inline: true },
        { name: '⚡ 50% CPU', value: '**Price:** 1,000 coins', inline: true },
        { name: '💿 1GB Disk', value: '**Price:** 800 coins', inline: true },
        { name: '🖥️ Extra Server Slot', value: '**Price:** 1,000 coins', inline: true },
        { name: '💾 1 Backup Slot', value: '**Price:** 1,000 coins', inline: true },
        { name: '🔌 1 Additional Port', value: '**Price:** 1,000 coins', inline: true }
      )
      .setFooter({ text: 'Click Buy Resources to purchase items' });
    
    const shopButton = new ActionRowBuilder()
      .addComponents(
        new ButtonBuilder()
          .setCustomId('buy_resources')
          .setLabel('Buy Resources')
          .setStyle(ButtonStyle.Primary)
          .setEmoji('🛒')
      );
    
    await interaction.reply({ embeds: [shopEmbed], components: [shopButton] });
  }

  if (interaction.commandName === 'resources') {
    try {
      const user = await User.findOne({ discordId: interaction.user.id });
      if (!user) {
        return interaction.reply({ content: 'You need to create a server first!', flags: 64 });
      }
      
      const resourceEmbed = new EmbedBuilder()
        .setTitle('📦 Your Resource Inventory')
        .setColor(0x00ff99)
        .addFields(
          { name: '💾 RAM', value: `${user.resources.ram} GB`, inline: true },
          { name: '⚡ CPU', value: `${user.resources.cpu}%`, inline: true },
          { name: '💿 Disk', value: `${user.resources.disk} GB`, inline: true },
          { name: '🖥️ Server Slots', value: `${user.resources.serverSlots}`, inline: true },
          { name: '💾 Backups', value: `${user.resources.backups}`, inline: true },
          { name: '🔌 Ports', value: `${user.resources.ports}`, inline: true },
          { name: '💰 Balance', value: `${user.balance} coins`, inline: true },
          { name: '📊 Total Value', value: `${(user.resources.ram * 1200) + (user.resources.cpu * 20) + (user.resources.disk * 800) + (user.resources.serverSlots * 1000) + (user.resources.backups * 1000) + (user.resources.ports * 1000)} coins`, inline: true }
        )
        .setFooter({ text: 'Use resources to upgrade your servers' });
      
      const addResourceButton = new ActionRowBuilder()
        .addComponents(
          new ButtonBuilder()
            .setCustomId('add_resource')
            .setLabel('Add Resource to Server')
            .setStyle(ButtonStyle.Success)
            .setEmoji('➕')
        );
      
      await interaction.reply({ embeds: [resourceEmbed], components: [addResourceButton] });
    } catch (error) {
      await interaction.reply({ content: 'Error fetching resources.', flags: 64 });
    }
  }

  if (interaction.commandName === 'balance') {
    try {
      const user = await User.findOne({ discordId: interaction.user.id });
      if (!user) {
        return interaction.reply({ content: 'You need to create a server first!', flags: 64 });
      }
      
      const level = Math.floor(user.balance / 1000) + 1;
      const progressBar = '█'.repeat(Math.floor((user.balance % 1000) / 100)) + '░'.repeat(10 - Math.floor((user.balance % 1000) / 100));
      
      const balanceEmbed = new EmbedBuilder()
        .setTitle('💰 BlazeNode Wallet')
        .setColor(0x00d4ff)
        .setAuthor({ 
          name: `${user.username}'s Profile`, 
          iconURL: interaction.user.displayAvatarURL({ dynamic: true }) 
        })
        .setThumbnail('https://cdn.discordapp.com/emojis/741395532728041492.gif')
        .addFields(
          { 
            name: '💰 Current Balance', 
            value: `\`\`\`fix\n${user.balance.toLocaleString()} Coins\`\`\``, 
            inline: true 
          },
          { 
            name: '🏆 Level', 
            value: `\`\`\`yaml\nLevel ${level}\`\`\``, 
            inline: true 
          },
          { 
            name: '📈 Progress', 
            value: `\`\`\`[${progressBar}] ${user.balance % 1000}/1000\`\`\``, 
            inline: false 
          },
          { 
            name: '🎰 Gambling', 
            value: '• `/coinflip` - 50% win chance\n• `/gamble` - Multiple games', 
            inline: true 
          },
          { 
            name: '🛒 Shopping', 
            value: '• `/shop` - Buy resources\n• `/resources` - View inventory', 
            inline: true 
          },
          { 
            name: '📊 Stats', 
            value: `• **Rank:** #${await User.countDocuments({ balance: { $gt: user.balance } }) + 1}\n• **Total Value:** ${((user.resources.ram * 1200) + (user.resources.cpu * 20) + (user.resources.disk * 800) + (user.resources.serverSlots * 1000) + (user.resources.backups * 1000) + (user.resources.ports * 1000) + user.balance).toLocaleString()} coins`, 
            inline: true 
          }
        )
        .setFooter({ 
          text: 'BlazeNode Panel Bot • Made by Shadow', 
          iconURL: 'https://cdn.discordapp.com/emojis/852881450667081728.gif' 
        })
        .setTimestamp();
      
      await interaction.reply({ embeds: [balanceEmbed] });
    } catch (error) {
      await interaction.reply({ content: 'Error fetching balance.', flags: 64 });
    }
  }

  if (interaction.commandName === 'coinflip') {
    const amount = interaction.options.getInteger('amount');
    const choice = interaction.options.getString('choice') || (Math.random() < 0.5 ? 'heads' : 'tails');
    
    try {
      const user = await User.findOne({ discordId: interaction.user.id });
      if (!user) {
        return interaction.reply({ content: 'You need to create a server first!', flags: 64 });
      }
      
      if (user.balance < amount) {
        return interaction.reply({ content: `You don't have enough coins! You have ${user.balance} coins.`, flags: 64 });
      }
      
      // Check cooldown
      const cooldownKey = interaction.user.id;
      const now = Date.now();
      const cooldownAmount = 4000; // 4 seconds
      
      if (coinflipCooldowns.has(cooldownKey)) {
        const expirationTime = coinflipCooldowns.get(cooldownKey) + cooldownAmount;
        if (now < expirationTime) {
          const timeLeft = (expirationTime - now) / 1000;
          return interaction.reply({ content: `Please wait ${timeLeft.toFixed(1)} more seconds before using coinflip again.`, flags: 64 });
        }
      }
      
      coinflipCooldowns.set(cooldownKey, now);
      
      const coinResult = Math.random() < 0.5 ? 'heads' : 'tails';
      const won = choice === coinResult && Math.random() < 0.4; // 40% win chance
      
      if (won) {
        user.balance += amount;
        await user.save();
        
        const winEmbed = new EmbedBuilder()
          .setTitle('🎉 You Won!')
          .setColor(0x00ff00)
          .setDescription(`The coin landed on **${coinResult}**! You chose **${choice}**`)
          .addFields(
            { name: '💰 Won', value: `${amount} coins`, inline: true },
            { name: '💳 New Balance', value: `${user.balance} coins`, inline: true }
          );
        
        await interaction.reply({ embeds: [winEmbed] });
      } else {
        user.balance -= amount;
        await user.save();
        
        const loseEmbed = new EmbedBuilder()
          .setTitle('😢 You Lost!')
          .setColor(0xff0000)
          .setDescription(`The coin landed on **${coinResult}**! You chose **${choice}**`)
          .addFields(
            { name: '💸 Lost', value: `${amount} coins`, inline: true },
            { name: '💳 New Balance', value: `${user.balance} coins`, inline: true }
          );
        
        await interaction.reply({ embeds: [loseEmbed] });
      }
    } catch (error) {
      await interaction.reply({ content: 'Error processing coinflip.', flags: 64 });
    }
  }

  if (interaction.commandName === 'leaderboard') {
    try {
      const topUsers = await User.find({}).sort({ balance: -1 }).limit(10);
      
      if (topUsers.length === 0) {
        return interaction.reply({ content: 'No users found!', flags: 64 });
      }
      
      const leaderboardEmbed = new EmbedBuilder()
        .setTitle('🏆 Coin Leaderboard - Top 10')
        .setColor(0xffd700)
        .setDescription(topUsers.map((user, index) => {
          const medals = ['🥇', '🥈', '🥉', '💫', '✨'];
          const medal = medals[index] || '🔹';
          return `${medal} **${index + 1}.** ${user.username} - ${user.balance} coins`;
        }).join('\n'))
        .setFooter({ text: 'Keep earning coins to climb the leaderboard!' })
        .setTimestamp();
      
      const reactionButtons = new ActionRowBuilder()
        .addComponents(
          new ButtonBuilder()
            .setCustomId('lb_fire')
            .setEmoji('🔥')
            .setStyle(ButtonStyle.Secondary),
          new ButtonBuilder()
            .setCustomId('lb_crown')
            .setEmoji('👑')
            .setStyle(ButtonStyle.Secondary),
          new ButtonBuilder()
            .setCustomId('lb_money')
            .setEmoji('💰')
            .setStyle(ButtonStyle.Secondary),
          new ButtonBuilder()
            .setCustomId('lb_star')
            .setEmoji('⭐')
            .setStyle(ButtonStyle.Secondary),
          new ButtonBuilder()
            .setCustomId('lb_gem')
            .setEmoji('💎')
            .setStyle(ButtonStyle.Secondary)
        );
      
      await interaction.reply({ embeds: [leaderboardEmbed], components: [reactionButtons] });
    } catch (error) {
      await interaction.reply({ content: 'Error fetching leaderboard.', flags: 64 });
    }
  }



  if (interaction.commandName === 'redeem') {
    const code = interaction.options.getString('code');
    
    try {
      const redeemCode = await RedeemCode.findOne({ code });
      if (!redeemCode) {
        return interaction.reply({ content: 'Invalid redeem code!', flags: 64 });
      }
      
      if (redeemCode.currentUses >= redeemCode.maxUses) {
        return interaction.reply({ content: 'This code has reached its usage limit!', flags: 64 });
      }
      
      if (redeemCode.usedBy.includes(interaction.user.id)) {
        return interaction.reply({ content: 'You have already used this code!', flags: 64 });
      }
      
      const user = await User.findOne({ discordId: interaction.user.id });
      if (!user) {
        return interaction.reply({ content: 'You need to create a server first!', flags: 64 });
      }
      
      user.balance += redeemCode.coins;
      await user.save();
      
      // Update user roles based on new balance
      await updateUserRoles(user, interaction.guild, interaction.user.id);
      
      redeemCode.currentUses += 1;
      redeemCode.usedBy.push(interaction.user.id);
      await redeemCode.save();
      
      const redeemEmbed = new EmbedBuilder()
        .setTitle('✅ Code Redeemed Successfully!')
        .setColor(0x00ff00)
        .addFields(
          { name: '🎁 Code', value: code, inline: true },
          { name: '💰 Coins Received', value: `${redeemCode.coins}`, inline: true },
          { name: '💳 New Balance', value: `${user.balance}`, inline: true }
        );
      
      await interaction.reply({ embeds: [redeemEmbed] });
    } catch (error) {
      await interaction.reply({ content: 'Error redeeming code.', flags: 64 });
    }
  }

  if (interaction.commandName === 'admin') {
    if (!ADMIN_IDS.includes(interaction.user.id) && !(await isAdmin(interaction.user.id))) {
      return interaction.reply({ content: 'You do not have permission to use this command!', flags: 64 });
    }
    
    const action = interaction.options.getString('action');
    const targetUser = interaction.options.getUser('user');
    
    if (action === 'add') {
      if (!targetUser) {
        return interaction.reply({ content: 'Please specify a user to add as admin!', flags: 64 });
      }
      
      const existingAdmin = await Admin.findOne({ discordId: targetUser.id });
      if (existingAdmin) {
        return interaction.reply({ content: 'This user is already an admin!', flags: 64 });
      }
      
      const newAdmin = new Admin({
        discordId: targetUser.id,
        username: targetUser.username,
        addedBy: interaction.user.id
      });
      
      await newAdmin.save();
      
      const addEmbed = new EmbedBuilder()
        .setTitle('✅ Admin Added')
        .setColor(0x00ff00)
        .setDescription(`${targetUser.username} has been added as an admin!`);
      
      await interaction.reply({ embeds: [addEmbed] });
    }
    
    if (action === 'remove') {
      if (!targetUser) {
        return interaction.reply({ content: 'Please specify a user to remove from admin!', flags: 64 });
      }
      
      if (ADMIN_IDS.includes(targetUser.id)) {
        return interaction.reply({ content: 'Cannot remove core admins!', flags: 64 });
      }
      
      const admin = await Admin.findOneAndDelete({ discordId: targetUser.id });
      if (!admin) {
        return interaction.reply({ content: 'This user is not an admin!', flags: 64 });
      }
      
      const removeEmbed = new EmbedBuilder()
        .setTitle('❌ Admin Removed')
        .setColor(0xff0000)
        .setDescription(`${targetUser.username} has been removed from admin!`);
      
      await interaction.reply({ embeds: [removeEmbed] });
    }
    
    if (action === 'list') {
      const admins = await Admin.find({});
      const adminList = admins.map(admin => `<@${admin.discordId}> (${admin.username})`).join('\n');
      
      const listEmbed = new EmbedBuilder()
        .setTitle('👑 Bot Admins')
        .setColor(0x0099ff)
        .setDescription(`**Core Admins:** <@${ADMIN_IDS.join('>, <@')}>\n\n**Added Admins:**\n${adminList || 'No additional admins added'}`);
      
      await interaction.reply({ embeds: [listEmbed] });
    }
  }

  if (interaction.commandName === 'coins') {
    if (!(await isAdmin(interaction.user.id))) {
      return interaction.reply({ content: 'You do not have permission to use this command!', flags: 64 });
    }
    
    const action = interaction.options.getString('action');
    const targetUser = interaction.options.getUser('user');
    const amount = interaction.options.getInteger('amount');
    
    try {
      const user = await User.findOne({ discordId: targetUser.id });
      if (!user) {
        return interaction.reply({ content: 'User not found in database!', flags: 64 });
      }
      
      if (action === 'add') {
        user.balance += amount;
        await user.save();
        
        // Update user roles based on new balance
        await updateUserRoles(user, interaction.guild, targetUser.id);
        
        const addEmbed = new EmbedBuilder()
          .setTitle('✅ Coins Added')
          .setColor(0x00ff00)
          .setDescription(`Added **${amount}** coins to ${targetUser.username}`);
        
        await interaction.reply({ embeds: [addEmbed] });
      }
      
      if (action === 'remove') {
        user.balance = Math.max(0, user.balance - amount);
        await user.save();
        
        // Update user roles based on new balance
        await updateUserRoles(user, interaction.guild, targetUser.id);
        
        const removeEmbed = new EmbedBuilder()
          .setTitle('❌ Coins Removed')
          .setColor(0xff0000)
          .setDescription(`Removed **${amount}** coins from ${targetUser.username}`);
        
        await interaction.reply({ embeds: [removeEmbed] });
      }
    } catch (error) {
      await interaction.reply({ content: 'Error managing coins.', flags: 64 });
    }
  }

  if (interaction.commandName === 'blacklist') {
    if (!(await isAdmin(interaction.user.id))) {
      return interaction.reply({ content: 'You do not have permission to use this command!', flags: 64 });
    }
    
    const action = interaction.options.getString('action');
    const targetUser = interaction.options.getUser('user');
    
    if (action === 'add') {
      const existingBlacklist = await Blacklist.findOne({ discordId: targetUser.id });
      if (existingBlacklist) {
        return interaction.reply({ content: 'This user is already blacklisted!', flags: 64 });
      }
      
      const blacklist = new Blacklist({
        discordId: targetUser.id,
        username: targetUser.username,
        blacklistedBy: interaction.user.id
      });
      
      await blacklist.save();
      
      const blacklistEmbed = new EmbedBuilder()
        .setTitle('❌ User Blacklisted')
        .setColor(0xff0000)
        .setDescription(`${targetUser.username} has been blacklisted from using the bot!`);
      
      await interaction.reply({ embeds: [blacklistEmbed] });
    }
    
    if (action === 'remove') {
      const blacklist = await Blacklist.findOneAndDelete({ discordId: targetUser.id });
      if (!blacklist) {
        return interaction.reply({ content: 'This user is not blacklisted!', flags: 64 });
      }
      
      const unblacklistEmbed = new EmbedBuilder()
        .setTitle('✅ User Unblacklisted')
        .setColor(0x00ff00)
        .setDescription(`${targetUser.username} has been removed from the blacklist!`);
      
      await interaction.reply({ embeds: [unblacklistEmbed] });
    }
  }

  if (interaction.commandName === 'createcode') {
    if (!(await isAdmin(interaction.user.id))) {
      return interaction.reply({ content: 'You do not have permission to use this command!', flags: 64 });
    }
    
    const code = interaction.options.getString('code');
    const coins = interaction.options.getInteger('coins');
    const uses = interaction.options.getInteger('uses');
    
    try {
      const existingCode = await RedeemCode.findOne({ code });
      if (existingCode) {
        return interaction.reply({ content: 'This code already exists!', flags: 64 });
      }
      
      const redeemCode = new RedeemCode({
        code,
        coins,
        maxUses: uses,
        createdBy: interaction.user.id
      });
      
      await redeemCode.save();
      
      const codeEmbed = new EmbedBuilder()
        .setTitle('✅ Redeem Code Created')
        .setColor(0x00ff00)
        .addFields(
          { name: '🎁 Code', value: code, inline: true },
          { name: '💰 Coins', value: `${coins}`, inline: true },
          { name: '👥 Max Uses', value: `${uses}`, inline: true }
        );
      
      await interaction.reply({ embeds: [codeEmbed] });
    } catch (error) {
      await interaction.reply({ content: 'Error creating code.', flags: 64 });
    }
  }

  if (interaction.commandName === 'server') {
    if (!(await isAdmin(interaction.user.id))) {
      return interaction.reply({ content: 'You do not have permission to use this command!', flags: 64 });
    }
    
    const action = interaction.options.getString('action');
    
    if (action === 'show') {
      try {
        await interaction.deferReply({ flags: 64 });
        
        const serversResponse = await axios.get(`${process.env.PTERODACTYL_URL}/api/application/servers`, {
          headers: {
            'Authorization': `Bearer ${process.env.PTERODACTYL_API_KEY}`,
            'Accept': 'application/json'
          }
        });
        
        const servers = serversResponse.data.data;
        
        if (servers.length === 0) {
          return interaction.editReply('No servers found on the panel.');
        }
        
        const serverEmbed = new EmbedBuilder()
          .setTitle('🖥️ Server Management')
          .setColor(0x0099ff)
          .setDescription('Select a server from the dropdown to manage:')
          .addFields(
            { name: '📊 Total Servers', value: `${servers.length}`, inline: true },
            { name: '🔧 Actions Available', value: 'Delete Server, Owner Info', inline: true }
          );
        
        const serverOptions = servers.slice(0, 25).map(server => ({
          label: server.attributes.name,
          value: server.attributes.id.toString(),
          description: `ID: ${server.attributes.id} | User: ${server.attributes.user}`
        }));
        
        const serverSelect = new ActionRowBuilder()
          .addComponents(
            new StringSelectMenuBuilder()
              .setCustomId('admin_server_select')
              .setPlaceholder('Select a server to manage')
              .addOptions(serverOptions)
          );
        
        await interaction.editReply({ embeds: [serverEmbed], components: [serverSelect] });
      } catch (error) {
        console.error('Server list error:', error.message);
        await interaction.editReply('Error fetching servers from panel.');
      }
    }
  }

  if (interaction.commandName === 'chat') {
    if (!(await isAdmin(interaction.user.id))) {
      return interaction.reply({ content: 'You do not have permission to use this command!', flags: 64 });
    }
    
    const action = interaction.options.getString('action');
    
    if (action === 'on') {
      chatCoinsEnabled = true;
      
      const onEmbed = new EmbedBuilder()
        .setTitle('✅ Chat Coins Enabled')
        .setColor(0x00ff00)
        .setDescription('Users will now earn 1 coin per 2 messages in the designated channel.')
        .addFields(
          { name: '📍 Channel', value: `<#${CHAT_CHANNEL_ID}>`, inline: true },
          { name: '💰 Reward', value: '1 coin per 2 messages', inline: true }
        );
      
      await interaction.reply({ embeds: [onEmbed] });
    }
    
    if (action === 'off') {
      chatCoinsEnabled = false;
      
      const offEmbed = new EmbedBuilder()
        .setTitle('❌ Chat Coins Disabled')
        .setColor(0xff0000)
        .setDescription('Users will no longer earn coins from chatting.');
      
      await interaction.reply({ embeds: [offEmbed] });
    }
    
    if (action === 'status') {
      const statusEmbed = new EmbedBuilder()
        .setTitle('📊 Chat Coins Status')
        .setColor(chatCoinsEnabled ? 0x00ff00 : 0xff0000)
        .addFields(
          { name: '🔄 Status', value: chatCoinsEnabled ? '✅ Enabled' : '❌ Disabled', inline: true },
          { name: '📍 Channel', value: `<#${CHAT_CHANNEL_ID}>`, inline: true },
          { name: '💰 Reward Rate', value: '1 coin per 2 messages', inline: true },
          { name: '👥 Active Users', value: `${userMessageCounts.size} users tracking`, inline: true }
        )
        .setTimestamp();
      
      await interaction.reply({ embeds: [statusEmbed] });
    }
  }

  if (interaction.commandName === 'help') {
    const helpEmbed = new EmbedBuilder()
      .setTitle('🤖 BlazeNode Panel Bot - Help')
      .setColor(0x00ff00)
      .setDescription('Complete Discord bot for Pterodactyl panel management\n\nSelect a category below to view specific commands:')
      .addFields(
        { name: '🎮 Server Management', value: 'Commands for creating and managing servers', inline: true },
        { name: '💰 Economy System', value: 'Coin earning, gambling, and shopping', inline: true },
        { name: '🛠️ Admin Commands', value: 'Administrative tools and management', inline: true }
      )
      .setFooter({ text: 'BlazeNode Panel Bot | Made by Shadow' })
      .setTimestamp();
    
    const helpSelect = new ActionRowBuilder()
      .addComponents(
        new StringSelectMenuBuilder()
          .setCustomId('help_category')
          .setPlaceholder('Select a command category')
          .addOptions(
            {
              label: '🎮 Server Management',
              value: 'server_commands',
              description: 'Server creation and resource management'
            },
            {
              label: '💰 Economy System',
              value: 'economy_commands',
              description: 'Coins, gambling, and shopping'
            },
            {
              label: '🛠️ Admin Commands',
              value: 'admin_commands',
              description: 'Administrative tools (Admin only)'
            },
            {
              label: '📋 General Info',
              value: 'general_info',
              description: 'Bot information and specifications'
            }
          )
      );
    
    await interaction.reply({ embeds: [helpEmbed], components: [helpSelect] });
  }

  if (interaction.commandName === 'nest') {
    const nestId = interaction.options.getString('nest');
    await interaction.deferReply();

    try {
      if (!nestId) {
        const nests = await getNests();
        const nestEmbed = new EmbedBuilder()
          .setTitle('🗂️ Available Nests')
          .setColor(0x0099ff)
          .setDescription(nests.map(nest => `**${nest.attributes.id}** - ${nest.attributes.name}`).join('\n'));
        
        const buttons = [];
        for (let i = 0; i < Math.min(nests.length, 5); i++) {
          buttons.push(
            new ButtonBuilder()
              .setCustomId(`eggs_${nests[i].attributes.id}`)
              .setLabel(`Eggs for ${nests[i].attributes.name}`)
              .setStyle(ButtonStyle.Primary)
              .setEmoji('🥚')
          );
        }
        
        const rows = [];
        for (let i = 0; i < buttons.length; i += 5) {
          rows.push(new ActionRowBuilder().addComponents(buttons.slice(i, i + 5)));
        }
        
        await interaction.editReply({ embeds: [nestEmbed], components: rows });
      } else {
        const eggs = await getEggs(nestId);
        const eggEmbed = new EmbedBuilder()
          .setTitle(`🥚 Eggs for Nest ${nestId}`)
          .setColor(0x00ff99)
          .setDescription(eggs.map(egg => `**${egg.attributes.id}** - ${egg.attributes.name}`).join('\n'));
        
        await interaction.editReply({ embeds: [eggEmbed] });
      }
    } catch (error) {
      console.error('Nest command error:', error.message);
      await interaction.editReply(`Error: ${error.message}`);
    }
  }
  } catch (error) {
    console.error('Interaction error:', error);
    try {
      if (!interaction.replied && !interaction.deferred) {
        await interaction.reply({ content: 'An error occurred while processing your request.', flags: 64 });
      }
    } catch (e) {
      console.error('Failed to send error message:', e);
    }
  }
});

process.on('unhandledRejection', (reason, promise) => {
  console.log('Unhandled Rejection at:', promise, 'reason:', reason);
});

process.on('uncaughtException', (err) => {
  console.log('Uncaught Exception thrown:', err);
});

client.on('error', (error) => {
  console.error('Discord client error:', error);
});

client.login(process.env.BOT_TOKEN);