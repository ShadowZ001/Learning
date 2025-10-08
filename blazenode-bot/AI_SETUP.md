# AI Command Setup

## Overview
The `/ai` command provides intelligent AI responses using Google's Gemini 1.5 Flash model.

## Features
- 🤖 **Smart AI Responses**: Uses Gemini 1.5 Flash (free model)
- 📍 **Channel-specific**: AI only responds in selected channel
- ⚙️ **Easy Configuration**: Dropdown menu interface
- 🔄 **Toggle Control**: Enable/disable AI responses
- 📊 **Status Monitoring**: Check AI configuration and status

## Usage

### Setup Commands
```
>ai        (prefix command)
/ai        (slash command)
>setup     (alternative prefix)
>aisetup   (alias)
>ai-setup  (alias)
```

### Configuration Options
1. **Select Channel**: Set which channel AI responds in
2. **AI Config**: View current configuration
3. **AI Status**: Check if AI is online/offline
4. **AI Enable/Disable**: Toggle AI responses

### How It Works
1. Admin runs `>ai` command
2. Selects "Select Channel" from dropdown
3. Mentions the target channel (e.g., #ai-chat)
4. Enables AI using "AI Enable/Disable"
5. AI will now respond to all messages in that channel

## Technical Details
- **Model**: Gemini 1.5 Flash (gemini-1.5-flash)
- **Provider**: Google AI
- **API Key**: Requires Google AI Studio API key (free tier)
- **Response Limit**: 500 tokens per response
- **Auto-splitting**: Long responses are split into multiple messages

## Admin Only
This command is restricted to server administrators only.