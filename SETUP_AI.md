# 🚀 Setup Instructions for OpenAI Integration

## Backend Setup

### 1. Install OpenAI Package
```powershell
cd backend
pip install openai
```

### 2. Add OpenAI API Key

Your `.env` file already has a placeholder. Replace it with your actual OpenAI API key:

1. Visit https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and replace in `.env`:

```env
GOOGLE_API_KEY="AIzaSyDwaUj8sPKhhxv5ARfhvMe-U8_oyKxcQXA"
OPENAI_API_KEY="sk-proj-your-actual-key-here"
```

### 3. Start Backend Server
```powershell
cd backend
python app.py
```

Server will run on `http://localhost:5000`

## Frontend Setup

No additional packages needed! All components are ready to use.

### Start Frontend
```powershell
cd frontend
npm run dev
```

Frontend will run on `http://localhost:3000`

## 🎯 New AI Features

### 1. AI-Powered Insights Dashboard
- Executive summary of reviews
- Key themes identification
- Customer strengths and pain points
- Actionable recommendations
- Customer personas
- Competitive intelligence
- Trend analysis

**How to use:**
1. Search for a Dr. Martens location
2. Wait for reviews to load
3. Click "✨ Generate AI Insights" button
4. View comprehensive analysis
5. Download professional report (📥 Download Report)

### 2. AI Chat Assistant
- Floating chat button (💬) in bottom-right corner
- Ask natural language questions about reviews
- Get instant AI-powered answers
- Context-aware responses
- Chat history maintained

**Example Questions:**
- "What do customers love most about Dr. Martens?"
- "What are the main complaints?"
- "How's the customer service?"
- "What about pricing concerns?"
- "Are there any quality issues?"

## 💰 OpenAI Pricing

The app uses **GPT-4o** model for best quality:
- Input: ~$0.005 per 1K tokens
- Output: ~$0.015 per 1K tokens
- Average cost per analysis: $0.10-0.30
- Chat responses: $0.02-0.05 each

**Monthly estimates:**
- 100 analyses: ~$15-30
- 500 chat queries: ~$15-25
- Total: ~$30-55/month for moderate use

## 🔧 Troubleshooting

### Backend Issues

**"OpenAI API key not configured"**
- Check `.env` file exists in backend folder
- Verify OPENAI_API_KEY is set correctly
- Restart the backend server

**"Failed to connect to OpenAI"**
- Check your internet connection
- Verify API key is valid and has credits
- Check OpenAI service status

**Import error: No module named 'openai'**
```powershell
pip install openai
```

### Frontend Issues

**"Failed to generate insights"**
- Ensure backend is running on port 5000
- Check browser console for errors
- Verify reviews are loaded first

**Chat not responding**
- Check backend logs for errors
- Verify OpenAI API key is configured
- Ensure reviews exist before asking questions

### API Key Issues

**Invalid API key error**
- Go to https://platform.openai.com/api-keys
- Regenerate your API key
- Update `.env` file
- Restart backend

**Rate limit exceeded**
- Wait a few minutes
- Upgrade your OpenAI plan
- Reduce number of requests

**Insufficient credits**
- Add payment method at https://platform.openai.com/account/billing
- Purchase credits or set up auto-recharge

## 📊 Testing the Features

### Test AI Insights
1. Search: "Dr. Martens Camden Town London"
2. Wait for reviews to load
3. Click "Generate AI Insights"
4. View the comprehensive analysis
5. Try downloading the report

### Test Chat Assistant
1. Click the 💬 button (bottom-right)
2. Try suggested questions
3. Ask custom questions like:
   - "Summarize the positive feedback"
   - "What improvements do customers suggest?"
   - "How do customers rate the quality?"

## 🎨 Features Showcase for Demo

### For Executive Presentation:
1. **Start with Search**: Show a flagship Dr. Martens store
2. **Basic Stats**: Highlight sentiment distribution
3. **Generate AI Insights**: Show comprehensive analysis
4. **Executive Summary**: Read the high-level overview
5. **Key Themes**: Walk through identified patterns
6. **Recommendations**: Show actionable insights
7. **Download Report**: Generate professional document
8. **Chat Demo**: Ask intelligent questions live

### Key Talking Points:
- ✅ "Real-time analysis of Google reviews"
- ✅ "GPT-4 powered insights beyond basic sentiment"
- ✅ "Actionable recommendations for business improvement"
- ✅ "Customer personas for targeted marketing"
- ✅ "Competitive intelligence from customer feedback"
- ✅ "Interactive AI assistant for deep-dive analysis"
- ✅ "Professional reports ready for stakeholders"

## 🔐 Security Best Practices

1. **Never commit `.env` file**
   - Already in `.gitignore`
   - Keep API keys secret

2. **Rotate API keys regularly**
   - Monthly rotation recommended
   - Revoke old keys

3. **Monitor usage**
   - Check OpenAI dashboard regularly
   - Set up billing alerts
   - Monitor for unusual activity

4. **Use environment variables**
   - Never hardcode API keys
   - Use different keys for dev/prod

## 📝 Next Steps

After setup is complete:

1. ✅ Test basic review fetching
2. ✅ Generate your first AI insights
3. ✅ Try the chat assistant
4. ✅ Download a sample report
5. ✅ Prepare demo script
6. ✅ Practice presentation flow

## 🆘 Support

If you encounter issues:

1. Check this setup guide
2. Review error messages in terminal/console
3. Verify all environment variables are set
4. Ensure all dependencies are installed
5. Check OpenAI account status

## 🎉 You're Ready!

Once everything is set up, you'll have:
- ✨ AI-powered insights generation
- 💬 Interactive chat assistant
- 📊 Comprehensive analytics
- 📥 Professional report generation
- 🎯 Competitive intelligence
- 👥 Customer persona identification

**This will definitely impress Dr. Martens!** 🚀
