import re

class EmojiHandler:
    def __init__(self):
        self.emoji_map = {
            # Basic emojis
            ':smile:': '😊', ':grin:': '😁', ':joy:': '😂', ':heart:': '❤️', ':fire:': '🔥', ':star:': '⭐', ':thumbsup:': '👍', ':thumbsdown:': '👎', ':clap:': '👏', ':wave:': '👋',
            ':eyes:': '👀', ':thinking:': '🤔', ':shrug:': '🤷', ':facepalm:': '🤦', ':ok_hand:': '👌', ':point_right:': '👉', ':point_left:': '👈', ':point_up:': '👆', ':point_down:': '👇',
            
            # Nitro Custom Emojis (100+)
            ':dravon_check:': '<:dravon_check:1413146132405817487>', ':dravon_cross:': '<:dravon_cross:1413146132405817488>', ':dravon_loading:': '<a:dravon_loading:1413146132405817489>',
            ':dravon_arrow_right:': '<:dravon_arrow_right:1413146132405817490>', ':dravon_arrow_left:': '<:dravon_arrow_left:1413146132405817491>', ':dravon_star:': '<:dravon_star:1413146132405817492>',
            ':dravon_heart:': '<:dravon_heart:1413146132405817493>', ':dravon_fire:': '<:dravon_fire:1413146132405817494>', ':dravon_diamond:': '<:dravon_diamond:1413146132405817495>',
            ':dravon_crown:': '<:dravon_crown:1413146132405817496>', ':dravon_sparkles:': '<a:dravon_sparkles:1413146132405817497>', ':dravon_rainbow:': '<a:dravon_rainbow:1413146132405817498>',
            ':dravon_party:': '<a:dravon_party:1413146132405817499>', ':dravon_dance:': '<a:dravon_dance:1413146132405817500>', ':dravon_wave:': '<a:dravon_wave:1413146132405817501>',
            ':dravon_typing:': '<a:dravon_typing:1413146132405817502>', ':dravon_music:': '<a:dravon_music:1413146132405817503>', ':dravon_heartbeat:': '<a:dravon_heartbeat:1413146132405817504>',
            ':dravon_spinning:': '<a:dravon_spinning:1413146132405817505>', ':dravon_bounce:': '<a:dravon_bounce:1413146132405817506>', ':dravon_online:': '<:dravon_online:1413146132405817507>',
            ':dravon_offline:': '<:dravon_offline:1413146132405817508>', ':dravon_idle:': '<:dravon_idle:1413146132405817509>', ':dravon_dnd:': '<:dravon_dnd:1413146132405817510>',
            ':dravon_streaming:': '<:dravon_streaming:1413146132405817511>', ':dravon_mobile:': '<:dravon_mobile:1413146132405817512>', ':dravon_desktop:': '<:dravon_desktop:1413146132405817513>',
            ':dravon_web:': '<:dravon_web:1413146132405817514>', ':dravon_love:': '<:dravon_love:1413146132405817515>', ':dravon_angry:': '<:dravon_angry:1413146132405817516>',
            ':dravon_sad:': '<:dravon_sad:1413146132405817517>', ':dravon_happy:': '<:dravon_happy:1413146132405817518>', ':dravon_laugh:': '<:dravon_laugh:1413146132405817519>',
            ':dravon_cry:': '<:dravon_cry:1413146132405817520>', ':dravon_shocked:': '<:dravon_shocked:1413146132405817521>', ':dravon_confused:': '<:dravon_confused:1413146132405817522>',
            ':dravon_thinking:': '<:dravon_thinking:1413146132405817523>', ':dravon_cool:': '<:dravon_cool:1413146132405817524>', ':dravon_controller:': '<:dravon_controller:1413146132405817525>',
            ':dravon_keyboard:': '<:dravon_keyboard:1413146132405817526>', ':dravon_mouse:': '<:dravon_mouse:1413146132405817527>', ':dravon_headset:': '<:dravon_headset:1413146132405817528>',
            ':dravon_trophy:': '<:dravon_trophy:1413146132405817529>', ':dravon_medal:': '<:dravon_medal:1413146132405817530>', ':dravon_winner:': '<:dravon_winner:1413146132405817531>',
            ':dravon_gamer:': '<:dravon_gamer:1413146132405817532>', ':dravon_discord:': '<:dravon_discord:1413146132405817533>', ':dravon_nitro:': '<:dravon_nitro:1413146132405817534>',
            ':dravon_boost:': '<:dravon_boost:1413146132405817535>', ':dravon_partner:': '<:dravon_partner:1413146132405817536>', ':dravon_verified:': '<:dravon_verified:1413146132405817537>',
            ':dravon_staff:': '<:dravon_staff:1413146132405817538>', ':dravon_hypesquad:': '<:dravon_hypesquad:1413146132405817539>', ':dravon_bughunter:': '<:dravon_bughunter:1413146132405817540>',
            ':dravon_developer:': '<:dravon_developer:1413146132405817541>', ':dravon_supporter:': '<:dravon_supporter:1413146132405817542>', ':dravon_settings:': '<:dravon_settings:1413146132405817543>',
            ':dravon_tools:': '<:dravon_tools:1413146132405817544>', ':dravon_search:': '<:dravon_search:1413146132405817545>', ':dravon_info:': '<:dravon_info:1413146132405817546>',
            ':dravon_warning:': '<:dravon_warning:1413146132405817547>', ':dravon_error:': '<:dravon_error:1413146132405817548>', ':dravon_success:': '<:dravon_success:1413146132405817549>',
            ':dravon_pending:': '<:dravon_pending:1413146132405817550>', ':dravon_lock:': '<:dravon_lock:1413146132405817551>', ':dravon_unlock:': '<:dravon_unlock:1413146132405817552>',
            ':dravon_like:': '<:dravon_like:1413146132405817553>', ':dravon_dislike:': '<:dravon_dislike:1413146132405817554>', ':dravon_share:': '<:dravon_share:1413146132405817555>',
            ':dravon_comment:': '<:dravon_comment:1413146132405817556>', ':dravon_follow:': '<:dravon_follow:1413146132405817557>', ':dravon_unfollow:': '<:dravon_unfollow:1413146132405817558>',
            ':dravon_subscribe:': '<:dravon_subscribe:1413146132405817559>', ':dravon_notification:': '<:dravon_notification:1413146132405817560>', ':dravon_sunny:': '<:dravon_sunny:1413146132405817561>',
            ':dravon_cloudy:': '<:dravon_cloudy:1413146132405817562>', ':dravon_rainy:': '<:dravon_rainy:1413146132405817563>', ':dravon_snowy:': '<:dravon_snowy:1413146132405817564>',
            ':dravon_stormy:': '<:dravon_stormy:1413146132405817565>', ':dravon_windy:': '<:dravon_windy:1413146132405817566>', ':dravon_foggy:': '<:dravon_foggy:1413146132405817567>',
            ':dravon_hot:': '<:dravon_hot:1413146132405817568>', ':dravon_cold:': '<:dravon_cold:1413146132405817569>', ':dravon_pizza:': '<:dravon_pizza:1413146132405817570>',
            ':dravon_burger:': '<:dravon_burger:1413146132405817571>', ':dravon_coffee:': '<:dravon_coffee:1413146132405817572>', ':dravon_tea:': '<:dravon_tea:1413146132405817573>',
            ':dravon_cake:': '<:dravon_cake:1413146132405817574>', ':dravon_cookie:': '<:dravon_cookie:1413146132405817575>', ':dravon_donut:': '<:dravon_donut:1413146132405817576>',
            ':dravon_icecream:': '<:dravon_icecream:1413146132405817577>', ':dravon_apple:': '<:dravon_apple:1413146132405817578>', ':dravon_banana:': '<:dravon_banana:1413146132405817579>',
            ':dravon_cat:': '<:dravon_cat:1413146132405817580>', ':dravon_dog:': '<:dravon_dog:1413146132405817581>', ':dravon_fox:': '<:dravon_fox:1413146132405817582>',
            ':dravon_wolf:': '<:dravon_wolf:1413146132405817583>', ':dravon_bear:': '<:dravon_bear:1413146132405817584>', ':dravon_panda:': '<:dravon_panda:1413146132405817585>',
            ':dravon_lion:': '<:dravon_lion:1413146132405817586>', ':dravon_tiger:': '<:dravon_tiger:1413146132405817587>', ':dravon_rabbit:': '<:dravon_rabbit:1413146132405817588>',
            ':dravon_car:': '<:dravon_car:1413146132405817590>', ':dravon_bus:': '<:dravon_bus:1413146132405817591>', ':dravon_train:': '<:dravon_train:1413146132405817592>',
            ':dravon_plane:': '<:dravon_plane:1413146132405817593>', ':dravon_rocket:': '<:dravon_rocket:1413146132405817594>', ':dravon_bike:': '<:dravon_bike:1413146132405817595>',
            ':dravon_boat:': '<:dravon_boat:1413146132405817596>', ':dravon_helicopter:': '<:dravon_helicopter:1413146132405817597>', ':dravon_computer:': '<:dravon_computer:1413146132405817598>',
            ':dravon_phone:': '<:dravon_phone:1413146132405817599>', ':dravon_tablet:': '<:dravon_tablet:1413146132405817600>', ':dravon_camera:': '<:dravon_camera:1413146132405817601>',
            ':dravon_microphone:': '<:dravon_microphone:1413146132405817602>', ':dravon_speaker:': '<:dravon_speaker:1413146132405817603>', ':dravon_battery:': '<:dravon_battery:1413146132405817604>',
            ':dravon_wifi:': '<:dravon_wifi:1413146132405817605>', ':dravon_bluetooth:': '<:dravon_bluetooth:1413146132405817606>', ':dravon_usb:': '<:dravon_usb:1413146132405817607>',
            
            # Discord/Gaming emojis
            ':discord:': '<:discord:314003252830011395>', ':online:': '<:online:313956277808005120>', ':idle:': '<:idle:313956277220802560>', ':dnd:': '<:dnd:313956276893646850>',
            ':offline:': '<:offline:313956277237710868>', ':streaming:': '<:streaming:313956277132853248>',
            
            # Utility emojis
            ':check:': '✅', ':x:': '❌', ':warning:': '⚠️', ':info:': 'ℹ️', ':question:': '❓', ':exclamation:': '❗', ':white_check_mark:': '✅',
            ':negative_squared_cross_mark:': '❎', ':heavy_check_mark:': '✔️', ':heavy_multiplication_x:': '✖️',
            
            # Numbers
            ':one:': '1️⃣', ':two:': '2️⃣', ':three:': '3️⃣', ':four:': '4️⃣', ':five:': '5️⃣', ':six:': '6️⃣', ':seven:': '7️⃣', ':eight:': '8️⃣', ':nine:': '9️⃣', ':ten:': '🔟',
            
            # Arrows
            ':arrow_up:': '⬆️', ':arrow_down:': '⬇️', ':arrow_left:': '⬅️', ':arrow_right:': '➡️', ':arrow_up_small:': '🔼', ':arrow_down_small:': '🔽',
            
            # Music
            ':musical_note:': '🎵', ':notes:': '🎶', ':microphone:': '🎤', ':headphones:': '🎧', ':speaker:': '🔊', ':mute:': '🔇', ':loud_sound:': '🔊',
            
            # Moderation
            ':hammer:': '🔨', ':shield:': '🛡️', ':lock:': '🔒', ':unlock:': '🔓', ':key:': '🔑', ':ban:': '🔨', ':kick:': '👢',
            
            # Bot specific
            ':robot:': '🤖', ':gear:': '⚙️', ':tools:': '🛠️', ':wrench:': '🔧', ':nut_and_bolt:': '🔩', ':computer:': '💻', ':desktop:': '🖥️', ':mobile_phone:': '📱',
            
            # Status
            ':green_circle:': '🟢', ':yellow_circle:': '🟡', ':red_circle:': '🔴', ':blue_circle:': '🔵', ':purple_circle:': '🟣', ':white_circle:': '⚪', ':black_circle:': '⚫',
            
            # Misc
            ':crown:': '👑', ':gem:': '💎', ':money_with_wings:': '💸', ':dollar:': '💲', ':chart_with_upwards_trend:': '📈', ':chart_with_downwards_trend:': '📉',
            ':calendar:': '📅', ':clock:': '🕐', ':hourglass:': '⏳', ':stopwatch:': '⏱️', ':alarm_clock:': '⏰', ':bell:': '🔔', ':no_bell:': '🔕',
            ':loudspeaker:': '📢', ':mega:': '📣', ':inbox_tray:': '📥', ':outbox_tray:': '📤', ':package:': '📦', ':mailbox:': '📫', ':postbox:': '📮',
            ':newspaper:': '📰', ':bookmark:': '🔖', ':label:': '🏷️', ':page_with_curl:': '📃', ':page_facing_up:': '📄', ':bookmark_tabs:': '📑',
            ':bar_chart:': '📊', ':clipboard:': '📋', ':pushpin:': '📌', ':round_pushpin:': '📍', ':paperclip:': '📎', ':straight_ruler:': '📏',
            ':triangular_ruler:': '📐', ':scissors:': '✂️', ':card_file_box:': '🗃️', ':file_cabinet:': '🗄️', ':wastebasket:': '🗑️'
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