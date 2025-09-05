import re

class EmojiHandler:
    def __init__(self):
        self.emoji_map = {
            # Basic emojis
            ':smile:': '😊',
            ':grin:': '😁',
            ':joy:': '😂',
            ':heart:': '❤️',
            ':fire:': '🔥',
            ':star:': '⭐',
            ':thumbsup:': '👍',
            ':thumbsdown:': '👎',
            ':clap:': '👏',
            ':wave:': '👋',
            ':eyes:': '👀',
            ':thinking:': '🤔',
            ':shrug:': '🤷',
            ':facepalm:': '🤦',
            ':ok_hand:': '👌',
            ':point_right:': '👉',
            ':point_left:': '👈',
            ':point_up:': '👆',
            ':point_down:': '👇',
            
            # Discord/Gaming emojis
            ':discord:': '<:discord:314003252830011395>',
            ':online:': '<:online:313956277808005120>',
            ':idle:': '<:idle:313956277220802560>',
            ':dnd:': '<:dnd:313956276893646850>',
            ':offline:': '<:offline:313956277237710868>',
            ':streaming:': '<:streaming:313956277132853248>',
            
            # Utility emojis
            ':check:': '✅',
            ':x:': '❌',
            ':warning:': '⚠️',
            ':info:': 'ℹ️',
            ':question:': '❓',
            ':exclamation:': '❗',
            ':white_check_mark:': '✅',
            ':negative_squared_cross_mark:': '❎',
            ':heavy_check_mark:': '✔️',
            ':heavy_multiplication_x:': '✖️',
            
            # Numbers
            ':one:': '1️⃣',
            ':two:': '2️⃣',
            ':three:': '3️⃣',
            ':four:': '4️⃣',
            ':five:': '5️⃣',
            ':six:': '6️⃣',
            ':seven:': '7️⃣',
            ':eight:': '8️⃣',
            ':nine:': '9️⃣',
            ':ten:': '🔟',
            
            # Arrows
            ':arrow_up:': '⬆️',
            ':arrow_down:': '⬇️',
            ':arrow_left:': '⬅️',
            ':arrow_right:': '➡️',
            ':arrow_up_small:': '🔼',
            ':arrow_down_small:': '🔽',
            
            # Music
            ':musical_note:': '🎵',
            ':notes:': '🎶',
            ':microphone:': '🎤',
            ':headphones:': '🎧',
            ':speaker:': '🔊',
            ':mute:': '🔇',
            ':loud_sound:': '🔊',
            
            # Moderation
            ':hammer:': '🔨',
            ':shield:': '🛡️',
            ':lock:': '🔒',
            ':unlock:': '🔓',
            ':key:': '🔑',
            ':ban:': '🔨',
            ':kick:': '👢',
            
            # Bot specific
            ':robot:': '🤖',
            ':gear:': '⚙️',
            ':tools:': '🛠️',
            ':wrench:': '🔧',
            ':nut_and_bolt:': '🔩',
            ':computer:': '💻',
            ':desktop:': '🖥️',
            ':mobile_phone:': '📱',
            
            # Status
            ':green_circle:': '🟢',
            ':yellow_circle:': '🟡',
            ':red_circle:': '🔴',
            ':blue_circle:': '🔵',
            ':purple_circle:': '🟣',
            ':white_circle:': '⚪',
            ':black_circle:': '⚫',
            
            # Misc
            ':crown:': '👑',
            ':gem:': '💎',
            ':money_with_wings:': '💸',
            ':dollar:': '💲',
            ':chart_with_upwards_trend:': '📈',
            ':chart_with_downwards_trend:': '📉',
            ':calendar:': '📅',
            ':clock:': '🕐',
            ':hourglass:': '⏳',
            ':stopwatch:': '⏱️',
            ':alarm_clock:': '⏰',
            ':bell:': '🔔',
            ':no_bell:': '🔕',
            ':loudspeaker:': '📢',
            ':mega:': '📣',
            ':inbox_tray:': '📥',
            ':outbox_tray:': '📤',
            ':package:': '📦',
            ':mailbox:': '📫',
            ':postbox:': '📮',
            ':newspaper:': '📰',
            ':bookmark:': '🔖',
            ':label:': '🏷️',
            ':page_with_curl:': '📃',
            ':page_facing_up:': '📄',
            ':bookmark_tabs:': '📑',
            ':bar_chart:': '📊',
            ':clipboard:': '📋',
            ':pushpin:': '📌',
            ':round_pushpin:': '📍',
            ':paperclip:': '📎',
            ':straight_ruler:': '📏',
            ':triangular_ruler:': '📐',
            ':scissors:': '✂️',
            ':card_file_box:': '🗃️',
            ':file_cabinet:': '🗄️',
            ':wastebasket:': '🗑️'
        }
    
    def replace_emojis(self, text):
        """Replace emoji placeholders with actual emojis"""
        if not text:
            return text
        
        # Replace custom emoji format <:name:id> and <a:name:id>
        text = re.sub(r'<a?:([^:]+):(\d+)>', r'<:\1:\2>', text)
        
        # Replace standard emoji placeholders
        for placeholder, emoji in self.emoji_map.items():
            text = text.replace(placeholder, emoji)
        
        return text
    
    def add_emoji(self, placeholder, emoji):
        """Add custom emoji mapping"""
        self.emoji_map[placeholder] = emoji
    
    def get_emoji(self, placeholder):
        """Get emoji by placeholder"""
        return self.emoji_map.get(placeholder, placeholder)