# N8N API Setup for Oatis 🤖

## 📋 What You Need (Copy These):

| What | Value | Where to Use |
|------|-------|--------------|
| **API URL** | `https://api.kendall-max.org/v1` | Base URL field |
| **API Key** | `sk-oatisawesome-2024-ml-api` | API Key field |
| **Backup Key** | `sk-0at!sAw3s0m3-2024-ml-v2` | If primary fails |
| **Model** | `llama3.1:8b` | Model field |

---

## 🚀 Quick Start: 3-Step Setup

### Step 1: Add OpenAI Node to Your Workflow

1. Open your N8N workflow (or create a new one)
2. Click the **"+"** button where you want to add AI
3. In the search box, type: `OpenAI`
4. Click on **"OpenAI"** node (the official one with OpenAI logo)

✅ **You now have an OpenAI node in your workflow!**

---

### Step 2: Configure API Credentials (ONE TIME ONLY)

**This connects you to Kendall's AI instead of OpenAI:**

1. Click on the **OpenAI node** you just added
2. Look for the **"Credential to connect with"** dropdown
3. Click it and select **"Create New Credential"**
4. You'll see a form with these fields:

#### Fill in EXACTLY like this:

| Field Name | What to Enter | Copy This |
|------------|---------------|-----------|
| **API Key** | Kendall's API key | `sk-oatisawesome-2024-ml-api` |
| **Base URL** | Kendall's server | `https://api.kendall-max.org/v1` |

5. **IMPORTANT:** Click the **"Save"** button at the bottom
6. Give your credential a name like: `Kendall's AI`

✅ **Credentials saved! You'll never need to do this again!**

---

### Step 3: Use It in Your Workflow

**Every time you use the OpenAI node:**

1. **Select your credential:**
   - In the "Credential to connect with" dropdown
   - Choose **"Kendall's AI"** (the one you just created)

2. **Select the model:**
   - Look for the **"Model"** dropdown
   - Type or select: `llama3.1:8b`

3. **Enter YOUR prompt:**
   - Find the big text box labeled **"Prompt"** or **"Text"**
   - **THIS IS WHERE YOU TYPE WHAT YOU WANT THE AI TO DO!**

   **Examples:**
   ```
   Summarize this customer email in 2 sentences
   ```
   ```
   Write a professional response to: {{$json.customer_message}}
   ```
   ```
   Analyze this data and tell me the top 3 insights
   ```
   ```
   Translate this to Spanish: {{$json.english_text}}
   ```
   ```
   Is this email urgent, normal, or spam? Reply with one word.
   ```

4. Click **"Execute Node"** to test it!

✅ **That's it! The AI will respond to whatever you typed!**

---

## 💡 Where Do I Type My Prompts?

### Visual Guide:

```
┌────────────────────────────────────────┐
│   OpenAI Node                          │
├────────────────────────────────────────┤
│                                        │
│  Credential: Kendall's AI ✅           │
│  Model: llama3.1:8b ✅                 │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ Prompt: (THIS IS WHERE!)         │ │ ⬅️ TYPE HERE!
│  │                                  │ │
│  │ Write a haiku about coffee       │ │
│  │                                  │ │
│  └──────────────────────────────────┘ │
│                                        │
│  [Execute Node]                        │
└────────────────────────────────────────┘
```

### The Prompt Field is YOUR Command to the AI:

- ✅ Type **ANY question** you want answered
- ✅ Type **ANY instruction** for the AI to follow
- ✅ Use **N8N variables** like `{{$json.email}}` to pass data
- ✅ Be **specific** - the more detail, the better the result!

**YOU control what the AI does. The prompt is 100% yours!**

---

## 🎯 Real-World Examples:

### Example 1: Email Summarizer

**Your Prompt:**
```
Summarize this email in one sentence: {{$json.emailBody}}
```

**AI Response:**
```
Customer is requesting a refund for order #12345 due to delayed shipping.
```

---

### Example 2: Customer Service Assistant

**Your Prompt:**
```
Write a professional, empathetic response to this customer complaint:

{{$json.complaint}}

Keep it under 100 words and offer a solution.
```

**AI Response:**
```
Dear valued customer,

I sincerely apologize for the inconvenience you've experienced...
[Full professional response]
```

---

### Example 3: Data Classifier

**Your Prompt:**
```
Classify this support ticket as: BUG, FEATURE_REQUEST, or QUESTION

Ticket: {{$json.ticket_text}}

Reply with just one word.
```

**AI Response:**
```
BUG
```

---

## 🔥 Pro Tips:

✅ **Use the same credential everywhere** - create it once, use it in all workflows
✅ **The prompt field accepts N8N expressions** - use `{{$json.data}}` to insert dynamic content
✅ **Test with "Execute Node" button** before activating your workflow
✅ **Change your prompt anytime** - it's not locked in!
✅ **No limits** - ask as many questions as you want, any time!

---

## ❓ Troubleshooting:

### "Invalid API Key" error:
- ✅ Check you entered: `sk-oatisawesome-2024-ml-api` (copy exactly)
- ✅ Check Base URL is: `https://api.kendall-max.org/v1` (include /v1)

### "Model not found" error:
- ✅ Model name must be exactly: `llama3.1:8b` (lowercase, with colon)

### No response:
- ✅ Make sure Kendall's server is running
- ✅ Check you clicked "Execute Node" button
- ✅ Look at the output panel on the right side

### Slow responses:
- ✅ Normal! AI generates 96-100 words per second
- ✅ Longer prompts = longer processing time

---

## 🎁 What You Get:

✅ **32,768 tokens per request** (8x bigger than ChatGPT!)
✅ **96-100 tokens/second speed** (super fast on M4 Max)
✅ **Unlimited requests** (no rate limits)
✅ **Same API as ChatGPT** (drop-in replacement)
✅ **Works with all N8N features** (variables, expressions, etc.)

**Type whatever you want in the Prompt field - the AI is yours to use!**

---

## 🔧 Advanced Option: HTTP Request Node

**Only use this if you can't use the OpenAI node. The OpenAI node is MUCH easier!**

### Step-by-Step HTTP Setup:

1. **Add HTTP Request node** to your workflow
2. Click on it and configure these fields:

| Field | Value |
|-------|-------|
| **Method** | `POST` |
| **URL** | `https://api.kendall-max.org/v1/chat/completions` |
| **Authentication** | `Header Auth` |
| **Header Name** | `Authorization` |
| **Header Value** | `Bearer sk-oatisawesome-2024-ml-api` |
| **Body Content Type** | `JSON` |

3. **Body (JSON):**
   ```json
   {
     "model": "llama3.1:8b",
     "messages": [
       {"role": "user", "content": "YOUR PROMPT GOES HERE"}
     ]
   }
   ```

4. **Replace `"YOUR PROMPT GOES HERE"`** with your actual question:
   ```json
   {
     "model": "llama3.1:8b",
     "messages": [
       {"role": "user", "content": "Summarize this email: {{$json.email}}"}
     ]
   }
   ```

5. Click **"Execute Node"** to test!

**Response will be in:** `{{$json.choices[0].message.content}}`

---

## 🧪 Test It From Command Line:

Want to test if the API is working? Run this in Terminal:

```bash
curl -X POST https://api.kendall-max.org/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Say hello!"}]
  }'
```

---

## 📞 Need Help?

**Contact Kendall** if you run into any issues!

**Common issues:**
- Forgot to add `/v1` to the end of the URL
- Typo in API key (copy-paste it!)
- Model name wrong (must be `llama3.1:8b` exactly)

---

## 🎉 You're All Set!

**Remember:** The prompt is whatever YOU want to ask the AI. There are no limits, no restrictions - just type your question and go!
