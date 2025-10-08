# Gemini API Setup Guide

## Get Your Free Gemini API Key

1. **Visit Google AI Studio**
   - Go to [https://aistudio.google.com/](https://aistudio.google.com/)
   - Sign in with your Google account

2. **Create API Key**
   - Click "Get API key" in the left sidebar
   - Click "Create API key"
   - Select "Create API key in new project" or choose existing project
   - Copy your API key

3. **Add to Environment**
   - Open your `.env` file
   - Replace `your_gemini_api_key_here` with your actual API key:
   ```
   GEMINI_API_KEY=AIzaSyC-your-actual-api-key-here
   ```

4. **Test the Setup**
   - Restart your bot: `npm start`
   - Use `>ai` command to configure AI channel
   - Send a message in the configured channel

## Free Tier Limits
- **15 requests per minute**
- **1 million tokens per day**
- **1,500 requests per day**

## Troubleshooting
- **401 Error**: Check your API key is correct
- **403 Error**: API key might be restricted
- **429 Error**: Rate limit exceeded, wait a minute

## Model Information
- **Model**: gemini-1.5-flash
- **Max tokens**: 500 per response
- **Temperature**: 0.7 (balanced creativity)