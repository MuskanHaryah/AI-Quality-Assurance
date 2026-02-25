# Google Gemini AI Integration Setup

## Overview

QualityMapAI now uses **Google Gemini AI** for enhanced domain detection and smarter recommendations! 🚀

### What Gemini Enhances

1. **Smarter Domain Detection**
   - AI-powered identification of software domains
   - Higher confidence in domain classification
   - Better handling of ambiguous or hybrid systems

2. **Intelligent Recommendations**
   - Context-aware suggestions based on your specific SRS
   - Domain-specific quality improvement advice
   - More actionable and detailed recommendations

3. **Quality Plan Insights**
   - AI analysis of Quality Plan documents
   - Automatic detection of strengths and gaps
   - Domain-aware testing suggestions

### Fallback Behavior

**Don't worry!** If you don't have a Gemini API key, the system automatically falls back to the original keyword-based detection. Everything will still work!

---

## How to Get Your Free Gemini API Key

### Step 1: Visit Google AI Studio

Go to: **https://aistudio.google.com/app/apikey**

### Step 2: Sign In

Sign in with your Google account (any Gmail account works).

### Step 3: Create API Key

1. Click **"Create API key"**
2. Select a Google Cloud project (or create a new one)
3. Copy the generated API key

### Step 4: Add to Your Backend

1. Navigate to the `backend/` folder
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and replace `your_gemini_api_key_here` with your actual API key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### Step 5: Restart Backend

If your backend is running, restart it:
```bash
# Stop the current backend (Ctrl+C if running in terminal)
# Then restart
python backend/app.py
```

---

## Verification

To verify Gemini is working:

1. Upload an SRS document
2. Check the logs for "Gemini detected domain" (if API is working)
3. Check for "Using keyword-based domain detection" (if falling back)

### Test Without API Key

The system will log:
```
Gemini unavailable, falling back to keyword-based detection
```

### Test With API Key

The system will log:
```
Gemini detected domain: Banking / Finance (confidence=0.85)
Gemini generated 5 AI-powered recommendations
```

---

## Free Tier Limits

Google's Gemini API free tier includes:
- **60 requests per minute**
- **Unlimited requests per day** (for `gemini-2.0-flash-exp`)
- **Generous context limits**

This is **more than enough** for a student project! 🎓

---

## Troubleshooting

### "Gemini available: False"

**Cause**: No API key found or invalid key

**Solution**:
1. Check `.env` file exists in `backend/`
2. Verify `GEMINI_API_KEY=` has your actual key (no quotes needed)
3. Restart the backend

### "ModuleNotFoundError: No module named 'google.genai'"

**Cause**: Dependencies not installed

**Solution**:
```bash
pip install -r backend/requirements.txt
```

### API Key Not Working

**Cause**: Invalid or expired key

**Solution**:
1. Go to https://aistudio.google.com/app/apikey
2. Generate a new API key
3. Update `.env` file
4. Restart backend

---

## Privacy & Security

- **Your API key is private**: Never commit `.env` to git (it's in `.gitignore`)
- **Your data is processed by Google**: Gemini API processes your SRS text for analysis
- **No data is stored**: Google doesn't store your requests for free tier
- **Alternative**: Use keyword-based detection (no external API calls)

---

## Technical Details

### Files Modified

- `backend/config.py` - Loads Gemini API key from environment
- `backend/services/gemini_service.py` - All Gemini AI logic
- `backend/services/quality_scorer.py` - Domain detection with Gemini fallback
- `backend/services/quality_plan_analyzer.py` - Enhanced QP analysis

### Gemini Model Used

- **Model**: `gemini-2.0-flash-exp`
- **Why**: Fastest, free tier, great for JSON responses
- **Alternatives**: Can be changed in `gemini_service.py`

### API Calls Made

1. **Domain Detection**: 1 call per SRS upload
2. **Recommendations**: 1 call per SRS analysis
3. **Quality Plan**: 1 call per QP upload

**Total**: ~3 API calls per full analysis cycle

---

## Need Help?

If you encounter any issues:

1. Check logs in `backend/data/app.log`
2. Verify `.env` file configuration
3. Test with Gemini disabled first (no API key)
4. Check Google AI Studio quotas

---

## Future Improvements

Possible enhancements:
- [ ] Cached responses to reduce API calls
- [ ] Custom domain training
- [ ] Multi-language SRS support
- [ ] More detailed quality scoring with Gemini

---

**Happy Testing!** 🎉
